from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

def generate_auth_token(user_data, expiration = 1000):
	s = Serializer(user_data['password'], expires_in = expiration)
	return s.dumps({ 'id': user_data['email'] })

# def verify_auth_token(token):
# 	s = Serializer(app.config['SECRET_KEY'])
# 	try:
# 		data = s.loads(token)
# 	except SignatureExpired:
# 		return 'Token Expired'
# 	except BadSignature:
# 		return 'Bad Token'
