import db.migrations
import pytest
from auth_server.exceptions.user_already_registered_exception import UserAlreadyRegisteredException
from auth_server.model.user import User
from auth_server.persistence.user_persistence import UserPersistence

def test_save_password_user(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  assert query_first_user(session) is None
  user_to_save = User('aa@gmail.com', 'aaa', 'John Doe', '555-5555', None, False, False)
  sut = UserPersistence(session)
  sut.save(user_to_save)
  row = query_first_user(session)
  assert row is not None
  assert row[0] == 'aa@gmail.com'
  assert row[1] == 'John Doe'
  assert row[2] == '555-5555'

def test_save_existent_user(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  saved_user = User('aa@gmail.com', 'bbb', 'Jane Doe', '111-1111', None, False, False)
  sut = UserPersistence(session)
  sut.save(saved_user)
  with pytest.raises(UserAlreadyRegisteredException):
    user_to_save = User('aa@gmail.com', 'aaa', 'John Doe', '555-5555', None, False, False)
    sut.save(user_to_save)


def create_all(conn):
  migrations = db.migrations.all_migrations()
  for migration in migrations:
    conn.execute(migration)

def query_first_user(conn):
    return conn.execute("SELECT email, full_name, phone_number FROM users").fetchone()
    
