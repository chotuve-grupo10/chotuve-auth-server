import logging
from flask import Blueprint, current_app, request
from flasgger import swag_from

users_bp = Blueprint('users', __name__)
logger = logging.getLogger('gunicorn.error')

@users_bp.route('/api/delete_user/<user_email>', methods=['DELETE'])
@swag_from('docs/delete_user.yml')
def _delete_user(user_email):
	logger.debug('Requested to delete user: ' + user_email)
	return {}
