import hashlib
from auth_server.random_string import *
from sqlalchemy import Column, Integer, String
from auth_server.model.base import Base
from auth_server.exceptions.cant_change_password_for_firebase_user_exception import CantChangePasswordForFirebaseUser

class User(Base):
  __tablename__ = 'users'

  email = Column(String, primary_key = True)
  full_name = Column(String)
  phone_number = Column(String)
  profile_picture = Column(String)
  hash = Column(String)
  salt = Column(String)
  firebase_user = Column(String)
  admin_user = Column(String)
  blocked_user = Column(String)

  def __init__(self, email, password, full_name, phone_number, profile_picture, \
      is_firebase_user, is_admin_user, is_blocked_user):
    sal = random_string(6)
    pimienta = random_string(1)
    self.email = email
    self.full_name = full_name
    self.phone_number = phone_number
    self.profile_picture = profile_picture
    self.hash = hashlib.sha512((password + sal + pimienta).encode('utf-8')).hexdigest() if password else 0
    self.salt = sal if password else 0
    self.firebase_user = '1' if is_firebase_user else '0'
    self.admin_user = '1' if is_admin_user else '0'
    self.blocked_user = '1' if is_blocked_user else '0'

  def is_firebase_user(self):
    return self.firebase_user == '1'

  def is_admin_user(self):
    return self.admin_user == '1'

  def is_blocked_user(self):
    return self.blocked_user == '1'

  def change_password(self, new_password):
    if self.is_firebase_user():
      raise CantChangePasswordForFirebaseUser

    sal = random_string(6)
    pimienta = random_string(1)
    self.hash = hashlib.sha512((new_password + sal + pimienta).encode('utf-8')).hexdigest()
    self.salt = sal

  def __repr__(self):
    return """<User email={0} full_name={1} phone_number={2} profile_picture={3}
        firebase={4} admin={5} blocked={6}""".format(self.email, self.full_name, self.phone_number,
        self.profile_picture, str(self.is_firebase_user()), self.admin_user, self.blocked_user)
