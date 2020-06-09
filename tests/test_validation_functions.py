import auth_server.validation_functions

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