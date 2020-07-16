import datetime
import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from auth_server.model.base import Base
from auth_server.model.user import User
from auth_server.random_string import id_generator

EXPIRATION_MINUTES = 30

class ResetPassword(Base):
	__tablename__ = 'resetpassword'

	token = Column(String)
	email = Column(String, ForeignKey(User.email), primary_key=True)
	registered_at = Column(DateTime)

	def __init__(self, email):
		self.token = id_generator()
		self.email = email
		self.registered_at = datetime.datetime.now()

	def is_token_expired(self):
		time_difference = datetime.datetime.now() - self.registered_at
		time_difference_in_minutes = int(round(time_difference.total_seconds() / 60))
		return time_difference_in_minutes > EXPIRATION_MINUTES

	def __repr__(self):
		return """<token={0} email={1} registered_at={2} """.format(self.token, self.email, self.registered_at)
