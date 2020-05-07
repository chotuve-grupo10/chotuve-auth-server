import os
from flask import Flask, request
from flasgger import Swagger
# La documentación de Flask dice que SIMPLEJSON funciona más rápido
# y que Flask está bien integrado con este
import simplejson as json

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)

	# Parametro que no estamos usando actualmente en from_mapping
	# DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
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

	@app.route('/api/ping/', methods=['GET'])
	def _respond():
		"""
    Este es un método para verificar el status del server
    ---
    responses:
      200:
        description: Server status
    """
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
	def _about():
		"""
    Este es un método para recibir información del server
    ---
    responses:
      200:
        description: Server status
    """
		return 'This is Authorization Server for chotuve-10. Still in construction'


	@app.route('/')
	def _index():
		return "<h1>Welcome to auth server !</h1>"

	return app
