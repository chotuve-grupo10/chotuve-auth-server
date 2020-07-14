from auth_server.model.reset_password import ResetPassword
from auth_server.exceptions.reset_password_not_found_exception import ResetPasswordNotFoundException

class ResetPasswordPersistence():
  def __init__(self, db_connection):
    self.db = db_connection

  def save(self, reset_password):
    self.db.session.add(reset_password)
    self.db.session.commit()

  def get_reset_password_by_email(self, email):
    reset_password = self.db.session.query(ResetPassword).get(email)
    if reset_password is None:
      raise ResetPasswordNotFoundException
    return reset_password

  def delete(self, email):
    reset_password = self.db.session.query(ResetPassword).get(email)
    if reset_password is None:
      raise ResetPasswordNotFoundException
    else:
      self.db.session.delete(reset_password)
      self.db.session.commit()