import os
import logging
import psycopg2 as psql
from psycopg2 import errors as psql_errors
from flask import Flask, request
from flasgger import Swagger
from flasgger import swag_from
from urllib.parse import urlparse
import simplejson as json
from auth_server.authentication import authentication_bp
# from auth_server.db_functions import initialize_db

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)

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

	# TODO: no funciona el mismo código al ser encapsulado. Tira un error cuando
	#  tiene que crear la tabla
	# with app.app_context():
	# 	initialize_db()

	client = app.client
	cursor = client.cursor()
	try:
		cursor.execute(
			"CREATE TABLE Users (email VARCHAR(255) NOT NULL, first_name VARCHAR(255) NOT NULL, last_name VARCHAR(255) NOT NULL, phone_number VARCHAR(255) NOT NULL, profile_picture VARCHAR(255))")
		# cursor.execute("ALTER TABLE Users PRIMARY KEY (email);")
		client.commit()
		app.logger.info('Table Users was created successfully')
	except psql_errors.DuplicateTable:
		client.rollback()
		app.logger.info('Table Users already exists')
	# Close communication with the database
	# client.close()

	app.config.from_mapping(SECRET_KEY='dev')
	Swagger(app)

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
	@app.route('/api/profile/', methods=['GET'])
	@swag_from('docs/profile.yml')
	def _profile():
		return {}

	@app.route('/api/update_profile/user/<int:id>', methods=['PATCH'])
	@swag_from('docs/update_profile.yml')
	def _update_profile():
		return {}

	@app.route('/api/register_app_server/', methods=['GET'])
	@swag_from('docs/register_app_server.yml')
	def _register_app_server():
		return {}

	@app.route('/api/stats/', methods=['GET'])
	@swag_from('docs/stats.yml')
	def _stats():
		return {}

	@app.route('/api/status/', methods=['GET'])
	@swag_from('docs/status.yml')
	def _status():
		return {}

	return app
