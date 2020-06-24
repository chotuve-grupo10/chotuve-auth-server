from auth_server.exceptions.user_already_registered_exception import UserAlreadyRegisteredException
from auth_server.model.user import User

class UserPersistence():
  def __init__(self, db_connection):
    self.db = db_connection
  
  def save(self, user):
    if self.db.query(User).get(user.email) is not None:
      raise UserAlreadyRegisteredException
    self.db.add(user)
    self.db.commit()