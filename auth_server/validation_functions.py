import hashlib

ADMIN_FLAG_POSITION = 7

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


def validate_admin_user(user):
	# Si se registro con firebase no puede ser admin.
	if (validate_firebase_user):
		return False
	admin_user = user[ADMIN_FLAG_POSITION]
	return admin_user == '1'
