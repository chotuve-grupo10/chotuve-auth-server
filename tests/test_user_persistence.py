import db.migrations
import pytest
from auth_server.exceptions.user_already_registered_exception import UserAlreadyRegisteredException
from auth_server.exceptions.user_not_found_exception import UserNotFoundException
from auth_server.model.user import User
from auth_server.persistence.user_persistence import UserPersistence

def test_save_password_user(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  assert query_first_user(session) is None
  user_to_save = User('aa@gmail.com', 'aaa', 'John Doe', '555-5555', None, False, False, False)
  sut = UserPersistence(postgresql_db)
  sut.save(user_to_save)
  row = query_first_user(session)
  assert row is not None
  assert row[0] == 'aa@gmail.com'
  assert row[1] == 'John Doe'
  assert row[2] == '555-5555'

def test_save_existent_user(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  saved_user = User('aa@gmail.com', 'bbb', 'Jane Doe', '111-1111', None, False, False, False)
  sut = UserPersistence(postgresql_db)
  sut.save(saved_user)
  with pytest.raises(UserAlreadyRegisteredException):
    user_to_save = User('aa@gmail.com', 'aaa', 'John Doe', '555-5555', None, False, False, False)
    sut.save(user_to_save)

def test_retrieve_existent_user(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  insert_test_user(session)
  sut = UserPersistence(postgresql_db)
  user = sut.get_user_by_email('test@test.com')
  assert user.email == 'test@test.com'
  assert user.full_name == 'Test User'
  assert user.phone_number == '444-4444'
#  assert user.is_admin() == False
#  assert user.is_firebase_user() == False

def test_retrieve_inexistent_user(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  sut = UserPersistence(postgresql_db)
  with pytest.raises(UserNotFoundException):
    user = sut.get_user_by_email('aa@gmail.com')

def create_all(conn):
  migrations = db.migrations.all_migrations()
  for migration in migrations:
    conn.execute(migration)

def query_first_user(conn):
    return conn.execute("SELECT email, full_name, phone_number FROM users").fetchone()

def insert_test_user(conn):
    conn.execute("""INSERT INTO users (email, full_name, phone_number, profile_picture,
						hash, salt, firebase_user, admin_user, blocked_user) VALUES ('test@test.com', 'Test User',
            '444-4444', null, 'xxxxx', 'xxxxx', '0', '0', '0')""")
