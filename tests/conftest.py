# import os
# import tempfile

import pytest
from auth_server import create_app
from flask_sqlalchemy import SQLAlchemy as sqla
import db.migrations as migrations
# pylint: disable=W0621	(redefined-outer-name)

@pytest.fixture
def app():
	# db_path = tempfile.mkstemp()
	app = create_app(test_config = {
		'TESTING': True
	})

	with app.app_context():
		pass

	return app

@pytest.fixture
def app_with_db(postgresql_db):
	# db_path = tempfile.mkstemp()
	app = create_app(test_config = {
		'TESTING': True
	},
    db_connection = postgresql_db)

	postgresql_db.session.execute(migrations.all_migrations()[0])

	with app.app_context():
		pass

	return app

@pytest.fixture
def client(app):
	return app.test_client()

@pytest.fixture
def client_with_db(app_with_db):
	return app_with_db.test_client()

@pytest.fixture
def runner(app):
	return app.test_cli_runner()
