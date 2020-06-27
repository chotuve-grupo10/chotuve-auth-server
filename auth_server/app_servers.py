import logging
from http import HTTPStatus
from flask import Blueprint, current_app, request
from flask_cors import CORS, cross_origin
from flasgger import swag_from
from auth_server.decorators.admin_user_required_decorator import admin_user_required
from auth_server.persistence.app_server_persistence import AppServerPersistence
from auth_server.model.app_server import AppServer

app_servers_bp = Blueprint('app_servers', __name__)
logger = logging.getLogger('gunicorn.error')

@app_servers_bp.route('/api/app_servers/', methods=['POST'])
@admin_user_required
@cross_origin(allow_headers=['Content-Type'])
@swag_from('docs/register_app_server.yml')
def _regiter_app_server():

    try:
        app_servers_persistence = AppServerPersistence(current_app.db)
        app_server = AppServer()
        app_servers_persistence.save(app_server)
        logger.debug("Successfully registered app server")
        return {'App server token' : app_server.get_token()}, HTTPStatus.CREATED
    except Exception as e:
        logger.error("Error:" + str(e))
        return {'Error' : 'Couldnt register app server'}, HTTPStatus.INTERNAL_SERVER_ERROR
