from auth_server.model.user import User

def parse_regular_user(body):
  email = body['email']
  full_name = body['full name']
  phone_number = body['phone number']
  profile_picture = body['profile picture']
  password = body['password']
  return User(email, password, full_name, phone_number, profile_picture, False, False)