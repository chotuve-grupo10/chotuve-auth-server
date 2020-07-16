import pytest
from auth_server.model.user import User
from auth_server.exceptions.cant_change_password_for_firebase_user_exception import CantChangePasswordForFirebaseUser

def test_is_firebase():
	user_firebase = User('aa@gmail.com', 'pa$$word', 'John Doe', '1111', 'NULL', True, False, False)
	user_not_firebase = User('aa@gmail.com', 'pa$$word', 'John Doe', '1111', 'NULL', False, False, False)
	assert user_firebase.is_firebase_user()
	assert not user_not_firebase.is_firebase_user()

def test_is_not_admin_user():
	user = User('aa@gmail.com', 'pa$$word', 'John Doe', '1111', 'NULL', True, False, False)
	assert not user.is_admin_user()

def test_is_admin_user():
	user = User('aa@gmail.com', 'pa$$word', 'John Doe', '1111', 'NULL', False, True, False)
	assert user.is_admin_user()

def test_is_not_blocked_user():
	user = User('aa@gmail.com', 'pa$$word', 'John Doe', '1111', 'NULL', True, False, False)
	assert not user.is_blocked_user()

def test_is_blocked_user():
	user = User('aa@gmail.com', 'pa$$word', 'John Doe', '1111', 'NULL', False, True, True)
	assert user.is_blocked_user()

def test_cant_change_password_for_firebase_user():
	user = User('aa@gmail.com', 'pa$$word', 'John Doe', '1111', 'NULL', True, True, True)
	old_hash = user.hash

	with pytest.raises(CantChangePasswordForFirebaseUser):
		user.change_password('password')

def test_change_password_successfully():
	user = User('aa@gmail.com', 'pa$$word', 'John Doe', '1111', 'NULL', False, True, True)
	old_hash = user.hash

	user.change_password('password')

	assert not user.hash == old_hash