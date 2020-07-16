import db.migrations
import pytest
from auth_server.exceptions.user_already_registered_exception import UserAlreadyRegisteredException
from auth_server.exceptions.user_not_found_exception import UserNotFoundException
from auth_server.exceptions.user_already_blocked_exception import UserlAlreadyBlockedException
from auth_server.exceptions.user_already_unblocked_exception import UserlAlreadyUnblockedException
from auth_server.model.user import User
from auth_server.persistence.user_persistence import UserPersistence
from auth_server.exceptions.cant_change_password_for_firebase_user_exception import CantChangePasswordForFirebaseUser

####### FUNCS ########
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

def insert_firebase_test_user(conn):
    conn.execute("""INSERT INTO users (email, full_name, phone_number, profile_picture,
						hash, salt, firebase_user, admin_user, blocked_user) VALUES ('test@test.com', 'Test User',
            '444-4444', null, 'xxxxx', 'xxxxx', '1', '0', '0')""")

############ TESTS ##############

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

def test_block_existent_user_successfully(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  insert_test_user(session)
  sut = UserPersistence(postgresql_db)
  user = sut.get_user_by_email('test@test.com')
  assert user.email == 'test@test.com'
  assert user.full_name == 'Test User'
  assert user.phone_number == '444-4444'
  assert user.blocked_user == '0'

  sut.block_user('test@test.com')
  user = sut.get_user_by_email('test@test.com')
  assert user.email == 'test@test.com'
  assert user.blocked_user == '1'

def test_cant_block_user_because_doesnt_exist(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  insert_test_user(session)
  sut = UserPersistence(postgresql_db)
  user = sut.get_user_by_email('test@test.com')
  assert user.email == 'test@test.com'

  with pytest.raises(UserNotFoundException):
    sut.block_user('testing@test.com')

def test_cant_block_user_because_user_is_already_blocked(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  insert_test_user(session)
  sut = UserPersistence(postgresql_db)
  user = sut.get_user_by_email('test@test.com')
  assert user.email == 'test@test.com'
  sut.block_user('test@test.com')

  with pytest.raises(UserlAlreadyBlockedException):
    sut.block_user('test@test.com')

def test_unblock_existent_user_successfully(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  insert_test_user(session)
  sut = UserPersistence(postgresql_db)
  user = sut.get_user_by_email('test@test.com')
  assert user.email == 'test@test.com'
  assert user.full_name == 'Test User'
  assert user.phone_number == '444-4444'
  assert user.blocked_user == '0'
  sut.block_user('test@test.com')

  sut.unblock_user('test@test.com')
  user = sut.get_user_by_email('test@test.com')
  assert user.email == 'test@test.com'
  assert user.blocked_user == '0'

def test_cant_unblock_user_because_doesnt_exist(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  insert_test_user(session)
  sut = UserPersistence(postgresql_db)
  user = sut.get_user_by_email('test@test.com')
  assert user.email == 'test@test.com'

  with pytest.raises(UserNotFoundException):
    sut.unblock_user('testing@test.com')

def test_cant_unblock_user_because_user_is_already_unblocked(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  insert_test_user(session)
  sut = UserPersistence(postgresql_db)
  user = sut.get_user_by_email('test@test.com')
  assert user.email == 'test@test.com'
  sut.block_user('test@test.com')
  sut.unblock_user('test@test.com')

  with pytest.raises(UserlAlreadyUnblockedException):
    sut.unblock_user('test@test.com')

def test_retrieve_inexistent_user(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  sut = UserPersistence(postgresql_db)
  with pytest.raises(UserNotFoundException):
    user = sut.get_user_by_email('aa@gmail.com')

def test_cant_change_password_for_non_existent_user(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  insert_test_user(session)
  sut = UserPersistence(postgresql_db)
  user = sut.get_user_by_email('test@test.com')
  assert user.email == 'test@test.com'

  with pytest.raises(UserNotFoundException):
    sut.change_password_for_user('testing@test.com', 'password')

def test_cant_change_password_for_firebase_user(postgresql_db):
  session = postgresql_db.session
  create_all(session)
  insert_firebase_test_user(session)
  sut = UserPersistence(postgresql_db)
  user = sut.get_user_by_email('test@test.com')
  assert user.email == 'test@test.com'

  with pytest.raises(CantChangePasswordForFirebaseUser):
    sut.change_password_for_user('testg@test.com', 'password')
