import requests
import pytest
from unittest.mock import patch
import simplejson as json
from auth_server.persistence.user_persistence import UserPersistence
from auth_server.model.user import User
from auth_server.exceptions.user_not_found_exception import UserNotFoundException
from auth_server.exceptions.user_already_blocked_exception import UserlAlreadyBlockedException

def raise_user_not_found_exception(cls, *args, **kwargs):
	raise UserNotFoundException

def raise_user_already_blocked_exception(cls, *args, **kwargs):
	raise UserlAlreadyBlockedException

#########################################################

def test_cant_delete_user_request_doesnt_come_from_admin_user(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = False

		hed = {'authorization': 'FAKETOKEN'}

		response = client.delete('/api/users/' + user_email, headers=hed, follow_redirects=False)

		value_expected = {'Error' : 'Request doesnt come from admin user'}

		assert mock.called
		assert json.loads(response.data) == value_expected

def test_cant_delete_user_because_doesnt_exist(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = True

		with patch.object(UserPersistence,'block_user', new=raise_user_not_found_exception) as block_user_mock:

			hed = {'authorization': 'TOKEN'}

			response = client.delete('/api/users/' + user_email, headers=hed, follow_redirects=False)

			value_expected = {'Error' : 'User {0} doesnt exist'.format(user_email)}

			assert mock.called
			assert json.loads(response.data) == value_expected

def test_cant_delete_user_already_deleted(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = True

		with patch.object(UserPersistence,'block_user', new=raise_user_already_blocked_exception) as block_user_mock:

			hed = {'authorization': 'TOKEN'}

			response = client.delete('/api/users/' + user_email, headers=hed, follow_redirects=False)

			value_expected = {'Error' : 'User {0} was already deleted'.format(user_email)}

			assert mock.called
			assert json.loads(response.data) == value_expected

def test_cant_delete_user_app_server_fails(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = True

		with patch.object(UserPersistence,'block_user') as user_persistence:

			with patch.object(requests,'delete') as delete_mock:

				delete_mock.return_value.status_code = 500

				hed = {'authorization': 'TOKEN'}

				response = client.delete('/api/users/' + user_email, headers=hed, follow_redirects=False)

				value_expected = {'Error' : 'Couldnt delete user {0} in app server'.format(user_email)}

				assert mock.called
				assert user_persistence.called
				assert json.loads(response.data) == value_expected

def test_delete_user_successfully(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = True

		with patch.object(UserPersistence,'block_user') as user_persistence:

			with patch.object(requests,'delete') as delete_mock:

				delete_mock.return_value.status_code = 200

				hed = {'authorization': 'TOKEN'}

				response = client.delete('/api/users/' + user_email, headers=hed, follow_redirects=False)

				value_expected = {'Delete':'successfully deleted user with email {0}'.format(user_email)}

				assert mock.called
				assert user_persistence.called
				assert json.loads(response.data) == value_expected

def test_cant_modify_user_request_doesnt_come_from_admin_user(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = False

		hed = {'authorization': 'FAKETOKEN'}

		response = client.put('/api/users/' + user_email, headers=hed, follow_redirects=False)

		value_expected = {'Error' : 'Request doesnt come from admin user'}

		assert mock.called
		assert json.loads(response.data) == value_expected

def test_modify_user_successfully(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = True

		with patch('auth_server.users.modify_user_from_db') as mock_modify_user:

			hed = {'authorization': 'TOKEN'}

			user_information = {'email': 'test@test.com',
				'password': 'fake password',
				'full name': 'full name',
				'phone number': 'phone number', 'profile picture': 'profile picture'}

			mock_modify_user.return_value = {'Modify':'successfully modified user with email {0}'.format(user_email)}, 200

			response = client.put('/api/users/' + user_email, json=user_information, headers=hed, follow_redirects=False)

			value_expected = {'Modify':'successfully modified user with email {0}'.format(user_email)}

			assert mock.called
			assert mock_modify_user.called
			assert json.loads(response.data) == value_expected

def test_cant_get_users_request_doesnt_come_from_admin_user(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = False

		hed = {'authorization': 'FAKETOKEN'}

		response = client.get('/api/users/', headers=hed, follow_redirects=False)

		value_expected = {'Error' : 'Request doesnt come from admin user'}

		assert mock.called
		assert json.loads(response.data) == value_expected

def test_cant_get_users_problem_with_db(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = True

		with pytest.raises(Exception) as error_received:

			hed = {'authorization': 'TOKEN'}

			response = client.get('/api/users/', headers=hed, follow_redirects=False)

			value_expected =  {'Error' : str(error_received)}

			assert mock.called
			assert json.loads(response.data) == value_expected

def test_get_users_successfully(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = True

		with patch('auth_server.users.get_all_users') as mock_get_all_users:

			hed = {'authorization': 'TOKEN'}

			users =json.dumps([
				{
					'email': 'test@test.com',
					'full name': 'full name',
					'phone number': 'phone number',
					'profile picture': 'profile picture'
				},
				{
					'email': 'test@test.com',
					'full name': 'full name',
					'phone number': 'phone number',
					'profile picture': 'profile picture'
				}])

			mock_get_all_users.return_value = users

			response = client.get('/api/users/', headers=hed, follow_redirects=False)

			value_expected = users

			assert mock.called
			assert mock_get_all_users.called
			assert json.loads(response.data) == json.loads(value_expected)

def test_cant_get_user_profile_app_server_token_not_provided(client):

	user_email = 'test@test.com'
	hed = {}

	response = client.get('/api/users/' + user_email, headers=hed, follow_redirects=False)

	value_expected = {'Error' : 'Missing app server token (AppServerToken)'}
	assert json.loads(response.data) == value_expected

def test_cant_get_user_profile_invalid_app_server_token(client):
	with patch('auth_server.decorators.app_server_token_required_decorator.is_valid_token_from_app_server') as mock:

		user_email = 'test@test.com'

		mock.return_value = False

		hed = {'AppServerToken': 'FAKETOKEN'}

		response = client.get('/api/users/' + user_email, headers=hed, follow_redirects=False)

		value_expected = {'Error' : 'App server token NOT valid'}

		assert mock.called
		assert json.loads(response.data) == value_expected

def test_cant_get_user_profile_because_user_doesnt_exist(client):
	with patch('auth_server.decorators.app_server_token_required_decorator.is_valid_token_from_app_server') as mock:

		mock.return_value = True

		with patch.object(UserPersistence,'get_user_by_email', new=raise_user_not_found_exception) as get_user_mock:

			user_email = 'test@test.com'
			hed = {'AppServerToken': 'FAKETOKEN'}

			response = client.get('/api/users/' + user_email, headers=hed, follow_redirects=False)

			value_expected = {'Error' : 'user {0} doesnt exist'.format(user_email)}

			assert mock.called
			assert json.loads(response.data) == value_expected

def test_get_user_profile_successfully(client):
	with patch('auth_server.decorators.app_server_token_required_decorator.is_valid_token_from_app_server') as mock:

		mock.return_value = True

		with patch.object(UserPersistence,'get_user_by_email') as get_user_mock:

			get_user_mock.return_value = User('test@test.com', 'secreto', 'Test', '1234', 'test.jpg', False, False, False)

			user_email = 'test@test.com'
			hed = {'AppServerToken': 'FAKETOKEN'}

			response = client.get('/api/users/' + user_email, headers=hed, follow_redirects=False)

			value_expected = {'email': 'test@test.com',
								'full_name': 'Test',
								'phone_number': '1234',
								'profile_picture' : 'test.jpg'}

			assert mock.called
			assert json.loads(response.data) == value_expected

