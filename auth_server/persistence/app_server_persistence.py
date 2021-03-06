from auth_server.exceptions.app_server_not_found_exception import AppServerNotFoundException
from auth_server.model.app_server import AppServer

class AppServerPersistence():
  def __init__(self, db_connection):
    self.db = db_connection

  def save(self, app_server):
    self.db.session.add(app_server)
    self.db.session.commit()

  def get_app_server_by_token(self, token):
    app_server = self.db.session.query(AppServer).get(token)
    if app_server is None:
      raise AppServerNotFoundException
    return app_server

  def get_all_app_servers(self):
    return self.db.session.query(AppServer).all()

  def delete(self, token):
    app_server = self.db.session.query(AppServer).get(token)
    if app_server is None:
      raise AppServerNotFoundException
    else:
      self.db.session.delete(app_server)
      self.db.session.commit()