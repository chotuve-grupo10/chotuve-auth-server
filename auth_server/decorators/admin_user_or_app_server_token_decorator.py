from functools import wraps
import logging
from flask import g, request, redirect, url_for, current_app
from auth_server.validation_functions import is_request_from_admin_user
from auth_server.validation_functions import is_valid_token_from_app_server

logger = logging.getLogger('gunicorn.error')

def admin_user_or_app_server_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('authorization', None)
        token_app_server = request.headers.get('AppServerToken', None)

        if token is None and token_app_server is None:
            return {'Error' : 'Missing authorization or app server token'}, 412

        if token is not None:
            if not is_request_from_admin_user(token):
                return {'Error' : 'Request doesnt come from admin user'}, 403
        else:
            if not is_valid_token_from_app_server(token_app_server):
                return {'Error' : 'App server token NOT valid'}, 403

        return f(*args, **kwargs)
    return decorated_function
