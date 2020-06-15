from unittest.mock import patch
import simplejson as json

def test_cant_delete_user_request_doesnt_come_from_admin_user(client):
	with patch('auth_server.users.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = False

		hed = {'authorization': 'FAKETOKEN'}

		response = client.delete('/api/delete_user/' + user_email, headers=hed, follow_redirects=False)

		value_expected = {'Error':'This request doesnt come from an admin user'}

		assert mock.called
		assert json.loads(response.data) == value_expected

def test_delete_user_successfully(client):
	with patch('auth_server.users.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = True

		with patch('auth_server.users.delete_user_from_db') as mock_delete_user:

			hed = {'authorization': 'TOKEN'}

			mock_delete_user.return_value = {'Delete':'successfully deleted user with email {0}'.format(user_email)}, 200

			response = client.delete('/api/delete_user/' + user_email, headers=hed, follow_redirects=False)

			value_expected = {'Delete':'successfully deleted user with email {0}'.format(user_email)}

			assert mock.called
			assert mock_delete_user.called
			assert json.loads(response.data) == value_expected

def test_cant_modify_user_request_doesnt_come_from_admin_user(client):
	with patch('auth_server.users.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = False

		hed = {'authorization': 'FAKETOKEN'}

		response = client.put('/api/modify_user/' + user_email, headers=hed, follow_redirects=False)

		value_expected = {'Error':'This request doesnt come from an admin user'}

		assert mock.called
		assert json.loads(response.data) == value_expected

def test_modify_user_successfully(client):
	with patch('auth_server.users.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = True

		with patch('auth_server.users.modify_user_from_db') as mock_modify_user:

			hed = {'authorization': 'TOKEN'}

			user_information = {'email': 'test@test.com',
				'password': 'fake password',
				'full name': 'full name',
				'phone number': 'phone number', 'profile picture': 'profile picture'}

			mock_modify_user.return_value = {'Modify':'successfully modified user with email {0}'.format(user_email)}, 200

			response = client.put('/api/modify_user/' + user_email, json=user_information, headers=hed, follow_redirects=False)

			value_expected = {'Modify':'successfully modified user with email {0}'.format(user_email)}

			assert mock.called
			assert mock_modify_user.called
			assert json.loads(response.data) == value_expected