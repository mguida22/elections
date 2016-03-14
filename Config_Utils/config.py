import os

class config:

	def __init__(self):
		pass

	@staticmethod
	def get_environment_variable(variable_name):

		try:
			return os.environ[variable_name]

		except KeyError:
			return "Error"

		return 0;
