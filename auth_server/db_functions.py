import logging
import hashlib
import simplejson as json
from flask import current_app
from psycopg2 import errors as psql_errors
from auth_server.random_string import *

EMAIL_POSITION = 0
FULL_NAME_POSITION = 1
PHONE_NUMBER_POSITION = 2
PROFILE_PICTURE_POSITION = 3
BLOCKED_USER_POSITION = 8

create_table_command = """CREATE TABLE Users (
						email VARCHAR(255) PRIMARY KEY ,
						full_name VARCHAR(255) NOT NULL,
						phone_number VARCHAR(255),
						profile_picture VARCHAR(255),
						hash VARCHAR(255) NOT NULL,
						salt VARCHAR(255) NOT NULL,
						firebase_user VARCHAR(1) NOT NULL,
						admin_user VARCHAR(1) NOT NULL,
						blocked_user VARCHAR(1) NOT NULL);"""

create_app_servers_table_command = """CREATE TABLE AppServers (
						token VARCHAR(255) PRIMARY KEY ,
						registered_at timestamp NOT NULL);"""

create_reset_password_table_command = """CREATE TABLE ResetPassword (
						token VARCHAR(6) NOT NULL,
						email VARCHAR(255),
						registered_at timestamp NOT NULL,
						PRIMARY KEY (email),
    					FOREIGN KEY (email) REFERENCES Users(email));"""

logger = logging.getLogger('gunicorn.error')

def initialize_db():
	initialize_users_table()
	initialize_app_servers_table()
	initialize_reset_password_table()

def initialize_users_table():
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

def initialize_app_servers_table():
	client = current_app.client
	if not table_exists(client, "AppServers"):
		cursor = client.cursor()
		try:
			cursor.execute(create_app_servers_table_command)
			client.commit()
			cursor.close()
			logger.debug('Table AppServers was created successfully')
		except Exception as e:
			client.rollback()
			cursor.close()
			logger.error('Error {e} creating AppServers table. Could not be created'.format(e=e))
	else:
		logger.debug('Table AppServers already exists')

def initialize_reset_password_table():
	client = current_app.client
	if not table_exists(client, "ResetPassword"):
		cursor = client.cursor()
		try:
			cursor.execute(create_reset_password_table_command)
			client.commit()
			cursor.close()
			logger.debug('Table ResetPasword was created successfully')
		except Exception as e:
			client.rollback()
			cursor.close()
			logger.error('Error {e} creating ResetPassword table. Could not be created'.format(e=e))
	else:
		logger.debug('Table ResetPassword already exists')


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

def insert_admin_user_into_users_db(client, user_information):

	# with current_app.app_context():
	client = current_app.client
	sal = random_string(6)
	pimienta = random_string(1)
	cursor = client.cursor()
	try:
		cursor.execute(
			"""INSERT INTO Users(email,full_name,phone_number,profile_picture,hash,salt,firebase_user,admin_user,blocked_user)
				VALUES('{email}','{full_name}','{phone_number}','{profile_picture}','{hash}','{salt}','{firebase_user}','{admin_user}','{blocked_user}');"""
					.format(email=user_information['email'],
					full_name=user_information['full name'],
					phone_number=user_information['phone number'],
					profile_picture=user_information['profile picture'],
					hash=hashlib.sha512((user_information['password']+sal+pimienta).encode('utf-8')).hexdigest(),
					salt=sal,
					firebase_user='0',
					admin_user='1',
					blocked_user='0'))

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
			"""INSERT INTO Users(email,full_name,phone_number,profile_picture,hash,salt,firebase_user,admin_user,blocked_user)
				VALUES('{email}','{full_name}','{phone_number}','{profile_picture}','{hash}','{salt}','{firebase_user}','{admin_user}','{blocked_user}');"""
					.format(email=claims.get('email'),
					full_name=claims.get('name'),
					phone_number='NULL',
					profile_picture=claims.get('picture'),
					hash='0',
					salt='0',
					firebase_user='1',
					admin_user='0',
					blocked_user='0'))

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

def get_all_users(client):

	cursor = client.cursor()
	logger.debug('Getting all users')
	try:
		cursor.execute("SELECT * FROM users WHERE admin_user = '{value}'".format(value=0))
		users = cursor.fetchall()
		logger.debug('Obtained all users')
		cursor.close()
		return json.dumps([serialize_user(user) for user in users])
	except Exception as e:
		client.rollback()
		cursor.close()
		logger.error('Error {e}. Could not get users'.format(e=e))
		raise Exception(str(e))

def modify_user_from_db(client, mail, user_information):

	cursor = client.cursor()
	logger.debug('Modifying user: {user}'.format(user=mail))
	try:
		cursor.execute("""UPDATE users SET email='{new_mail}', full_name='{new_name}', phone_number='{new_phone}', profile_picture='{new_picture}'
						WHERE email='{email}';"""
					.format(new_mail=user_information['email'],
					new_name=user_information['full_name'],
					new_phone=user_information['phone_number'],
					new_picture=user_information['profile_picture'],
					email=mail))
		client.commit()
		logger.debug('User modified')
		result = {'Modify':'successfully modified user with email {0}'.format(mail)}
		status_code = 200
	except Exception as e:
		client.rollback()
		logger.error('Error {e}. Could not modify user'.format(e=e))
		result = {'Modify': 'Error {e}'.format(e=e)}
		status_code = 500

	cursor.close()
	return result, status_code

def serialize_user(user):
	return {
		'email' : user[EMAIL_POSITION],
		'full_name' : user[FULL_NAME_POSITION],
		'phone_number' : user[PHONE_NUMBER_POSITION],
		'profile_picture': user[PROFILE_PICTURE_POSITION],
		'blocked': user[BLOCKED_USER_POSITION] == '1'
	}
