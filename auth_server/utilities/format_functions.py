def format_with_underscores(dictionary):
	new_dictionary = {}
	for key in dictionary:
		new_dictionary[key.replace(' ', '_')] = dictionary[key]

	return new_dictionary
