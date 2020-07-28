import string
import random

def random_string(length):
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def id_generator(size=6, chars=string.digits):
	return ''.join(random.choice(chars) for x in range(size))
