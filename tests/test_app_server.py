from auth_server.model.app_server import AppServer

def test_create_app_server_successfully():
  app_server = AppServer()
  assert app_server is not None