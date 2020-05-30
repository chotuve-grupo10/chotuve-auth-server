import simplejson as json

def test_hello(client):
	response = client.get('/api/hello', follow_redirects=True)
	assert response.data == b'Hello, World!'
	assert response.status_code == 200

def test_about(client):
	response = client.get('/api/about/', follow_redirects=True)
	assert response.data == b'This is Authorization Server for chotuve-10. Still in construction'
	assert response.status_code == 200

def test_ping(client):
	response = client.get('/api/ping/', follow_redirects=True)
	assert json.loads(response.data) == {'Health' : 'OK'}
	assert response.status_code == 200

def test_home(client):
	response = client.get('/', follow_redirects=True)
	assert response.data == b'<h1>Welcome to auth server !</h1>'
	assert response.status_code == 200

def test_fake(client):
	response = client.get('/fake/', follow_redirects=True)
	assert not response.status_code == 200
	assert response.status_code == 404
