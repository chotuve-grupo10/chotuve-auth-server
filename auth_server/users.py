import os
import logging
from http import HTTPStatus
import requests
from flask import Blueprint, current_app, request
from flask_cors import CORS, cross_origin
from flasgger import swag_from
from auth_server.validation_functions import *
from auth_server.db_functions import *
from auth_server.decorators.admin_user_required_decorator import admin_user_required
from auth_server.persistence.user_persistence import UserPersistence
from auth_server.exceptions.user_not_found_exception import UserNotFoundException
from auth_server.exceptions.user_already_blocked_exception import UserlAlreadyBlockedException
from auth_server.exceptions.user_already_unblocked_exception import UserlAlreadyUnblockedException

users_bp = Blueprint('users', __name__)
logger = logging.getLogger('gunicorn.error')

@users_bp.route('/api/users/<user_email>', methods=['DELETE'])
@admin_user_required
@cross_origin(allow_headers=['Content-Type', 'authorization'])
@swag_from('docs/delete_user.yml')
def _delete_user(user_email):
	logger.debug('Requested to delete user: ' + user_email)

	try:
		user_persistence = UserPersistence(current_app.db)
		user_persistence.block_user(user_email)
		logger.debug('Successfully deleted user')

		logger.debug('Requesting to delete user from app server')
		delete_user_app_server_url = os.environ.get('APP_SERVER_URL') + '/api/users/' + user_email
		logger.debug('Url: ' + delete_user_app_server_url)
		response_app_server = requests.delete(url=delete_user_app_server_url)

		if response_app_server.status_code == HTTPStatus.OK:
			result, status_code = {'Delete' : 'successfully deleted user with email {0}'.format(user_email)}, HTTPStatus.OK
			logger.debug('User deleted')
		else:
			result, status_code = {'Error' : 'Couldnt delete user {0} in app server'.format(user_email)}, HTTPStatus.INTERNAL_SERVER_ERROR
			logger.debug('Couldnt delete user from app server')
			try:
				user_persistence.unblock_user(user_email)
			except UserNotFoundException:
				logger.critical('Couldnt find user to unblock')
			except UserlAlreadyUnblockedException:
				logger.critical('User was never blocked')
	except UserNotFoundException:
		result, status_code = {'Error' : 'User {0} doesnt exist'.format(user_email)}, HTTPStatus.NOT_FOUND
		logger.debug('User doesnt exist')
	except UserlAlreadyBlockedException:
		result, status_code = {'Error' : 'User {0} was already deleted'.format(user_email)}, HTTPStatus.NOT_FOUND
		logger.debug('User was already deleted')

	return result, status_code

@users_bp.route('/api/users/<user_email>', methods=['PUT'])
@admin_user_required
@cross_origin(allow_headers=['Content-Type', 'authorization'])
@swag_from('docs/modify_user.yml')
def _modify_user(user_email):
	logger.debug('Requested to modify user: ' + user_email)

	data = request.json
	with current_app.app_context():
		result, status_code = modify_user_from_db(current_app.client, user_email, data)

	return result, status_code

@users_bp.route('/api/users/', methods=['GET'])
@admin_user_required
@cross_origin(allow_headers=['Content-Type', 'authorization'])
@swag_from('docs/users.yml')
def _get_users():

	with current_app.app_context():
		try:
			result = get_all_users(current_app.client)
			status_code = 200
		except Exception as exc:
			result = {'Error' : str(exc)}
			status_code = 500

	return result, status_code
