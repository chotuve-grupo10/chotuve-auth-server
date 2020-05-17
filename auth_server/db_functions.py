from flask import current_app
from psycopg2 import errors as psql_errors
import logging

create_table_command = "CREATE TABLE Users (email VARCHAR(255) NOT NULL, first_name VARCHAR(255) NOT NULL, last_name VARCHAR(255) NOT NULL, phone_number VARCHAR(255) NOT NULL, profile_picture VARCHAR(255) )"

logger = logging.getLogger('gunicorn.error')

def initialize_db():
	client = current_app.client
	if not table_exists(client, "Users"):
		cursor = client.cursor()
		try:
			cursor.execute(create_table_command)
			#cursor.execute("ALTER TABLE Users PRIMARY KEY (email);")
			client.commit()
			cursor.close()
			logger.debug('Table Users was created successfully')
		except Exception as e:
			client.rollback()
			cursor.close()
			logger.error('Error {e} creating Users table. Could not be created'.format(e=e))
	else:
		logger.debug('Table Users already exists')


def table_exists(client, table_name):

	cursor = client.cursor()
	try:
		cursor.execute("SELECT exists(SELECT 1 from {0})".format(table_name))
		client.commit()
		cursor.close()
		return True
	except psql_errors.lookup("42P01"):
		cursor.close()
		client.rollback()
		logger.debug('Table {0} does not exists'.format(table_name))
		return False