# -*- coding: utf8 -*-
import sys
import MySQLdb
import requests
import re

DB_SERVER = "tiger"
DB_SERVER_PORT = 34891
DB_USER = "kantuban"
DB_PASSWORD = "UmkVpysZnsOh9hucwG22"
DB_NAME = "ptpq"
PRODUCT_IDS_HTTP = 'http://192.168.0.186:7070/tag_products/%d'

db_con = MySQLdb.connect(host=DB_SERVER,port=DB_SERVER_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, charset='utf8')

review_tables = {
				1:'tc_comment_detail', 5:'tc_comment_detail', 
				2:'ctrip_comment_detail', 3:'ctrip_comment_detail', 41:'ctrip_comment_detail', 42:'ctrip_comment_detail',
				43:'ctrip_comment_detail', 44:'ctrip_comment_detail', 45:'ctrip_comment_detail',
				6:'elong_comment_detail',
				51:'dianping_comment_detail',
				52:'daodao_comment_detail',
				}

def get_product_ids(poi_id):
	_req = requests.get(PRODUCT_IDS_HTTP%(poi_id))
	if _req.status_code == 200:
		_list = _req.json()
		return [(_item['Source'], _item['ProductId']) for _item in _list]
	else:
		return []

def get_review(ota_id, product_id):
	_reviews = []
	
	if review_tables.has_key(ota_id):
		_cursor = db_con.cursor()
		_cursor.execute('select distinct(content) from %s where source_id=%s'%(review_tables[ota_id], product_id))
		_records = _cursor.fetchall()
		
		for _record in _records:
			if (len(_record[0]) * 1.1) > len(_record[0].encode('utf-8')):
				#Not Chinese review
				continue
			hotel_review = re.sub(u'[ \n"\'~@#$%^&*()-_+=|\\{}\[\]<>/～￥……（）]+', '', _record[0])
			hotel_review = re.sub(u'[，、：:,]+', u' ', hotel_review)
			hotel_review = re.sub(u'[。.！!？?；;]+', u' ', hotel_review)
			_reviews.append(hotel_review)
		
		_cursor.close()
	
	return _reviews

def main(poi_id):
	ota_ids = get_product_ids(poi_id)
	with open(str(poi_id) + '.txt','w') as dump:
		for (ota_id, product_id) in ota_ids:
			reviews = get_review(ota_id, product_id)
			
			dump.write('<<<<<<<<<<<<<<<<<<<<<<<<<<%s>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n'%(review_tables[ota_id]))
			for review in reviews:
				dump.write(review.encode('utf-8') + '\n')
				print review

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Wrong parameters"
		quit(1)

	poi_id = int(sys.argv[1]) 
	main(poi_id)
