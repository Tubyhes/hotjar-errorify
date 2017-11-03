
class AuthStub ():

	# dict of form {<session_id>: [<tracker_id>, ..]}
	def __init__ (self):
		self.__auth__ = {
			"abcdef": ["1234567890", "2345678901"],
			"qwerty": ["0987654321", "2345678901"]
		}

	def authorized (self, tracker_id, session_id):
		if not session_id in self.__auth__:
			return False

		return tracker_id in self.__auth__[session_id]