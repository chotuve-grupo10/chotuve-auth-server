import pytest
from http import HTTPStatus
from unittest.mock import patch
import simplejson as json
from auth_server.persistence.app_server_persistence import AppServerPersistence

def test_cant_register_app_server_request_doesnt_come_from_admin_user(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		mock.return_value = False

		hed = {'authorization': 'FAKETOKEN'}

		response = client.post('/api/app_servers/', headers=hed, follow_redirects=False)

		value_expected = {'Error' : 'Request doesnt come from admin user'}

		assert mock.called
		assert json.loads(response.data) == value_expected

def test_register_app_server_successfully(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		mock.return_value = True

		with patch.object(AppServerPersistence,'save') as mock_app_server_persistence:

			hed = {'authorization': 'FAKETOKEN'}

			response = client.post('/api/app_servers/', headers=hed, follow_redirects=False)

			assert mock.called
			assert mock_app_server_persistence.called
			assert response.status_code == HTTPStatus.CREATED

def test_cant_delete_app_server_request_doesnt_come_from_admin_user(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		mock.return_value = False

		hed = {'authorization': 'FAKETOKEN'}

		app_server_token = 'test'

		response = client.delete('/api/app_servers/' + app_server_token, headers=hed, follow_redirects=False)

		value_expected = {'Error' : 'Request doesnt come from admin user'}

		assert mock.called
		assert json.loads(response.data) == value_expected

def test_delete_app_server_successfully(client):
	with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock:

		mock.return_value = True

		with patch.object(AppServerPersistence,'delete') as mock_app_server_persistence:

			hed = {'authorization': 'FAKETOKEN'}

			app_server_token = 'test'

			response = client.delete('/api/app_servers/' + app_server_token, headers=hed, follow_redirects=False)

			value_expected = {'Delete app server' : 'deleted app server successfully'}

			assert mock.called
			assert mock_app_server_persistence.called
			assert json.loads(response.data) == value_expected
