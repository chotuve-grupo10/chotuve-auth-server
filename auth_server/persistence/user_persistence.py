from auth_server.exceptions.user_already_registered_exception import UserAlreadyRegisteredException
from auth_server.exceptions.user_not_found_exception import UserNotFoundException
from auth_server.model.user import User

class UserPersistence():
  def __init__(self, db_connection):
    self.db = db_connection

  def save(self, user):
    if self.db.session.query(User).get(user.email) is not None:
      raise UserAlreadyRegisteredException
    self.db.session.add(user)
    self.db.session.commit()

  def get_user_by_email(self, email):
    user = self.db.session.query(User).get(email)
    if user is None:
      raise UserNotFoundException
    return user

  def block_user(self, email):
    user = self.db.session.query(User).get(email)
    if user is None:
      raise UserNotFoundException
    user.blocked_user = '1'
    self.db.session.commit()
