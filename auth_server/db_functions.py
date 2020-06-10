import logging
import hashlib
from flask import current_app
from psycopg2 import errors as psql_errors
from auth_server.random_string import *

create_table_command = """CREATE TABLE Users (
						email VARCHAR(255) PRIMARY KEY ,
						full_name VARCHAR(255) NOT NULL,
						phone_number VARCHAR(255),
						profile_picture VARCHAR(255),
						hash VARCHAR(255) NOT NULL,
						salt VARCHAR(255) NOT NULL,
						firebase_user VARCHAR(1) NOT NULL,
						admin_user VARCHAR(1) NOT NULL);"""

logger = logging.getLogger('gunicorn.error')

def initialize_db():
	client = current_app.client
	if not table_exists(client, "Users"):
		cursor = client.cursor()
		try:
			cursor.execute(create_table_command)
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

def insert_local_user_into_users_db(client, user_information):

	# with current_app.app_context():
	client = current_app.client
	sal = random_string(6)
	pimienta = random_string(1)
	cursor = client.cursor()
	try:
		cursor.execute(
			"""INSERT INTO Users(email,full_name,phone_number,profile_picture,hash,salt,firebase_user,admin_user)
				VALUES('{email}','{full_name}','{phone_number}','{profile_picture}','{hash}','{salt}','{firebase_user}','{admin_user}');"""
					.format(email=user_information['email'],
					full_name=user_information['full name'],
					phone_number=user_information['phone number'],
					profile_picture=user_information['profile picture'],
					hash=hashlib.sha512((user_information['password']+sal+pimienta).encode('utf-8')).hexdigest(),
					salt=sal,
					firebase_user='0',
					admin_user='0'))

		client.commit()
		logger.debug('Successfully registered new user with email {0}'.format(user_information['email']))
		result = {'Registration': 'Successfully registered new user with email {0}'.format(user_information['email'])}
		status_code = 201		# Created
	except psql_errors.UniqueViolation:
		client.rollback()
		logger.error('This user already exists!')
		result = {'Registration': 'This user already exists!'}
		status_code = 409		# Conflict
	except Exception as e:
		client.rollback()
		logger.error('Error {e}. Could not insert new user'.format(e=e))
		result = {'Registration': 'Error {e}. Could not insert new user'.format(e=e)}
		status_code = 500

	cursor.close()
	return result, status_code

def insert_admin_user_into_users_db(client, user_information):

	# with current_app.app_context():
	client = current_app.client
	sal = random_string(6)
	pimienta = random_string(1)
	cursor = client.cursor()
	try:
		cursor.execute(
			"""INSERT INTO Users(email,full_name,phone_number,profile_picture,hash,salt,firebase_user,admin_user)
				VALUES('{email}','{full_name}','{phone_number}','{profile_picture}','{hash}','{salt}','{firebase_user}','{admin_user}');"""
					.format(email=user_information['email'],
					full_name=user_information['full name'],
					phone_number=user_information['phone number'],
					profile_picture=user_information['profile picture'],
					hash=hashlib.sha512((user_information['password']+sal+pimienta).encode('utf-8')).hexdigest(),
					salt=sal,
					firebase_user='0',
					admin_user='1'))

		client.commit()
		logger.debug('Successfully registered new admin user with email {0}'.format(user_information['email']))
		result = {'Registration': 'Successfully registered new admin user with email {0}'.format(user_information['email'])}
		status_code = 201		# Created
	except psql_errors.UniqueViolation:
		client.rollback()
		logger.error('This user already exists!')
		result = {'Registration': 'This user already exists!'}
		status_code = 409		# Conflict
	except Exception as e:
		client.rollback()
		logger.error('Error {e}. Could not insert new user'.format(e=e))
		result = {'Registration': 'Error {e}. Could not insert new user'.format(e=e)}
		status_code = 500

	cursor.close()
	return result, status_code

def insert_firebase_user_into_users_db(client, claims):

	cursor = client.cursor()
	try:
		cursor.execute(
			"""INSERT INTO Users(email,full_name,phone_number,profile_picture,hash,salt,firebase_user,admin_user)
				VALUES('{email}','{full_name}','{phone_number}','{profile_picture}','{hash}','{salt}','{firebase_user}','{admin_user}');"""
					.format(email=claims.get('email'),
					full_name=claims.get('name'),
					phone_number='NULL',
					profile_picture=claims.get('picture'),
					hash='0',
					salt='0',
					firebase_user='1',
					admin_user='0'))

		client.commit()
		logger.debug('Successfully registered new user with email {0}'.format(claims.get('email')))
		result = {'Registration': 'Successfully registered new user with email {0}'.format(claims.get('email'))}
		status_code = 201		# Created
	except psql_errors.UniqueViolation:
		client.rollback()
		logger.error('This user already exists!')
		result = {'Registration': 'This user already exists!'}
		status_code = 409		# Conflict
	except Exception as e:
		client.rollback()
		logger.error('Error {e}. Could not insert new user'.format(e=e))
		result = {'Registration': 'Error {e}. Could not insert new user'.format(e=e)}
		status_code = 500

	cursor.close()
	return result, status_code

def get_user(client, mail):

	cursor = client.cursor()
	logger.debug('Looking for user {user}'.format(user=mail))
	try:
		cursor.execute("SELECT * FROM users WHERE email = '{mail}'".format(mail=mail))
		row = cursor.fetchone()
		if row is not None:
			logger.debug('User found')
			result = {'Login': 'user found'}
			status_code = 200
		else:
			logger.debug('User NOT found')
			result = {'Login': 'user NOT found'}
			status_code = 404
	except Exception as e:
		client.rollback()
		logger.error('Error {e}. Could not find user'.format(e=e))
		result = {'Registration': 'Error {e}. Problems finding user'.format(e=e)}
		status_code = 500

	cursor.close()
	return result, status_code, row
