from functools import wraps
from flask import g, request, redirect, url_for, current_app
from auth_server.validation_functions import is_valid_token_from_app_server

def app_server_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        app_server_token = request.headers.get('Token')
        if app_server_token is None:
            return {'Error' : 'Missing app server token (Token)'}, 412

        if not is_valid_token_from_app_server(app_server_token):
            return {'Error' : 'App server token NOT valid'}, 403

        return f(*args, **kwargs)
    return decorated_function
