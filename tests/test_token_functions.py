import pytest
import auth_server.token_functions
from auth_server.model.user import User

def test_valid_token():
	user = User('test@test.com', 'fake_falopa', 'John Doe', '1111', 'NULL', True, False)

	generated_token = auth_server.token_functions.generate_auth_token(user)
	result, status_code = auth_server.token_functions.validate_token(generated_token)

	assert status_code == 200
	assert result == {'Message': 'token valido para user {0}'.format(user.email)}

def test_invalid_token():
	invalid_token = 'test123test123'

	result, status_code = auth_server.token_functions.validate_token(invalid_token)

	assert status_code == 401
	assert result == {'Message': 'invalid token'}

def test_returns_user_with_token_successfully():
	user = User('test@test.com', 'fake_falopa', 'John Doe', '1111', 'NULL', True, False)

	generated_token = auth_server.token_functions.generate_auth_token(user)
	user_obtained = auth_server.token_functions.get_user_with_token(generated_token)

	assert user_obtained == user.email

def test_returns_user_with_token_fails_invalid_token():
	with pytest.raises(ValueError) as error_received:

		invalid_token = 'invalid_token'

		user = auth_server.token_functions.get_user_with_token(invalid_token)

	assert str(error_received.value) == 'Cant decode token'
