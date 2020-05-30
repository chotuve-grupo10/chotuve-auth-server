import auth_server.token_functions

def test_valid_token():
    user_email = 'test@test.com'

    generated_token = auth_server.token_functions.generate_auth_token(user_email)
    result, status_code = auth_server.token_functions.validate_token(generated_token)

    assert status_code == 200
    assert result == {'Message': 'token valido para user {0}'.format(user_email)}

def test_invalid_token():
    invalid_token = 'test123test123'

    result, status_code = auth_server.token_functions.validate_token(invalid_token)

    assert status_code == 401
    assert result == {'Message': 'invalid token'}