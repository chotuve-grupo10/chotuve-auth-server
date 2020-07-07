import logging
import hashlib
from http import HTTPStatus
from flask import Blueprint, current_app, request
from auth_server.db_functions import *
from auth_server.token_functions import *
from auth_server.persistence.app_server_persistence import AppServerPersistence
from auth_server.exceptions.app_server_not_found_exception import AppServerNotFoundException

ADMIN_FLAG_POSITION = 7
BLOCKED_FLAG_POSITION = 8

logger = logging.getLogger('gunicorn.error')

def validar_usuario(user, password):
	hashed = user[4]
	salt = user[5]
	for i in range(256):
		pimienta = chr(i)
		if hashlib.sha512((password+salt+pimienta).encode('utf-8')).hexdigest() == hashed:
			return True
	return False


def validate_firebase_user(user):
	firebase_user = user[6]
	return firebase_user == '1'


def validate_admin_user(user):
	# Si se registro con firebase no puede ser admin.
	if validate_firebase_user(user):
		return False
	admin_user = user[ADMIN_FLAG_POSITION]
	return admin_user == '1'

def is_blocked_user(user):
	admin_user = user[BLOCKED_FLAG_POSITION]
	return admin_user == '1'

def is_request_from_admin_user(token):
	result_validate, status_code_validate = validate_token(token)

	if status_code_validate == 200:
		logger.debug('Valid token')
		try:
			user_email = get_user_with_token(token)
			logger.debug('User with token is ' + user_email)
			with current_app.app_context():
				result, status_code, user = get_user(current_app.client, user_email)

			if HTTPStatus.OK == status_code:
				if is_blocked_user(user):
					logger.debug('This user is BLOCKED')
					return False

				if validate_admin_user(user):
					logger.debug('Token is from admin user')
					return True

				logger.error('User is not admin user')
				return False

			logger.error(result)
			return False

		except ValueError as error:
			logger.error(error)
			return False
	else:
		logger.error('The token is invalid')
		return False

def is_valid_token_from_app_server(app_server_token):

	app_servers_persistence = AppServerPersistence(current_app.db)
	try:
		app_servers_persistence.get_app_server_by_token(app_server_token)
		logger.debug('App server token is valid')
		return True
	except AppServerNotFoundException as notFound:
		logger.debug('App server token is NOT valid')
		return False
