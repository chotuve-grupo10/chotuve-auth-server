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

@app_servers_bp.route('/api/app_servers/<app_server_token>', methods=['DELETE'])
@admin_user_required
@cross_origin(allow_headers=['Content-Type'])
@swag_from('docs/delete_app_server.yml')
def _delete_app_server(app_server_token):

	try:
		app_servers_persistence = AppServerPersistence(current_app.db)
		app_servers_persistence.delete(app_server_token)
		logger.debug("Successfully deleted app server with token:" + app_server_token)
		return {'Delete app server' : 'deleted app server successfully'}, HTTPStatus.OK
	except Exception as e:
		logger.error("Error:" + str(e))
		return {'Error' : 'Couldnt delete app server'}, HTTPStatus.INTERNAL_SERVER_ERROR

@app_servers_bp.route('/api/app_servers/<app_server_token>', methods=['GET'])
@admin_user_required
@cross_origin(allow_headers=['Content-Type'])
@swag_from('docs/get_app_server_by_token.yml')
def _get_app_server(app_server_token=None):

	try:
		app_servers_persistence = AppServerPersistence(current_app.db)

		app_server = app_servers_persistence.get_app_server_by_token(app_server_token)
		logger.debug("Successfully obtained app server with token:" + app_server_token)
		return {'App server' : app_server.serialize()}, HTTPStatus.OK
	except Exception as e:
		logger.error("Error:" + str(e))
		return {'Error' : 'Couldnt get app server'}, HTTPStatus.INTERNAL_SERVER_ERROR

@app_servers_bp.route('/api/app_servers/', methods=['GET'])
@admin_user_required
@cross_origin(allow_headers=['Content-Type'])
@swag_from('docs/get_app_servers.yml')
def _get_app_servers():

	try:
		app_servers_persistence = AppServerPersistence(current_app.db)

		app_servers = app_servers_persistence.get_all_app_servers()
		app_servers_serialized = [item.serialize() for item in app_servers]
		logger.debug("Successfully obtained all apps servers")
		return {'App servers' : app_servers_serialized}, HTTPStatus.OK

	except Exception as e:
		logger.error("Error:" + str(e))
		return {'Error' : 'Couldnt get app servers'}, HTTPStatus.INTERNAL_SERVER_ERROR
