import logging
from http import HTTPStatus
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from flask import Blueprint, current_app, request
from flask_cors import CORS, cross_origin
from flasgger import swag_from
# from requests.auth import HTTPBasicAuth
# from app_server.http_functions import get_auth_server_login, get_auth_server_register
import google.auth.transport.requests
import google.oauth2.id_token
from auth_server.db_functions import *
from auth_server.token_functions import *
from auth_server.validation_functions import *
import auth_server.body_parser as body_parser
from auth_server.persistence.user_persistence import UserPersistence
from auth_server.exceptions.user_already_registered_exception import UserAlreadyRegisteredException
from auth_server.exceptions.user_not_found_exception import UserNotFoundException
from auth_server.model.user import User
from auth_server.decorators.admin_user_required_decorator import admin_user_required
from auth_server.decorators.app_server_token_required_decorator import app_server_token_required

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
HTTP_REQUEST = google.auth.transport.requests.Request()


authentication_bp = Blueprint('authentication', __name__)
CORS(authentication_bp)
logger = logging.getLogger('gunicorn.error')

# TODO: puede ser variable de entorno
cred = credentials.Certificate('chotuve-android-app-firebase-adminsdk-2ry62-ab27b1a04b.json')
firebase_app = firebase_admin.initialize_app(cred)

### Register methods ###

@authentication_bp.route('/api/register/', methods=['POST'])
@app_server_token_required
@swag_from('docs/register.yml')
def _register_user():
	try:
		data = request.json
		user = body_parser.parse_regular_user(data)
		user_persistence = UserPersistence(current_app.db)
		user_persistence.save(user)
		result = {'Registration': 'Successfully registered new user with email {0}'.format(user.email)}
		logger.debug('User was inserted')
		return result, HTTPStatus.CREATED
	except UserAlreadyRegisteredException:
		logger.error('This user already exists!')
		result = {'Registration': 'This user already exists!'}
		return result, HTTPStatus.CONFLICT


@authentication_bp.route('/api/register_with_firebase/', methods=['POST'])
@app_server_token_required
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
@admin_user_required
@cross_origin(allow_headers=['Content-Type'])
@swag_from('docs/register_admin_user.yml')
def _register_admin_user():

	data = request.json
	with current_app.app_context():
		result, status_code = insert_admin_user_into_users_db(current_app.client, data)

	return result, status_code


### Login methods ###

@authentication_bp.route('/api/login/', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
@swag_from('docs/login.yml')
def _login_user():
	data = request.json
	logger.debug(data['email'])
	with current_app.app_context():
		result, status_code, user = get_user(current_app.client, data['email'])
		if status_code == 200:
			if validar_usuario(user, data['password']):
				logger.debug('Usuario logueado con exito')
				user_persistence = UserPersistence(current_app.db)
				user_found = user_persistence.get_user_by_email(data['email'])
				token = generate_auth_token(user_found)
				logger.debug('This is the token {0}'.format(token))
				result = {'Token': token}
			else:
				logger.debug('Incorrect user or password')
				result = {'Login': 'invalid user or password'}
				status_code = 401
	return result, status_code

@authentication_bp.route('/api/login_with_firebase/', methods=['POST'])
@app_server_token_required
@swag_from('docs/login_with_firebase.yml')
def _login_user_using_firebase():
	try:
		id_token = request.headers.get('authorization', None)
		claims = firebase_admin.auth.verify_id_token(id_token)
		if not claims or not claims.get('email'):
			logger.debug('Response from auth server login is 401')
			result = {'Login': 'invalid firebase token'}
			status_code = 401
			return result, status_code

		user_persistence = UserPersistence(current_app.db)
		user = None
		try:
			user = user_persistence.get_user_by_email(claims.get('email'))
		except UserNotFoundException:
			user = User(claims.get('email'), None, claims.get('name'), 'NULL',
							claims.get('picture'), True, False, False)
			user_persistence.save(user)

		if user.is_blocked_user():
			logger.debug('This user is BLOCKED')
			result = {'Login': 'user not registered with Firebase'}
			status_code = 401
		elif user.is_firebase_user():
			logger.debug('Usuario logueado con exito')
			token = generate_auth_token(user)
			logger.debug('This is the token {0}'.format(token))
			result = {'Token': token, 'claims': claims}
			status_code = HTTPStatus.OK
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
