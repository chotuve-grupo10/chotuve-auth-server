from auth_server.model.user import User

def test_is_firebase():
  user_firebase = User('aa@gmail.com', 'pa$$word', 'John Doe', '1111', 'NULL', True, False)
  user_not_firebase = User('aa@gmail.com', 'pa$$word', 'John Doe', '1111', 'NULL', False, False)
  assert user_firebase.is_firebase_user()
  assert not user_not_firebase.is_firebase_user()

def test_is_not_admin_user():
  user = User('aa@gmail.com', 'pa$$word', 'John Doe', '1111', 'NULL', True, False)
  assert not user.is_admin_user()

def test_is_admin_user():
  user = User('aa@gmail.com', 'pa$$word', 'John Doe', '1111', 'NULL', False, True)
  assert user.is_admin_user()