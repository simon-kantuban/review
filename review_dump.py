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
SQL_QUERY = "select distinct(content) from %s"

def format_review(sentence):
	if (len(sentence) * 1.1) > len(sentence.encode('utf-8')):
			#Not Chinese review
			return ''	
	sentence = re.sub(u'[ \n"\'~@#$%^&*()-_+=|\\{}\[\]<>/～￥……（）]+', '', sentence)
	sentence = re.sub(u'[，、：:,]+', u' ', sentence)
	sentence = re.sub(u'[。.！!？?；;]+', u' ', sentence)
	if sentence:
		words = word_seg(sentence)
		for (i, word) in enumerate(words):
			word = re.sub(' ', '', word)
			if (len(word) * 1.1) > len(word.encode('utf-8')):
					#Not Chinese
				word = ''
			if i == 0:
				sentence = word
			else:
				sentence += ',' + word		
	
	return sentence
	
with open(sys.argv[1]+'_dump_unique.csv','w') as dump:
	db = MySQLdb.connect(host=DB_SERVER,port=DB_SERVER_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, charset='utf8mb4' )
	cursor = db.cursor()
	cursor.execute(SQL_QUERY%(sys.argv[1]))
	for i in range(cursor.rowcount):
		record = cursor.fetchone()
		hotel_review = format_review(record[0])
		if hotel_review:
			print(record[0])
			print(hotel_review)
			dump.write(hotel_review.encode('utf-8') + '\n')
	db.close()
	
