# -*- coding: utf8 -*-
# -*- coding: utf8 -*-
import sys
import MySQLdb
from review_tfidf_score import ReviewCorpus 
from review_dump import format_review
from ictclas.cnseg_ext import *

DB_SERVER = "tiger"
DB_SERVER_PORT = 34890
DB_USER = "kantuban"
DB_PASSWORD = "UmkVpysZnsOh9hucwG22"
DB_NAME = "ptpq" 
SQL_QUERY = "select id, content from %s"
SQL_UPDATE = "update %s set tfidf_score=%f where id=%d"

table_name = sys.argv[1]
corpus = ReviewCorpus.load('model/' + table_name)

read_con = MySQLdb.connect(host=DB_SERVER,port=DB_SERVER_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, charset='utf8mb4' )
write_con = MySQLdb.connect(host=DB_SERVER,port=DB_SERVER_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, charset='utf8mb4' )

read_cursor = read_con.cursor()
read_cursor.execute(SQL_QUERY%(table_name))

write_cursor = write_con.cursor() 

for i in range(read_cursor.rowcount):
    record = read_cursor.fetchone()
    hotel_review = format_review(record[1])
    tfidf_score = 0
    if hotel_review:
        tfidf_score = corpus.tfidf_score(hotel_review)
    
    write_cursor.execute(SQL_UPDATE %(table_name, tfidf_score, record[0]))
    print "[%f]%s"%(tfidf_score, record[1])

write_cursor.close()
write_con.close()

read_cursor.close()
read_con.close()