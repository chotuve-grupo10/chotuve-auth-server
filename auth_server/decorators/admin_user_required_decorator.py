from functools import wraps
from flask import g, request, redirect, url_for, current_app
from auth_server.validation_functions import is_request_from_admin_user

def admin_user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('authorization', None)
        if token is None:
            return {'Error' : 'Missing authorization token'}, 412

        if not is_request_from_admin_user(token):
            return {'Error' : 'Request doesnt come from admin user'}, 403

        return f(*args, **kwargs)
    return decorated_function