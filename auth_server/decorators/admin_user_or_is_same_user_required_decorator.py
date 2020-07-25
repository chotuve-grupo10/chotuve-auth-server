from functools import wraps
import logging
from flask import g, request, redirect, url_for, current_app
from auth_server.validation_functions import is_request_from_admin_user
from auth_server.token_functions import get_user_with_token

logger = logging.getLogger('gunicorn.error')

def admin_user_or_is_same_user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('authorization', None)
        is_admin_user=False
        is_same_user=False
        if token is None:
            return {'Error' : 'Missing authorization token'}, 412

        if is_request_from_admin_user(token):
            is_admin_user = True

        user_email = get_user_with_token(token)
        email_user_to_modify = request.view_args['user_email']
        if (user_email == email_user_to_modify):
            is_same_user= True
        
        if (not is_same_user and not is_admin_user):
             return {'Error': 'Request not authorized to modify user data'}, 403

        return f(*args, **kwargs)
    return decorated_function
