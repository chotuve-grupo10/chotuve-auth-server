import datetime
import db.migrations
import pytest
from auth_server.model.app_server import AppServer
from auth_server.persistence.app_server_persistence import AppServerPersistence

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
