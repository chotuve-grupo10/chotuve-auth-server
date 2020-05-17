# import os
import logging
import firebase_admin
from firebase_admin import credentials
from flask import Blueprint, current_app
from flasgger import swag_from
# from requests.auth import HTTPBasicAuth
# from app_server.http_functions import get_auth_server_login, get_auth_server_register
from auth_server.db_functions import insert_into_users_db

authentication_bp = Blueprint('authentication', __name__)
logger = logging.getLogger('gunicorn.error')

# TODO: puede ser variable de entorno
cred = credentials.Certificate('chotuve-android-app-firebase-adminsdk-2ry62-ab27b1a04b.json')
firebase_app = firebase_admin.initialize_app(cred)

### Register methods ###

@authentication_bp.route('/api/register/', methods=['POST'])
@swag_from('docs/register.yml')
def _register_user():

	body = {'name': 'usuario',
			'last_name': 'primero',
			'email': 'primerusuario@aol.com',
			'phone_number': '47777777',
			'profile_pic': 'photocongatitos01.png'}

	with current_app.app_context():
		# TODO have something returned?
		insert_into_users_db(current_app.client, body)
	logger.debug('First user was inserted')
	return {'Result': 'Registration was successfull'}

	# if response_auth_server.status_code == 200:
	# 	app.logger.debug('Response from auth server register is 200')
	# 	response = {'Successful registragion'}
	# 	response.status_code = 200
	# else:
	# 	app.logger.debug('Response from auth server register is {0}'.
	# 					 format(response_auth_server.status_code))
	# 	response = {'Registration process failed'}
	# 	response.status_code = 401

@authentication_bp.route('/api/register_with_facebook/', methods=['POST'])
@swag_from('docs/register_with_facebook.yml')
def _register_user_using_facebook():
	return {}

@authentication_bp.route('/api/register_with_google/', methods=['POST'])
@swag_from('docs/register_with_google.yml')
def _register_user_using_google():
	return {}

### Login methods ###

@authentication_bp.route('/api/login/', methods=['GET'])  # esto está conceptualmente bien?
@swag_from('docs/login.yml')
def _login_user():
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
	current_app.logger.debug('Login was successful since it does anything at all')
	return {'Login': 'was successful'}

@authentication_bp.route('/api/login_with_facebook/', methods=['GET'])
@swag_from('docs/login_with_facebook.yml')
def _login_user_using_facebook():
	return {}

@authentication_bp.route('/api/login_with_google/', methods=['GET'])
@swag_from('docs/login_with_google.yml')
def _login_user_using_google():
	return {}

#### Updating methods ###

@authentication_bp.route('/api/forgot_password/', methods=['GET'])
@swag_from('docs/forgot_password.yml')
def _forgot_password():
	return {}

@authentication_bp.route('/api/reset_password/', methods=['GET'])
@swag_from('docs/reset_password.yml')
def _reset_password():
	return {}
