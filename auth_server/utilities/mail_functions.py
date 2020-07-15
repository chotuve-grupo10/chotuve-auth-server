from flask_mail import Mail, Message
mail = Mail()

def send_email_with_reset_password_token(user_email, token):
	msg = Message("Cambiar contraseña",
						recipients=[user_email],
						body='Hola, este es tu codigo:{0}'.format(token))
	mail.send(msg)