import auth_server.validation_functions
import auth_server.token_functions
from unittest.mock import patch
from auth_server.persistence.app_server_persistence import AppServerPersistence
from auth_server.model.app_server import AppServer

def test_valid_firebase_user():

    user = ['test@mail.com', 'test', 'phone', 'picture', 'hash', 'salt', '1', '0']

    assert auth_server.validation_functions.validate_firebase_user(user)

def test_invalid_firebase_user():

    user = ['test@mail.com', 'test', 'phone', 'picture', 'hash', 'salt', '0', '0']

    assert not auth_server.validation_functions.validate_firebase_user(user)

def test_firebase_user_cant_be_admin():

    user = ['test@mail.com', 'test', 'phone', 'picture', 'hash', 'salt', '1', '1']

    assert not auth_server.validation_functions.validate_admin_user(user)

def test_invalid_admin_user():

    user = ['test@mail.com', 'test', 'phone', 'picture', 'hash', 'salt', '0', '0']

    assert not auth_server.validation_functions.validate_admin_user(user)

def test_valid_admin_user():

    user = ['test@mail.com', 'test', 'phone', 'picture', 'hash', 'salt', '0', '1']

    assert auth_server.validation_functions.validate_admin_user(user)

def test_isnt_valid_request_from_admin_user_token_is_invalid():

    invalid_token = 'INVALIDTOKEN'

    assert not auth_server.validation_functions.is_request_from_admin_user(invalid_token)

def test_isnt_valid_request_from_admin_user_cant_get_user_from_token():

    token = 'INVALIDTOKEN'

    with patch('auth_server.validation_functions.validate_token') as mock_validate_token:

        mock_validate_token.return_value = {'Test':'test'}, 200

        response = auth_server.validation_functions.is_request_from_admin_user(token)

        assert mock_validate_token.called
        assert not response

def test_is_blocked_user():

    user = ['test@mail.com', 'test', 'phone', 'picture', 'hash', 'salt', '0', '1', '1']

    assert auth_server.validation_functions.is_blocked_user(user)

def test_is_not_blocked_user():

    user = ['test@mail.com', 'test', 'phone', 'picture', 'hash', 'salt', '0', '1', '0']

    assert not auth_server.validation_functions.is_blocked_user(user)
