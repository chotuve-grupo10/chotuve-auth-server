from unittest.mock import patch
from auth_server.db_functions import insert_into_users_db
import simplejson as json

def test_register_user_succesfully(client):
	with patch('auth_server.authentication.insert_into_users_db') as mock:
		user_information = {'email': 'this_email_should_not_be_saved@test.com',
				'password': 'fake password',
				'first name': 'first name', 'last name': 'last name',
				'phone number': 'phone number', 'profile picture': 'profile picture',
				'hash': 'hash', 'salt': 'salt'}

		result = {'Registration': 'Successfully registered new user with email {0}'.format(user_information['email'])}
		status_code = 201

		mock.return_value = result, status_code

		response = client.post('/api/register/', json=user_information,
							   follow_redirects=False)
		value_expected = {'Registration' :
			'Successfully registered new user with email {0}'.format(user_information['email'])}

		assert mock.called
		assert json.loads(response.data) == value_expected

def test_register_user_already_registered(client):
	with patch('auth_server.authentication.insert_into_users_db') as mock:
		user_information = {'email': 'diegote@gmail.com',
				'password': 'fake password',
				'first name': 'first name', 'last name': 'last name',
				'phone number': 'phone number', 'profile picture': 'profile picture',
				'hash': 'hash', 'salt': 'salt'}

		result = {'Registration': 'This user already exists!'}
		status_code = 409

		mock.return_value = result, status_code

		response = client.post('/api/register/', json=user_information,
							   follow_redirects=False)
		value_expected = {'Registration' :
			'This user already exists!'}

		assert mock.called
		assert json.loads(response.data) == value_expected
