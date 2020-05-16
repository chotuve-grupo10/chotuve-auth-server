from flask import current_app
from psycopg2 import errors as psql_errors
import logging

logger = logging.getLogger('gunicorn.error')
#client = current_app.client # esto no le gusta

def initialize_db(client):

	if not table_exists("Users"):
		# TODO: try: ### except Exception as e: ####
		cursor = client.cursor()
		cursor.execute("CREATE TABLE Users (email VARCHAR(255) NOT NULL, first_name VARCHAR(255) NOT NULL, last_name VARCHAR(255) NOT NULL, phone_number VARCHAR(255) NOT NULL, profile_picture VARCHAR(255))")
		#cursor.execute("ALTER TABLE Users PRIMARY KEY (email);")
		client.commit()
		cursor.close()
		logger.debug('Table Users was created successfully')
	else:
		logger.debug('Table Users already exists')


def table_exists(table_name):

	try:
		cursor = client.cursor()
		cursor.execute("SELECT exists(SELECT 1 from {0})".format(table_name))
		rowcount = cursor.rowcount
		cursor.close()
		logger.debug('Rowcount for table {0} is {1}'.format(table_name, rowcount))
		return True
	# except psql_errors.UndefinedTable:
	except psql_errors.lookup("42P01"):
		cursor.close()
		logger.debug('Table {0} does not exists'.format(table_name))
		return False