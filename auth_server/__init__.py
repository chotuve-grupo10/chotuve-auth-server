import os
import logging
from urllib.parse import urlparse
import psycopg2 as psql
from psycopg2 import errors as psql_errors
from flask import Flask, request
from flasgger import Swagger
from flasgger import swag_from
from flask_cors import CORS
import simplejson as json
from flask_sqlalchemy import SQLAlchemy
from auth_server.authentication import authentication_bp
from auth_server.users import users_bp
from auth_server.db_functions import initialize_db
from auth_server.token_functions import *

def create_app(test_config=None, db_connection=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)

	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	app.db = db_connection or SQLAlchemy(app)

	parameters = urlparse(os.environ.get('DATABASE_URL'))
	username = parameters.username
	password = parameters.password
	database = parameters.path[1:]
	hostname = parameters.hostname
	app.client = psql.connect(
		database=database,
		user=username,
		password=password,
		host=hostname)

	with app.app_context():
		initialize_db()

	app.config.from_mapping(SECRET_KEY='dev')
	Swagger(app)
	CORS(app, resources=r'/*', allow_headers='Content-Type')



	if test_config is None:
		# load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
		# load the test config if passed in
		app.config.from_mapping(test_config)

	# ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# Set up del log
	# Basicamente lo que se esta haciendo es usar el handler de gunicorn para
	# que todos los logs salgan por ese canal.
	gunicorn_logger = logging.getLogger('gunicorn.error')
	app.logger.handlers = gunicorn_logger.handlers
	app.logger.setLevel(gunicorn_logger.level)

	app.logger.debug('Log configuration finished')
	app.logger.info('Auth server running...')

	# Registro de blueprints que encapsulan comportamiento:
	with app.app_context():
		app.register_blueprint(authentication_bp)
		app.register_blueprint(users_bp)

	@app.route('/api/ping/', methods=['GET'])
	@swag_from('docs/ping.yml')
	def _respond():
		response = {}
		response['Health'] = 'OK'
		return json.dumps(response)

	@app.route('/api/hello/')
	def _hello():
		return 'Hello, World!'

	# @app.route('/user/<username>')
	# def show_user_profile(username):
	#     # show the user profile for that user
	#     return 'User name is %s' % escape(username)

	# @app.route('/post/<int:post_id>')
	# def show_post(post_id):
	#     # show the post with the given id, the id is an integer
	#     return 'Post %d' % post_id

	@app.route('/api/about/')
	@swag_from('docs/about.yml')
	def _about():
		return 'This is Authorization Server for chotuve-10. Still in construction'

	@app.route('/')
	def _index():
		return "<h1>Welcome to auth server !</h1>"

	### Métodos no implementados aún ###
	# @app.route('/api/profile/', methods=['GET'])
	# @swag_from('docs/profile.yml')
	# def _profile():
	# 	jwt_token = request.headers.get('authorization', None)
	# 	result, status_code = validate_token(jwt_token)
	# 	return result, status_code
	#
	# @app.route('/api/update_profile/user/<int:id>', methods=['PATCH'])
	# @swag_from('docs/update_profile.yml')
	# def _update_profile():
	# 	return {}
	#
	# @app.route('/api/register_app_server/', methods=['GET'])
	# @swag_from('docs/register_app_server.yml')
	# def _register_app_server():
	# 	return {}
	#
	# @app.route('/api/stats/', methods=['GET'])
	# @swag_from('docs/stats.yml')
	# def _stats():
	# 	return {}
	#
	# @app.route('/api/status/', methods=['GET'])
	# @swag_from('docs/status.yml')
	# def _status():
	# 	return {}

	return app
