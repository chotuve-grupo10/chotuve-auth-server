from auth_server.model.app_server import AppServer

def test_create_app_server_successfully():
  app_server = AppServer()
  assert app_server is not None

def test_app_server_returns_token_successfully():
  app_server = AppServer()
  assert app_server.get_token() is not None

def test_serialize_app_server_successfully():
  app_server = AppServer()
  app_server_serialized = app_server.serialize()

  app_server_serialized['token'] = app_server.get_token