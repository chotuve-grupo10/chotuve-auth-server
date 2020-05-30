import auth_server.validation_functions

def test_valid_firebase_user():

    user = ['test@mail.com', 'test', 'phone', 'picture', 'hash', 'salt', '1', '0']

    assert auth_server.validation_functions.validate_firebase_user(user)

def test_invalid_firebase_user():

    user = ['test@mail.com', 'test', 'phone', 'picture', 'hash', 'salt', '0', '0']

    assert not auth_server.validation_functions.validate_firebase_user(user)
