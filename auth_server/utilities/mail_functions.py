from flask_mail import Mail, Message
mail = Mail()

def send_email_with_reset_password_token(user_email, token):
	msg = Message("Solicitud de cambio de contraseña",
						recipients=[user_email],
						body='Hola! Este es tu codigo: {0}'.format(token))
	mail.send(msg)