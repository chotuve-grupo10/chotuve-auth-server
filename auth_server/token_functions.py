import logging
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from datetime import datetime, timedelta
import jwt

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'

logger = logging.getLogger('gunicorn.error')

def generate_auth_token(user_data, expiration = 1000):
	s = Serializer(user_data['password'], expires_in = expiration)
	return s.dumps({ 'id': user_data['email'] })

def generate_auth_token2(user_data, expiration = 1000):
	payload = {
        'user_id': user_data['email'],
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
		except (jwt.DecodeError):
			result = {'Message': 'invalid token'}
			status_code = 401
		except (jwt.ExpiredSignatureError):
			result = {'Message': 'expired token'}
			status_code = 401
	
	return result, status_code

# def verify_auth_token(token):
# 	s = Serializer(app.config['SECRET_KEY'])
# 	try:
# 		data = s.loads(token)
# 	except SignatureExpired:
# 		return 'Token Expired'
# 	except BadSignature:
# 		return 'Bad Token'
