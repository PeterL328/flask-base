from .. import easy_db


class DatabaseUtils(object):
	
	def insert(self, table, values):
		'''
		params example:
			table= pothole
			values = point(3,4)
		'''
		easy_db.execute("INSERT INTO " + table + " VALUES (" + values + ")")

	def select(self, table):
		easy_db.execute("SELECT * FROM " + table)
