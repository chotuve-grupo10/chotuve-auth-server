import logging
from datetime import datetime, timedelta
import jwt

# TODO: env var this!
JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'

logger = logging.getLogger('gunicorn.error')

def generate_auth_token(user_email, expiration=1000):
	payload = {
		'user_id': user_email,
		'exp': datetime.utcnow() + timedelta(seconds=expiration)
	}

	jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
	return jwt_token

def validate_token(token):
	if token:
		try:
			logger.debug("Token to decode")
			logger.debug(token)
			payload = jwt.decode(token, JWT_SECRET, algorithms='HS256')
			user = payload['user_id']
			result = {'Message': 'token valido para user {0}'.format(user)}
			status_code = 200
		except jwt.DecodeError:
			result = {'Message': 'invalid token'}
			status_code = 401
		except jwt.ExpiredSignatureError:
			result = {'Message': 'expired token'}
			status_code = 401
		return result, status_code
	else:
		logger.error('No token provided')
		return {'Error':'No token provided'}, 500


def get_user_with_token(token):
	if token:
		try:
			logger.debug("Token to decode")
			logger.debug(token)
			payload = jwt.decode(token, JWT_SECRET, algorithms='HS256')
			user = payload['user_id']
			return user
		except jwt.DecodeError:
			logger.error('Cant decode token')
			raise ValueError('Cant decode token')
		except jwt.ExpiredSignatureError:
			logger.error('Token expired')
			raise ValueError('This token is expired')
	else:
		logger.error('Error on token received')
		raise ValueError('Error on token received')
