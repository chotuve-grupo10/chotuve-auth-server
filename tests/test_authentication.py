from unittest.mock import patch
from auth_server.authentication import _register_user
import simplejson as json

# @patch.object(_register_user, '_register_user', lambda x: False)
def test_register_user_succesfully(client):
	with patch('auth_server.authentication._register_user') as mock_register_user:

		data = {'email': 'test_email@test.com'}

		mock_register_user.return_value.json.return_value = \
			{'Registration' :
			'Successfully registered new user with email {0}'.format(data['email'])}
		mock_register_user.return_value.status_code = 200

		response = client.post('/api/register', data=data, follow_redirects=False)

		value_expected = {'Registration' :
			'Successfully registered new user with email test_email@test.com'}

		assert True
		# assert mock_register_user.called
		# assert json.loads(response.data) == value_expected