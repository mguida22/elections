import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

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
