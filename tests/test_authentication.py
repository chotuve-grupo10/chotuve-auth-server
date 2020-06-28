from unittest.mock import patch
import simplejson as json
from auth_server.persistence.user_persistence import UserPersistence
from auth_server.model.user import User
# from auth_server.db_functions import insert_into_users_db
from auth_server.exceptions.user_already_registered_exception import UserAlreadyRegisteredException
from auth_server.exceptions.user_not_found_exception import UserNotFoundException
from auth_server.decorators.app_server_token_required_decorator import APP_SERVER_TOKEN_HEADER

def test_register_fails_invalid_app_server_token(client):

  with patch('auth_server.decorators.app_server_token_required_decorator.is_valid_token_from_app_server') as mock_is_valid_token_from_app_server:

    mock_is_valid_token_from_app_server.return_value = False

    user_information = {'email': 'this_email_should_not_be_saved@test.com',
        'password': 'fake password',
        'full name': 'full name',
        'phone number': 'phone number',
        'profile picture': 'profile picture',
    }

    hed = {APP_SERVER_TOKEN_HEADER: 'FAKETOKEN'}

    response = client.post('/api/register/', json=user_information, headers=hed,
                follow_redirects=False)

    value_expected =  {'Error' : 'App server token NOT valid'}

    assert mock_is_valid_token_from_app_server.called
    assert json.loads(response.data) == value_expected

def test_register_user_succesfully(client):

  with patch('auth_server.decorators.app_server_token_required_decorator.is_valid_token_from_app_server') as mock_is_valid_token_from_app_server:

    mock_is_valid_token_from_app_server.return_value = True

    with patch.object(UserPersistence,'save') as mock:
      user_information = {'email': 'this_email_should_not_be_saved@test.com',
          'password': 'fake password',
          'full name': 'full name',
          'phone number': 'phone number',
          'profile picture': 'profile picture',
      }

      result = {'Registration': 'Successfully registered new user with email {0}'.format(user_information['email'])}

      hed = {APP_SERVER_TOKEN_HEADER: 'FAKETOKEN'}

      response = client.post('/api/register/', json=user_information, headers=hed,
                  follow_redirects=False)
      value_expected = {'Registration' :
        'Successfully registered new user with email {0}'.format(user_information['email'])}

      assert mock.called
      assert mock_is_valid_token_from_app_server.called
      assert json.loads(response.data) == value_expected
      assert response.status_code == 201

def test_register_user_succesfully_e2e(client_with_db):

    with patch('auth_server.decorators.app_server_token_required_decorator.is_valid_token_from_app_server') as mock_is_valid_token_from_app_server:

      mock_is_valid_token_from_app_server.return_value = True

      user_information = {'email': 'this_email_should_not_be_saved@test.com',
          'password': 'fake password',
          'full name': 'full name',
          'phone number': 'phone number',
          'profile picture': 'profile picture',
      }

      hed = {APP_SERVER_TOKEN_HEADER: 'FAKETOKEN'}

      response = client_with_db.post('/api/register/', json=user_information, headers=hed,
                  follow_redirects=False)
      value_expected = {'Registration' :
        'Successfully registered new user with email {0}'.format(user_information['email'])}
      assert json.loads(response.data) == value_expected
      assert response.status_code == 201

def raise_already_registered_exception(cls, *args, **kwargs):
  raise UserAlreadyRegisteredException

def test_register_user_already_registered(client):


  with patch('auth_server.decorators.app_server_token_required_decorator.is_valid_token_from_app_server') as mock_is_valid_token_from_app_server:

    mock_is_valid_token_from_app_server.return_value = True

    with patch.object(UserPersistence,'save', new=raise_already_registered_exception) as mock:
      user_information = {'email': 'diegote@gmail.com',
          'password': 'fake password',
          'full name': 'full name',
          'phone number': 'phone number', 'profile picture': 'profile picture',
          'hash': 'hash', 'salt': 'salt', 'firebase_user':'0', 'admin_user':'0'}

      hed = {APP_SERVER_TOKEN_HEADER: 'FAKETOKEN'}

      response = client.post('/api/register/', json=user_information, headers=hed,
                  follow_redirects=False)
      value_expected = {'Registration' :
        'This user already exists!'}

      assert json.loads(response.data) == value_expected
      assert response.status_code == 409

def test_login_user_succesful(client):
  with patch('auth_server.authentication.get_user') as mock_get_user:
    result = {}
    status_code = 200
    user = ('diegote@gmail.com')
    mock_get_user.return_value = result, status_code, user

    with patch('auth_server.authentication.validar_usuario') as mock_validar:

      with patch('auth_server.authentication.generate_auth_token') as mock_token_generation:
        mock_token_generation.return_value = 'THISISAFAKETOKEN'
        user_information = {'email': 'diegote@gmail.com',
                  'password': 'fake_falopa'}


        response = client.post('/api/login/', json=user_information,
                     follow_redirects=False)
        value_expected = {'Token':
                  'THISISAFAKETOKEN'}

      mock_validar.return_value = True
      assert mock_get_user.called
      assert mock_validar.called
      assert mock_token_generation.called
      assert json.loads(response.data) == value_expected

def test_login_user_not_found(client):
  with patch('auth_server.authentication.get_user') as mock_get_user:
    result = {'Login': 'user NOT found'}
    status_code = 404
    user = None
    mock_get_user.return_value = result, status_code, user

    user_information = {'email': 'this_user_does_not_Exist@gmail.com',
              'password': 'some_password'}

    response = client.post('/api/login/', json=user_information,
                     follow_redirects=False)
    value_expected = result

    assert mock_get_user.called
    assert json.loads(response.data) == value_expected

def test_register_admin_user_fails_request_doesnt_come_from_admin_user(client):
  with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock_is_request_from_admin_user:

    mock_is_request_from_admin_user.return_value = False

    user_information = {'email': 'this_email_should_not_be_saved@test.com',
        'password': 'fake password',
        'full name': 'full name',
        'phone number': 'phone number', 'profile picture': 'profile picture'}

    hed = {'authorization': 'FAKETOKEN'}

    response = client.post('/api/register_admin_user/', json=user_information, headers=hed,
                     follow_redirects=False)

    value_expected = {'Error' : 'Request doesnt come from admin user'}

    assert mock_is_request_from_admin_user.called
    assert json.loads(response.data) == value_expected

def test_register_admin_user_successfully(client):
  with patch('auth_server.decorators.admin_user_required_decorator.is_request_from_admin_user') as mock_is_request_from_admin_user:

    mock_is_request_from_admin_user.return_value = True

    with patch('auth_server.authentication.insert_admin_user_into_users_db') as mock_insert_admin_user:

      user_information = {'email': 'test@test.com',
          'password': 'fake password',
          'full name': 'full name',
          'phone number': 'phone number', 'profile picture': 'profile picture'}

      hed = {'authorization': 'FAKETOKEN'}

      result = {'Registration': 'Successfully registered new user with email {0}'.format(user_information['email'])}
      status_code = 201

      mock_insert_admin_user.return_value = result, status_code

      response = client.post('/api/register_admin_user/', json=user_information, headers=hed,
                    follow_redirects=False)

      value_expected =  result

      assert mock_is_request_from_admin_user.called
      assert mock_insert_admin_user.called
      assert json.loads(response.data) == value_expected

def test_succesful_login_with_firebase_user_already_registered(client):
  with patch.object(UserPersistence,'get_user_by_email') as user_persistence_mock:
    with patch('firebase_admin.auth.verify_id_token') as firebase_mock:
      firebase_mock.return_value = {'email': 'aa@gmail.com'}
      user_persistence_mock.return_value = User('aa@gmail.com', '', 'Tito', '', '', True, False)
      response = client.post('/api/login_with_firebase/', json={},
                    headers={'authorization': 'FAKETOKEN'}, follow_redirects=False)

      assert json.loads(response.data).get('Token')

def test_login_with_firebase_user_registered_as_password_user(client):
  with patch.object(UserPersistence,'get_user_by_email') as user_persistence_mock:
    with patch('firebase_admin.auth.verify_id_token') as firebase_mock:
      firebase_mock.return_value = {'email': 'aa@gmail.com'}
      user_persistence_mock.return_value = User('aa@gmail.com', '', 'Tito', '', '', False, False)
      response = client.post('/api/login_with_firebase/', json={},
                    headers={'authorization': 'FAKETOKEN'}, follow_redirects=False)

      assert json.loads(response.data) == {'Login': 'user not registered with Firebase'}

def raise_not_found_exception(cls, *args, **kwargs):
  raise UserNotFoundException

def test_succesful_login_with_firebase_user_not_registered(client):
  with patch.object(UserPersistence,'save') as save_user:
    with patch.object(UserPersistence,'get_user_by_email', new=raise_not_found_exception) as get_user:
      with patch('firebase_admin.auth.verify_id_token') as firebase_mock:
        firebase_mock.return_value = {'email': 'aa@gmail.com'}

        response = client.post('/api/login_with_firebase/', json={},
                      headers={'authorization': 'FAKETOKEN'}, follow_redirects=False)

        assert save_user.called
        assert json.loads(response.data).get('Token')