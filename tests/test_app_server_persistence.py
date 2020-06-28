import datetime
import db.migrations
import pytest
from auth_server.model.app_server import AppServer
from auth_server.persistence.app_server_persistence import AppServerPersistence
from auth_server.exceptions.app_server_not_found_exception import AppServerNotFoundException

def create_appservers_table(conn):
    migrations = db.migrations.all_migrations()
    conn.execute(migrations[1])

def query_first_app_server(conn):
    return conn.execute("SELECT * FROM appservers").fetchone()

def test_save_app_server_successfully(postgresql_db):
    session = postgresql_db.session
    create_appservers_table(session)
    assert query_first_app_server(session) is None

    app_server_to_save = AppServer()
    sut = AppServerPersistence(postgresql_db)
    sut.save(app_server_to_save)
    row = query_first_app_server(session)
    assert row is not None
    assert row[1].month == datetime.datetime.now().month

def test_app_server_with_given_token_not_found(postgresql_db):
    session = postgresql_db.session
    create_appservers_table(session)
    sut = AppServerPersistence(postgresql_db)
    with pytest.raises(AppServerNotFoundException):
        user = sut.get_app_server_by_token('5a3d6026-2f5c-4957-b52d-c094b50774db')

def test_get_app_server_by_token_successfully(postgresql_db):
    session = postgresql_db.session
    create_appservers_table(session)
    assert query_first_app_server(session) is None

    app_server_to_save = AppServer()
    sut = AppServerPersistence(postgresql_db)
    sut.save(app_server_to_save)
    row = query_first_app_server(session)
    assert row is not None
    assert row[1].month == datetime.datetime.now().month

    assert sut.get_app_server_by_token(app_server_to_save.get_token()) is not None

def test_delete_app_server_successfully(postgresql_db):
    session = postgresql_db.session
    create_appservers_table(session)
    assert query_first_app_server(session) is None

    app_server_to_save = AppServer()
    sut = AppServerPersistence(postgresql_db)
    sut.save(app_server_to_save)
    row = query_first_app_server(session)
    assert row is not None
    assert row[1].month == datetime.datetime.now().month

    sut.delete(app_server_to_save.get_token())
    assert query_first_app_server(session) is None

def test_cant_delete_app_server_with_given_token_not_found(postgresql_db):
    session = postgresql_db.session
    create_appservers_table(session)
    sut = AppServerPersistence(postgresql_db)
    with pytest.raises(AppServerNotFoundException):
        user = sut.delete('5a3d6026-2f5c-4957-b52d-c094b50774db')

def test_get_all_app_servers_successfully(postgresql_db):
    session = postgresql_db.session
    create_appservers_table(session)
    assert query_first_app_server(session) is None

    app_server_to_save = AppServer()
    sut = AppServerPersistence(postgresql_db)
    sut.save(app_server_to_save)
    row = query_first_app_server(session)
    assert row is not None
    assert row[1].month == datetime.datetime.now().month

    app_server_to_save_2 = AppServer()
    sut = AppServerPersistence(postgresql_db)
    sut.save(app_server_to_save_2)
    row = query_first_app_server(session)
    assert row is not None

    app_servers_received = sut.get_all_app_servers()
    assert app_servers_received.length == 2
