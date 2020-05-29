# import os
import logging
import hashlib
import firebase_admin
from firebase_admin import credentials
from flask import Blueprint, current_app, request
from flasgger import swag_from
# from requests.auth import HTTPBasicAuth
# from app_server.http_functions import get_auth_server_login, get_auth_server_register
from auth_server.db_functions import *
from auth_server.token_functions import *

authentication_bp = Blueprint('authentication', __name__)
logger = logging.getLogger('gunicorn.error')

# TODO: puede ser variable de entorno
cred = credentials.Certificate('chotuve-android-app-firebase-adminsdk-2ry62-ab27b1a04b.json')
firebase_app = firebase_admin.initialize_app(cred)

def validar_usuario(user, password):
	hashed = user[5]
	salt = user[6]
	for i in range(256):
		pimienta = chr(i)
		if hashlib.sha512((password+salt+pimienta).encode('utf-8')).hexdigest() == hashed:
			return True
	return False

### Register methods ###

@authentication_bp.route('/api/register/', methods=['POST'])
@swag_from('docs/register.yml')
def _register_user():
	data = request.json

	with current_app.app_context():
		result, status_code = insert_into_users_db(current_app.client, data)

	return result, status_code

@authentication_bp.route('/api/register_with_facebook/', methods=['POST'])
@swag_from('docs/register_with_facebook.yml')
def _register_user_using_facebook():
	return {}

@authentication_bp.route('/api/register_with_google/', methods=['POST'])
@swag_from('docs/register_with_google.yml')
def _register_user_using_google():
	return {}

### Login methods ###

@authentication_bp.route('/api/login/', methods=['POST'])  # esto está conceptualmente bien?
@swag_from('docs/login.yml')
def _login_user():
	data = request.json
	logger.debug(data['email'])
	with current_app.app_context():
		result, status_code, user = get_user(current_app.client, data['email'])
		if status_code == 200:
			if validar_usuario(user, data['password']):
				logger.debug('Usuario logueado con exito')
				token = generate_auth_token(data)
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

@authentication_bp.route('/api/login_with_facebook/', methods=['GET'])
@swag_from('docs/login_with_facebook.yml')
def _login_user_using_facebook():
	return {}

@authentication_bp.route('/api/login_with_google/', methods=['GET'])
@swag_from('docs/login_with_google.yml')
def _login_user_using_google():
	return {}

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
