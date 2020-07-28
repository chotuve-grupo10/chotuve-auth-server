from auth_server.model.reset_password import ResetPassword

def test_create_reset_password_successfully():

  reset_password = ResetPassword('test@test.com')

  assert reset_password is not None

def test_token_is_not_expired():

  reset_password = ResetPassword('test@test.com')

  assert not reset_password.is_token_expired()
