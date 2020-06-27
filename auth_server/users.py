import logging
from flask import Blueprint, current_app, request
from flask_cors import CORS, cross_origin
from flasgger import swag_from
from auth_server.validation_functions import *
from auth_server.db_functions import *
from auth_server.decorators.admin_user_required_decorator import admin_user_required

users_bp = Blueprint('users', __name__)
logger = logging.getLogger('gunicorn.error')

@users_bp.route('/api/delete_user/<user_email>', methods=['DELETE'])
@admin_user_required
@cross_origin(allow_headers=['Content-Type'])
@swag_from('docs/delete_user.yml')
def _delete_user(user_email):
	logger.debug('Requested to delete user: ' + user_email)

	data = request.json
	with current_app.app_context():
		result, status_code = delete_user_from_db(current_app.client, user_email)

	return result, status_code

@users_bp.route('/api/modify_user/<user_email>', methods=['PUT'])
@admin_user_required
@cross_origin(allow_headers=['Content-Type'])
@swag_from('docs/modify_user.yml')
def _modify_user(user_email):
	logger.debug('Requested to modify user: ' + user_email)

	data = request.json
	with current_app.app_context():
		result, status_code = modify_user_from_db(current_app.client, user_email, data)

	return result, status_code

@users_bp.route('/api/users/', methods=['GET'])
@admin_user_required
@cross_origin(allow_headers=['Content-Type'])
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
