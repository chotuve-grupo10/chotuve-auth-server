import datetime
import db.migrations
import pytest
from auth_server.model.reset_password import ResetPassword
from auth_server.persistence.reset_password_persistence import ResetPasswordPersistence
from auth_server.exceptions.reset_password_not_found_exception import ResetPasswordNotFoundException

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

# def test_app_server_with_given_token_not_found(postgresql_db):
#     session = postgresql_db.session
#     create_appservers_table(session)
#     sut = AppServerPersistence(postgresql_db)
#     with pytest.raises(AppServerNotFoundException):
#         user = sut.get_app_server_by_token('5a3d6026-2f5c-4957-b52d-c094b50774db')

# def test_get_app_server_by_token_successfully(postgresql_db):
#     session = postgresql_db.session
#     create_appservers_table(session)
#     assert query_first_app_server(session) is None

#     app_server_to_save = AppServer()
#     sut = AppServerPersistence(postgresql_db)
#     sut.save(app_server_to_save)
#     row = query_first_app_server(session)
#     assert row is not None
#     assert row[1].month == datetime.datetime.now().month

#     assert sut.get_app_server_by_token(app_server_to_save.get_token()) is not None

# def test_delete_app_server_successfully(postgresql_db):
#     session = postgresql_db.session
#     create_appservers_table(session)
#     assert query_first_app_server(session) is None

#     app_server_to_save = AppServer()
#     sut = AppServerPersistence(postgresql_db)
#     sut.save(app_server_to_save)
#     row = query_first_app_server(session)
#     assert row is not None
#     assert row[1].month == datetime.datetime.now().month

#     sut.delete(app_server_to_save.get_token())
#     assert query_first_app_server(session) is None

# def test_cant_delete_app_server_with_given_token_not_found(postgresql_db):
#     session = postgresql_db.session
#     create_appservers_table(session)
#     sut = AppServerPersistence(postgresql_db)
#     with pytest.raises(AppServerNotFoundException):
#         user = sut.delete('5a3d6026-2f5c-4957-b52d-c094b50774db')

# def test_get_all_app_servers_successfully(postgresql_db):
#     session = postgresql_db.session
#     create_appservers_table(session)
#     assert query_first_app_server(session) is None

#     app_server_to_save = AppServer()
#     sut = AppServerPersistence(postgresql_db)
#     sut.save(app_server_to_save)
#     row = query_first_app_server(session)
#     assert row is not None
#     assert row[1].month == datetime.datetime.now().month

#     app_server_to_save_2 = AppServer()
#     sut = AppServerPersistence(postgresql_db)
#     sut.save(app_server_to_save_2)
#     row = query_first_app_server(session)
#     assert row is not None

#     app_servers_received = sut.get_all_app_servers()
#     assert len(app_servers_received) == 2
