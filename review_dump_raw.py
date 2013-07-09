# -*- coding: utf8 -*-
import sys
import MySQLdb
import re
#from ictclas.cnseg_ext import *

DB_SERVER = "tiger"
DB_SERVER_PORT = 34890
DB_USER = "kantuban"
DB_PASSWORD = "UmkVpysZnsOh9hucwG22"
DB_NAME = "ptpq" 
SQL_QUERY = "select distinct(content) from %s"
#SQL_QUERY = "select content from %s limit 10"

def main():
	with open(sys.argv[1]+'_raw.txt','w') as dump:
		db = MySQLdb.connect(host=DB_SERVER,port=DB_SERVER_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, charset='utf8')
		cursor = db.cursor()
		cursor.execute(SQL_QUERY%(sys.argv[1]))
		for _ in range(cursor.rowcount):
			record = cursor.fetchone()
			print record[0].encode('utf-8')
			dump.write(record[0].encode('utf-8') + '\n')
		db.close()
		
if __name__ == '__main__':
	main()
