import auth_server.random_string

def test_random_string_generates_string_in_uppercase():

	id_generated = auth_server.random_string.random_string(6)

	assert len(id_generated) == 6
	assert id_generated.isupper()


def test_id_generator_generates_6_digits_string_successfully():

	id_generated = auth_server.random_string.id_generator()

	assert len(id_generated) == 6