import psycopg2
from auth_server.model.reset_password import ResetPassword
from auth_server.exceptions.reset_password_not_found_exception import ResetPasswordNotFoundException
from auth_server.exceptions.reset_password_for_non_existent_user_exception import ResetPasswordForNonExistentUserExcpetion

class ResetPasswordPersistence():
  def __init__(self, db_connection):
    self.db = db_connection

  def save(self, reset_password):
    try:
        self.db.session.add(reset_password)
        self.db.session.commit()
    except psycopg2.errors.ForeignKeyViolation:
        ResetPasswordForNonExistentUserExcpetion

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