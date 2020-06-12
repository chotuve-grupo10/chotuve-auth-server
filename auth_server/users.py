import logging
from flask import Blueprint, current_app, request
from flasgger import swag_from
from auth_server.validation_functions import *
from auth_server.db_functions import *

users_bp = Blueprint('users', __name__)
logger = logging.getLogger('gunicorn.error')

@users_bp.route('/api/delete_user/<user_email>', methods=['DELETE'])
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
