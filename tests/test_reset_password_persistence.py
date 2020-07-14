import datetime
import db.migrations
import pytest
import psycopg2
from auth_server.model.reset_password import ResetPassword
from auth_server.persistence.reset_password_persistence import ResetPasswordPersistence
from auth_server.exceptions.reset_password_not_found_exception import ResetPasswordNotFoundException
from auth_server.exceptions.reset_password_for_non_existent_user_exception import ResetPasswordForNonExistentUserException

def create_reset_password_table(conn):
    migrations = db.migrations.all_migrations()
    conn.execute(migrations[0])
    conn.execute("""INSERT INTO users (email, full_name, phone_number, profile_picture,
						hash, salt, firebase_user, admin_user, blocked_user) VALUES ('test@test.com', 'Test User',
            '444-4444', null, 'xxxxx', 'xxxxx', '0', '0', '0')""")
    conn.execute(migrations[2])

def query_first_reset_password(conn):
    return conn.execute("SELECT * FROM resetpassword").fetchone()

######## TESTS #########

def test_save_reset_password_successfully(postgresql_db):
    session = postgresql_db.session
    create_reset_password_table(session)
    assert query_first_reset_password(session) is None

    email = 'test@test.com'

    reset_password_to_save = ResetPassword(email)
    sut = ResetPasswordPersistence(postgresql_db)
    sut.save(reset_password_to_save)
    row = query_first_reset_password(session)
    assert row is not None
    assert row[1] == email

def test_save_reset_password_fails_user_doesnt_exist(postgresql_db):
    session = postgresql_db.session
    create_reset_password_table(session)
    assert query_first_reset_password(session) is None

    email = 'hola@hola.com'

    reset_password_to_save = ResetPassword(email)
    sut = ResetPasswordPersistence(postgresql_db)
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        sut.save(reset_password_to_save)


def test_reset_password_with_given_email_not_found(postgresql_db):
    session = postgresql_db.session
    create_reset_password_table(session)
    sut = ResetPasswordPersistence(postgresql_db)
    with pytest.raises(ResetPasswordNotFoundException):
        user = sut.get_reset_password_by_email('hola@hola.com')

def test_get_reset_password_by_email_successfully(postgresql_db):
    session = postgresql_db.session
    create_reset_password_table(session)
    assert query_first_reset_password(session) is None

    email = 'test@test.com'

    reset_password_to_save = ResetPassword(email)
    sut = ResetPasswordPersistence(postgresql_db)
    sut.save(reset_password_to_save)

    reset_password_obtained = email = 'test@test.com'
    assert reset_password_obtained is not None

def test_delete_reset_password_successfully(postgresql_db):
    session = postgresql_db.session
    create_reset_password_table(session)
    assert query_first_reset_password(session) is None

    email = 'test@test.com'

    reset_password_to_save = ResetPassword(email)
    sut = ResetPasswordPersistence(postgresql_db)
    sut.save(reset_password_to_save)
    row = query_first_reset_password(session)
    assert row is not None
    assert row[1] == email

    sut.delete(email)
    assert query_first_reset_password(session) is None

def test_cant_delete_reset_password_with_given_email_not_found(postgresql_db):
    session = postgresql_db.session
    create_reset_password_table(session)
    sut = ResetPasswordPersistence(postgresql_db)
    with pytest.raises(ResetPasswordNotFoundException):
        user = sut.delete('test@test.com')
