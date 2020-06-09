import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from flask import Blueprint, current_app, request
from flasgger import swag_from
# from requests.auth import HTTPBasicAuth
# from app_server.http_functions import get_auth_server_login, get_auth_server_register
import google.auth.transport.requests
import google.oauth2.id_token
from auth_server.db_functions import *
from auth_server.token_functions import *
from auth_server.validation_functions import *




# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
HTTP_REQUEST = google.auth.transport.requests.Request()


authentication_bp = Blueprint('authentication', __name__)
logger = logging.getLogger('gunicorn.error')

# TODO: puede ser variable de entorno
cred = credentials.Certificate('chotuve-android-app-firebase-adminsdk-2ry62-ab27b1a04b.json')
firebase_app = firebase_admin.initialize_app(cred)

### Register methods ###

@authentication_bp.route('/api/register/', methods=['POST'])
@swag_from('docs/register.yml')
def _register_user():
	data = request.json

	with current_app.app_context():
		result, status_code = insert_local_user_into_users_db(current_app.client, data)
	logger.debug('User was inserted')
	return result, status_code


@authentication_bp.route('/api/register_with_firebase/', methods=['POST'])
@swag_from('docs/register_with_firebase.yml')
def _register_user_using_firebase():
	try:
		id_token = request.headers.get('authorization', None)
		# En claims se almacena mas informacion de usuario como mail, y datos personales
		claims = firebase_admin.auth.verify_id_token(id_token)
		#Si firebase no reconoce el token
		if not claims:
			logger.debug('Token incorrecto')
			result = {'Register': 'invalid firebase token'}
			status_code = 401
		else:
			logger.debug('Valid token')
			result = {'Register': 'valid firebase token'}
			status_code = 200
			with current_app.app_context():
				result, status_code = insert_firebase_user_into_users_db(current_app.client, claims)
		return result, status_code
	except ValueError as exc:
		result = {'Register': 'Error'}
		status_code = 401
		logger.error(exc)
		return result, status_code
	except firebase_admin._auth_utils.InvalidIdTokenError as invalid_token_error:
		result = {'Register': 'invalid token'}
		status_code = 401
		logger.error(invalid_token_error)
		return result, status_code

@authentication_bp.route('/api/register_admin_user/', methods=['POST'])
@swag_from('docs/register_admin_user.yml')
def _register_admin_user():

	id_token = request.headers.get('authorization', None)
	result, status_code = validate_token(id_token)

	if status_code == 200:
		logger.debug('Valid token')
		user_email = get_user_with_token(id_token)
		if user_email != 'invalid token':
			with current_app.app_context():
				result, status_code, user = get_user(current_app.client, user_email)

			if validate_admin_user(user):
				logger.debug('Token is from admin user')
				data = request.json
				with current_app.app_context():
					result, status_code = insert_admin_user_into_users_db(current_app.client, data)
			else:
				result, status_code = {'Error':'this user is not admin'}, 401
		else:
			result, status_code = {'Message':'invalid token'}, 401

	return result, status_code

## La realidad es que no importa la red social lo que verificamos es el token de firebase.
## Por ahora lo dejo por si se me esta pasando algo, pero eventualmente vamos a borrar este endpoint

# @authentication_bp.route('/api/register_with_google/', methods=['POST'])
# @swag_from('docs/register_with_google.yml')
# def _register_user_using_google():
# 	try:
# 		id_token = get_token_id_from_request()
# 		# En claims se almacena mas informacion de usuario como mail, y datos personales
# 		claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
# 		#Si firebase no reconoce el token
# 		if not claims:
# 			logger.debug('Token incorrecto')
# 			result = {'Register': 'invalid firebase token'}
# 			status_code = 401
# 		else:
# 			#TODO: insert into users db no esta preparada para recibir claims.
# 			#TODO: hacer funcion previa que prepara la data.
# 			logger.debug('Valid token')
# 			result = {'Register': 'valid firebase token'}
# 			status_code = 200
# 			# with current_app.app_context():
# 			# 	result, status_code = insert_into_users_db(current_app.client, claims)
# 			# logger.debug('User was inserted')
# 		return result, status_code
# 	except ValueError as exc:
# 		result = {'Register': 'Error'}
# 		status_code = 401
# 		logger.error(exc)
# 		return result, status_code

### Login methods ###

@authentication_bp.route('/api/login/', methods=['POST'])
@swag_from('docs/login.yml')
def _login_user():
	data = request.json
	logger.debug(data['email'])
	with current_app.app_context():
		result, status_code, user = get_user(current_app.client, data['email'])
		if status_code == 200:
			if validar_usuario(user, data['password']):
				logger.debug('Usuario logueado con exito')
				token = generate_auth_token(data['email'])
				logger.debug('This is the token {0}'.format(token))
				result = {'Token': token}
			else:
				logger.debug('La password es incorrecta')
				result = {'Login': 'invalid password'}
				status_code = 401
	return result, status_code
	# para cuando nos llegue la request desde Androide
	# user_request = request.headers['AuthenticationHeader']
	# auth = HTTPBasicAuth('taller', 'notanseguro')
	# auth_login = '/api/login/'
	# response_auth_server = get_auth_server_login(os.environ.get('AUTH_SERVER_URL') +
	# 											 auth_login, auth)
	# if response_auth_server.status_code == 200:
	# 	# app.logger.debug('Response from auth server login is 200')
	# 	response = {'Successful login'}
	# 	response.status_code = 200
	# else:
	# 	# app.logger.debug('Response from auth server login is {0}'.
	# 	#                  format(response_auth_server.status_code))
	# 	response = {'Login failed'}
	# 	response.status_code = 401
	# current_app.logger.debug('Login was successful since it does anything at all')
	# return {'Login': 'was successful'}

@authentication_bp.route('/api/login_with_firebase/', methods=['POST'])
@swag_from('docs/login_with_firebase.yml')
def _login_user_using_firebase():
	try:
		id_token = request.headers.get('authorization', None)
		claims = firebase_admin.auth.verify_id_token(id_token)
		if not claims:
			logger.debug('Response from auth server login is 401')
			result = {'Login': 'invalid firebase token'}
			status_code = 401
		else:
			with current_app.app_context():
				result, status_code, user = get_user(current_app.client, claims.get('email'))
				if status_code == 200:
					if validate_firebase_user(user):
						logger.debug('Usuario logueado con exito')
						token = generate_auth_token(claims.get('email'))
						logger.debug('This is the token {0}'.format(token))
						result = {'Token': token}
					else:
						logger.debug('User not registered with Firebase')
						result = {'Login': 'user not registered with Firebase'}
						status_code = 401
		return result, status_code
	except ValueError as exc:
		result = {'Login': 'Error'}
		status_code = 401
		logger.error(exc)
		return result, status_code
	except firebase_admin._auth_utils.InvalidIdTokenError as invalid_token_error:
		result = {'Register': str(invalid_token_error)}
		status_code = 401
		logger.error(invalid_token_error)
		return result, status_code

## Misma historia que mas arriba.
## El login de firebase seria general, no necesitamos determinar la red social.

# @authentication_bp.route('/api/login_with_google/', methods=['GET'])
# @swag_from('docs/login_with_google.yml')
# def _login_user_using_google():
# 	try:
# 		id_token = get_token_id_from_request()
# 		# En claims se almacena mas informacion de usuario como mail, y datos personales
# 		claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
# 		#Si google no reconoce el token
# 		if not claims:
# 			logger.debug('Token incorrecto')
# 			result = {'Login': 'invalid firebase token'}
# 			status_code = 401
# 		else:
# 			result, status_code, user = get_user(current_app.client, claims.get('email'))
# 			logger.debug('Usuario logueado con exito via Google')
# 			token = generate_auth_token(claims)
# 			logger.debug('This is the token {0}'.format(token))
# 			result = {'Token': token}
# 			status_code = 200
# 		return result, status_code
# 	except ValueError as exc:
# 		result = {'Login': 'Error'}
# 		status_code = 401
# 		logger.error(exc)
# 		return result, status_code


### Validating token methods ####

@authentication_bp.route('/api/validate_token/', methods=['GET'])
@swag_from('docs/validate_token.yml')
def _validate_token():
	jwt_token = request.headers.get('authorization', None)
	result, status_code = validate_token(jwt_token)
	return result, status_code


#### Updating methods ###

@authentication_bp.route('/api/forgot_password/', methods=['GET'])
@swag_from('docs/forgot_password.yml')
def _forgot_password():
	return {}

@authentication_bp.route('/api/reset_password/', methods=['GET'])
@swag_from('docs/reset_password.yml')
def _reset_password():
	return {}
