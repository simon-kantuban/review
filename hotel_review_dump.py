# -*- coding: utf8 -*-
import sys
import MySQLdb
import re
from ictclas.cnseg_ext import *

DB_SERVER = "tiger"
DB_SERVER_PORT = 34890
DB_USER = "kantuban"
DB_PASSWORD = "UmkVpysZnsOh9hucwG22"
DB_NAME = "ptpq" 
SQL_QUERY = "select distinct(content) from ctrip_comment_detail"

with open(sys.argv[1],'w') as dump:
	db = MySQLdb.connect(host=DB_SERVER,port=DB_SERVER_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, charset='utf8mb4' )
	cursor = db.cursor()
	cursor.execute(SQL_QUERY)
	for i in range(cursor.rowcount):
		record = cursor.fetchone()
		if (len(record[0]) * 1.1) > len(record[0].encode('utf-8')):
			#Not Chinese review
			continue
		#words = word_seg_full(record[1].replace(u'\n', ''))
		hotel_review = re.sub(u'[ \n"\'~@#$%^&*()-_+=|\\{}\[\]<>/～￥……（）]+', '', record[0])
        	hotel_review = re.sub(u'[，、：:,]+', u' ', hotel_review)
		hotel_review = re.sub(u'[。.！!？?；;]+', u' ', hotel_review)
				
		words = word_seg(hotel_review)
		sentence = ""
		for (i, word) in enumerate(words):
			word = re.sub(' ', '', word)
			if (len(word) * 1.1) > len(word.encode('utf-8')):
				#Not Chinese
				word = ''
			if i == 0:
				sentence = word
			else:
				sentence += ',' + word

		if sentence:
			print(hotel_review)
			print(sentence)
			dump.write(sentence.encode('utf-8') + '\n')
	db.close()
	
