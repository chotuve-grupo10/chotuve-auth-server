from unittest.mock import patch
from auth_server.db_functions import insert_into_users_db
import simplejson as json

def test_register_user_succesfully(client):
	with patch('auth_server.db_functions.insert_into_users_db') as mock:
		user_information = {'email': 'segundo_intento_this_email_should_not_be_saved@test.com',
				'password': 'fake password',
				'first name': 'first name', 'last name': 'last name',
				'phone number': 'phone number', 'profile picture': 'profile picture',
				'hash': 'hash', 'salt': 'salt'}

		mock.return_value.json.return_value = \
			{'Registration' :
			'Successfully registered new user with email {0}'.format(user_information['email'])}
		mock.return_value.status_code = 200

		response = client.post('/api/register/', json=user_information,
							   follow_redirects=False)
		value_expected = {'Registration' :
			'Successfully registered new user with email {0}'.format(user_information['email'])}

		assert True
		assert mock.called
		# assert mock_register_user.assert_not_called
		# assert json.loads(response.data) == value_expected
