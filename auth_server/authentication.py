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
from auth_server.persistence.reset_password_persistence import ResetPasswordPersistence
from auth_server.model.reset_password import ResetPassword
from auth_server.exceptions.reset_password_not_found_exception import ResetPasswordNotFoundException
from auth_server.exceptions.reset_password_for_non_existent_user_exception import ResetPasswordForNonExistentUserException
from auth_server.utilities.mail_functions import send_email_with_reset_password_token
from auth_server.exceptions.cant_change_password_for_firebase_user_exception import CantChangePasswordForFirebaseUser
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

@authentication_bp.route('/api/users/<user_email>/reset_password_token', methods=['POST'])
@app_server_token_required
@swag_from('docs/forgot_password.yml')
# pylint: disable=R0915
def _forgot_password(user_email):

	logger.debug('Forgot password request from user:{0}'.format(user_email))

	try:
		user_persistence = UserPersistence(current_app.db)
		user = user_persistence.get_user_by_email(user_email)

		if user.is_firebase_user():
			result = {"Error" : "user {0} is a firebase user".format(user_email)}
			status_code = HTTPStatus.PRECONDITION_FAILED
			logger.debug('User is firebase user. Cant change password')
		else:
			reset_password_persistence = ResetPasswordPersistence(current_app.db)
			try:
				# Ya teniamos un codigo para resetear la pass de este usuario
				# Si esta vencido le damos uno nuevo y sino le mandamos el mismo
				reset_password_obtained = reset_password_persistence.get_reset_password_by_email(user_email)
				logger.debug('User already has reset password')
				if reset_password_obtained.is_token_expired():
					try:
						logger.debug('Token expired. Regenerating new one')
						reset_password_persistence.delete(user_email)
						reset_password_updated = ResetPassword(user_email)
						reset_password_persistence.save(reset_password_updated)

						send_email_with_reset_password_token(user_email, reset_password_updated.token)

						result = {"Forgot password" : "email sent to {0}".format(user_email)}
						status_code = HTTPStatus.OK
						logger.debug('Email sent to user:{0}'.format(user_email))
					except ResetPasswordNotFoundException:
						logger.critical('Trying to delete non existent reset password')
						result = {"Error" : "couldnt update token for user {0}".format(user_email)}
						status_code = HTTPStatus.INTERNAL_SERVER_ERROR
					except ResetPasswordForNonExistentUserException:
						logger.critical('Trying to generate reset password for inexistent user in Users table. Super critical!')
						result = {"Error" : "user {0} doesnt exist in table users".format(user_email)}
						status_code = HTTPStatus.INTERNAL_SERVER_ERROR
				else:
					logger.debug('Token is still valid. Sending email again')
					send_email_with_reset_password_token(user_email, reset_password_obtained.token)
					result = {"Forgot password" : "email sent to {0}".format(user_email)}
					status_code = HTTPStatus.OK
					logger.debug('Email sent to user:{0}'.format(user_email))
			except ResetPasswordNotFoundException:
				# No tenemos un codigo activo para resetear la pass de este user
				# Creamos uno
				logger.debug('User hasnt reset password. Lets create one')
				try:
					reset_password_to_save = ResetPassword(user_email)
					reset_password_persistence.save(reset_password_to_save)

					result = {"Forgot password" : "email sent to {0}".format(user_email)}
					status_code = HTTPStatus.OK

					send_email_with_reset_password_token(user_email, reset_password_to_save.token)

					logger.debug('Email sent to user:{0}'.format(user_email))
				except ResetPasswordForNonExistentUserException:
					logger.critical('Trying to generate reset password for inexistent user in Users table!')
					result = {"Error" : "user {0} doesnt exist in table users".format(user_email)}
					status_code = HTTPStatus.INTERNAL_SERVER_ERROR
	except UserNotFoundException:
		result = {"Error" : "user {0} doesnt exist".format(user_email)}
		status_code = HTTPStatus.NOT_FOUND
		logger.debug('User doesnt exist')

	return result, status_code

@authentication_bp.route('/api/users/<user_email>/password', methods=['PUT'])
@app_server_token_required
@swag_from('docs/reset_password.yml')
def _reset_password(user_email):

	logger.debug('Reset password request from user:{0}'.format(user_email))

	data = request.json
	token_received = data['token']
	password_received = data['new_password']

	reset_password_persistence = ResetPasswordPersistence(current_app.db)
	try:
		reset_password_obtained = reset_password_persistence.get_reset_password_by_email(user_email)
		if reset_password_obtained.token == token_received:
			if reset_password_obtained.is_token_expired():
				logger.debug('Token is expired')
				result = {'Error' : 'token expired. Already sent new one'}
				status_code = HTTPStatus.UNAUTHORIZED
				_forgot_password(user_email)
			else:
				logger.debug('Valid token')
				user_persistence = UserPersistence(current_app.db)

				try:
					user_persistence.change_password_for_user(user_email, password_received)
					reset_password_persistence.delete(user_email)
					result = {'Reset password' : 'password updated for user {0}'.format(user_email)}
					status_code = HTTPStatus.OK
					logger.debug('Password updated')
				except CantChangePasswordForFirebaseUser:
					logger.critical('Trying to change password for firebase user!')
					result = {'Error' : 'user {0} is a firebase user'.format(user_email)}
					status_code = HTTPStatus.INTERNAL_SERVER_ERROR
				except UserNotFoundException:
					logger.critical('Cant find user!')
					result = {'Error' : 'user {0} doesnt exist'.format(user_email)}
					status_code = HTTPStatus.INTERNAL_SERVER_ERROR
				except ResetPasswordNotFoundException:
					logger.critical('Cant reset password to delete!')
					result = {'Error' : 'cant delete reset password request for user {0}'.format(user_email)}
					status_code = HTTPStatus.INTERNAL_SERVER_ERROR
		else:
			logger.debug('The token {0} is NOT correct'.format(token_received))
			result = {'Error' : 'token is NOT correct'}
			status_code = HTTPStatus.NOT_FOUND
	except ResetPasswordNotFoundException:
		logger.debug('This user didnt request to reset password')
		result = {'Error' : 'user {0} didnt request to reset password'.format(user_email)}
		status_code = HTTPStatus.NOT_FOUND

	return result, status_code
