from .. import easy_db


class DatabaseUtils():
	
	def insert(table, values):
		'''
		params example:
			table= pothole
			values = point(3,4)
		'''
		easy_db.execute("INSERT INTO " + table " VALUES (" + values + ")");

		
	def select(table):
		easy_db.execute("SELECT * FROM " + table);