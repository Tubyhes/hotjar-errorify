
class DBDictionary ():

	__db__ = {}

	def store (self, key, value):
		self.__db__[key] = value

	def retrieve (self, key):
		if key in self.__db__:
			return self.__db__[key]
		else:
			return None