import requests
import pytest
from unittest.mock import patch
import simplejson as json
from auth_server.persistence.user_persistence import UserPersistence
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

			value_expected = {'Delete' : 'User {0} doesnt exist'.format(user_email)}

			assert mock.called
			assert json.loads(response.data) == value_expected

def test_cant_delete_user_already_deleted(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		user_email = 'test@test.com'

		mock.return_value = True

		with patch.object(UserPersistence,'block_user', new=raise_user_already_blocked_exception) as block_user_mock:

			hed = {'authorization': 'TOKEN'}

			response = client.delete('/api/users/' + user_email, headers=hed, follow_redirects=False)

			value_expected = {'Delete' : 'User {0} was already deleted'.format(user_email)}

			assert mock.called
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
