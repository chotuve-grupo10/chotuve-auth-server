import hashlib

def validar_usuario(user, password):
	hashed = user[4]
	salt = user[5]
	for i in range(256):
		pimienta = chr(i)
		if hashlib.sha512((password+salt+pimienta).encode('utf-8')).hexdigest() == hashed:
			return True
	return False


def validate_firebase_user(user):
	firebase_user = user[6]
	return firebase_user == '1'
