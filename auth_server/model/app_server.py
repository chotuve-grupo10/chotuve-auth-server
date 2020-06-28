import datetime
import uuid
from sqlalchemy import Column, Integer, String, DateTime
from auth_server.model.base import Base

class AppServer(Base):
  __tablename__ = 'appservers'

  token = Column(String, primary_key = True)
  registered_at = Column(DateTime)

  def __init__(self):
    self.token = str(uuid.uuid4())
    self.registered_at = datetime.datetime.now()

  def __repr__(self):
    return """<token={0} registered_at={1} """.format(self.token, self.registered_at)

  def get_token(self):
    return self.token

  def serialize(self):
    return {
      'token' : self.token,
      'registered_at' : self.registered_at
    }
