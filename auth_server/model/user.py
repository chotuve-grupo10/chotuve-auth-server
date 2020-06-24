import hashlib
from auth_server.random_string import *
from sqlalchemy import Column, Integer, String
from auth_server.model.base import Base

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

  def __init__(self, email, password, full_name, phone_number, profile_picture, \
      is_firebase_user, is_admin_user):
    sal = random_string(6)
    pimienta = random_string(1)
    self.email = email
    self.full_name = full_name
    self.phone_number = phone_number
    self.profile_picture = profile_picture
    self.hash = hashlib.sha512((password + sal + pimienta).encode('utf-8')).hexdigest()
    self.salt = sal
    self.firebase_user = 1 if is_firebase_user else 0
    self.admin_user = 1 if is_admin_user else 0
    

