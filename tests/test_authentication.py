from unittest.mock import patch
import simplejson as json
# from auth_server.db_functions import insert_into_users_db

def test_register_user_succesfully(client):
	with patch('auth_server.authentication.insert_local_user_into_users_db') as mock:
		user_information = {'email': 'this_email_should_not_be_saved@test.com',
				'password': 'fake password',
				'full name': 'full name',
				'phone number': 'phone number', 'profile picture': 'profile picture',
				'hash': 'hash', 'salt': 'salt', 'firebase_user':'0', 'admin_user':'0'}

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
	with patch('auth_server.authentication.insert_local_user_into_users_db') as mock:
		user_information = {'email': 'diegote@gmail.com',
				'password': 'fake password',
				'full name': 'full name',
				'phone number': 'phone number', 'profile picture': 'profile picture',
				'hash': 'hash', 'salt': 'salt', 'firebase_user':'0', 'admin_user':'0'}

		result = {'Registration': 'This user already exists!'}
		status_code = 409

		mock.return_value = result, status_code

		response = client.post('/api/register/', json=user_information,
							   follow_redirects=False)
		value_expected = {'Registration' :
			'This user already exists!'}

		assert mock.called
		assert json.loads(response.data) == value_expected

def test_login_user_succesful(client):
	with patch('auth_server.authentication.get_user') as mock_get_user:
		result = {}
		status_code = 200
		user = ('diegote@gmail.com')
		mock_get_user.return_value = result, status_code, user

		with patch('auth_server.authentication.validar_usuario') as mock_validar:

			with patch('auth_server.authentication.generate_auth_token') as mock_token_generation:
				mock_token_generation.return_value = 'THISISAFAKETOKEN'
				user_information = {'email': 'diegote@gmail.com',
									'password': 'fake_falopa'}


				response = client.post('/api/login/', json=user_information,
									   follow_redirects=False)
				value_expected = {'Token':
								  'THISISAFAKETOKEN'}

			mock_validar.return_value = True
			assert mock_get_user.called
			assert mock_validar.called
			assert mock_token_generation.called
			assert json.loads(response.data) == value_expected

def test_login_user_not_found(client):
	with patch('auth_server.authentication.get_user') as mock_get_user:
		result = {'Login': 'user NOT found'}
		status_code = 404
		user = None
		mock_get_user.return_value = result, status_code, user

		user_information = {'email': 'this_user_does_not_Exist@gmail.com',
							'password': 'some_password'}

		response = client.post('/api/login/', json=user_information,
									   follow_redirects=False)
		value_expected = result

		assert mock_get_user.called
		assert json.loads(response.data) == value_expected
