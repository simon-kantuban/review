# -*- coding: utf8 -*-
import sys
import MySQLdb
import re
from ictclas.cnseg_ext import *

DB_SERVER = "192.168.0.186"
DB_SERVER_PORT = 34890
DB_USER = "kantuban"
DB_PASSWORD = "UmkVpysZnsOh9hucwG22"
DB_NAME = "ptpq" 
SQL_QUERY = "select distinct(content) from %s"

LHan = [[0x2E80, 0x2E99],    # Han # So  [26] CJK RADICAL REPEAT, CJK RADICAL RAP
        [0x2E9B, 0x2EF3],    # Han # So  [89] CJK RADICAL CHOKE, CJK RADICAL C-SIMPLIFIED TURTLE
        [0x2F00, 0x2FD5],    # Han # So [214] KANGXI RADICAL ONE, KANGXI RADICAL FLUTE
        0x3005,              # Han # Lm       IDEOGRAPHIC ITERATION MARK
        0x3007,              # Han # Nl       IDEOGRAPHIC NUMBER ZERO
        [0x3021, 0x3029],    # Han # Nl   [9] HANGZHOU NUMERAL ONE, HANGZHOU NUMERAL NINE
        [0x3038, 0x303A],    # Han # Nl   [3] HANGZHOU NUMERAL TEN, HANGZHOU NUMERAL THIRTY
        0x303B,              # Han # Lm       VERTICAL IDEOGRAPHIC ITERATION MARK
        [0x3400, 0x4DB5],    # Han # Lo [6582] CJK UNIFIED IDEOGRAPH-3400, CJK UNIFIED IDEOGRAPH-4DB5
        [0x4E00, 0x9FC3],    # Han # Lo [20932] CJK UNIFIED IDEOGRAPH-4E00, CJK UNIFIED IDEOGRAPH-9FC3
        [0xF900, 0xFA2D],    # Han # Lo [302] CJK COMPATIBILITY IDEOGRAPH-F900, CJK COMPATIBILITY IDEOGRAPH-FA2D
        [0xFA30, 0xFA6A],    # Han # Lo  [59] CJK COMPATIBILITY IDEOGRAPH-FA30, CJK COMPATIBILITY IDEOGRAPH-FA6A
        [0xFA70, 0xFAD9],    # Han # Lo [106] CJK COMPATIBILITY IDEOGRAPH-FA70, CJK COMPATIBILITY IDEOGRAPH-FAD9
        [0x20000, 0x2A6D6],  # Han # Lo [42711] CJK UNIFIED IDEOGRAPH-20000, CJK UNIFIED IDEOGRAPH-2A6D6
        [0x2F800, 0x2FA1D]]  # Han # Lo [542] CJK COMPATIBILITY IDEOGRAPH-2F800, CJK COMPATIBILITY IDEOGRAPH-2FA1D

def build_re():
    L = []
    for i in LHan:
        if isinstance(i, list):
            f, t = i
            f = unichr(f)
            t = unichr(t)
            L.append('%s-%s' % (f, t))
        else:
            L.append(unichr(i))

    return re.compile('[%s]+' % ''.join(L), re.UNICODE)

chinese_re = build_re()

"""
We only take out Chinese chars
"""
def format_review(sentence):
	"""
	if (len(sentence) * 1.1) > len(sentence.encode('utf-8')):
			#Not Chinese review
			return ''	
	sentence = re.sub(u'[ \n"\'~@#$%^&*()-_+=|\\{}\[\]<>/～￥……（）]+', '', sentence)
	sentence = re.sub(u'[，、：:,]+', u' ', sentence)
	sentence = re.sub(u'[。.！!？?；;]+', u' ', sentence)
	"""
        #words = re.findall(u'[\u4e00-\u9fff]+', sentence)
        words = chinese_re.findall(sentence) 
	sentence = ''
	for (i, word) in enumerate(words):
		if i > 0:
			sentence += ','
		sentence += word

	if sentence:
		words = word_seg(sentence)
		sentence = ''
		for (i, word) in enumerate(words):
			word = re.sub(',', '', word)
			if not word:
				continue
			if sentence:
				sentence += ',' + word
			else:
				sentence = word		
	
	return sentence
	
def main():
	with open(sys.argv[1]+'.txt','w') as dump:
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
		
if __name__ == '__main__':
	main()
