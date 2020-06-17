import logging
from flask import Blueprint, current_app, request
from flask_cors import CORS, cross_origin
from flasgger import swag_from
from auth_server.validation_functions import *
from auth_server.db_functions import *

users_bp = Blueprint('users', __name__)
logger = logging.getLogger('gunicorn.error')

@users_bp.route('/api/delete_user/<user_email>', methods=['DELETE'])
@cross_origin(allow_headers=['Content-Type'])
@swag_from('docs/delete_user.yml')
def _delete_user(user_email):
	logger.debug('Requested to delete user: ' + user_email)

	token = request.headers.get('authorization', None)

	if is_request_from_admin_user(token):
		logger.debug('Token is from admin user')
		data = request.json
		with current_app.app_context():
			result, status_code = delete_user_from_db(current_app.client, user_email)
	else:
		logger.error('Request doesnt come from admin user')
		result, status_code = {'Error':'This request doesnt come from an admin user'}, 401

	return result, status_code

@users_bp.route('/api/modify_user/<user_email>', methods=['PUT'])
@cross_origin(allow_headers=['Content-Type'])
@swag_from('docs/modify_user.yml')
def _modify_user(user_email):
	logger.debug('Requested to modify user: ' + user_email)

	token = request.headers.get('authorization', None)

	if is_request_from_admin_user(token):
		logger.debug('Token is from admin user')
		data = request.json
		with current_app.app_context():
			result, status_code = modify_user_from_db(current_app.client, user_email, data)
	else:
		logger.error('Request doesnt come from admin user')
		result, status_code = {'Error':'This request doesnt come from an admin user'}, 401

	return result, status_code

@users_bp.route('/api/users/', methods=['GET'])
@cross_origin(allow_headers=['Content-Type'])
@swag_from('docs/users.yml')
def _get_users():

	token = request.headers.get('authorization', None)

	if is_request_from_admin_user(token):
		logger.debug('Token is from admin user')
		#with current_app.app_context():
			# result, status_code = modify_user_from_db(current_app.client, user_email, data)
	else:
		logger.error('Request doesnt come from admin user')
		result, status_code = {'Error':'This request doesnt come from an admin user'}, 401

	return result, status_code
