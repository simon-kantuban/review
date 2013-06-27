# -*- coding: utf8 -*-
import MySQLdb

DB_SERVER = "192.168.0.186"
DB_SERVER_PORT = 34890
DB_USER = "kantuban"
DB_PASSWORD = "UmkVpysZnsOh9hucwG22"
DB_NAME = "ptpq"
POI_IDS_QUERY = "select tag_id from tag_product group by tag_id"
PRODUCT_IDS_QUERY = "select source, product_id, tag_id from tag_product where tag_id = %d group by source having max(create_date)"

"""
ProductSourceTongchengTicket = 1 //同程门票
ProductSourceCtripTicke = 2 //携程门票
ProductSourceCtripHotel = 3 //携程酒店
ProductSourceSongguo = 4 //松果客栈
ProductSourceTongchengHotel = 5 //同程酒店
ProductSourceElongHotel = 6 //艺龙酒店
ProductSourceZhaohaowan = 40 //找好玩
ProductSourceCtrip_11 = 41 //携程id_11
ProductSourceCtrip_12 = 42 //携程id_12
ProductSourceCtrip_13 = 43 //携程城市id
ProductSourceCtrip_14 = 44 //携程id_14
ProductSourceCtrip_15 = 45 //携程id_15
ProductSourceDianping = 51 //大众点评
ProductSourceTripadvisor = 52 //Tripadvisor
ProductSourceElongCity = 53 //艺龙城市
ProductSourceSongguoCity = 54 //松果目的地
"""

def score_pencentile (db, product_id, table_name):
	_cursor = db.cursor()
	_cursor.execute('select avg(score), count(id) from %s where source_id=%d'%(table_name, product_id))
	_review_count = 0
	_score_total = 0
	if _cursor.rowcount > 0:
		_record = _cursor.fetchone()		
		_score_average = _record[0]
		_review_count= _record[1]
		
	_cursor.close
	
	return (_review_count, _score_total)
	
def score_5 (db, product_id, table_name):
	_cursor = db.cursor()
	_cursor.execute('select avg(score), count(id) from %s where source_id=%d'%(table_name, product_id))
	_review_count = 0
	_score_total = -1
	if _cursor.rowcount > 0:
		_record = _cursor.fetchone()		
		_score_average = _record[0]
		_review_count= _record[1]
		
	_cursor.close
	
	return [_score_average, _review_count]

#function and voting power
score_dict = {1:(score_5, 'tc_comment_detail', 1), 2:(score_5, 'ctrip_comment_detail',1)}

def get_score(db, product_ids):
	_scores = {}
	for (_source_id, _product_id) in product_ids:
		if score_dict.has_key(_source_id):
			_scores[_source_id] = score_dict[_source_id][0](db, _product_id, score_dict[_source_id][1])

	if _scores:			
		return weight_score(_scores)
	else:
		return -1

def weight_score(scores):
	print scores
	_total_weight = 0
	for _source_id in scores.keys():
		_total_weight += score_dict[_source_id][2]
		
	for (_source_id, _score) in scores.iteritems():
		_score[1] = _score[1] * (float(score_dict[_source_id][2]) / _total_weight) 

	_total_review = 0
	for (_source_id, _score) in scores.iteritems():
		_total_review += _score[1]
	
	_final_score = 0
	for (_source_id, _score) in scores.iteritems():
		_final_score += _score[0] * (float(_score[1]) / _total_review)
	
	return _final_score

def main():
	db = MySQLdb.connect(host=DB_SERVER,port=DB_SERVER_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
	poi_cursor = db.cursor()
	poi_cursor.execute(POI_IDS_QUERY)
	
	#product_db = MySQLdb.connect(host=DB_SERVER,port=DB_SERVER_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
	product_cursor = db.cursor()
	
	for _ in range(poi_cursor.rowcount):
		poi_record = poi_cursor.fetchone()
		product_cursor.execute(PRODUCT_IDS_QUERY%(poi_record[0]))
		product_records = product_cursor.fetchall()
		poi_product = [(int(_record[0]), int(_record[1])) for _record in product_records]
		print get_score(db, poi_product)
	
	poi_cursor.close()
	product_cursor.close()
	db.close()


if __name__ == '__main__':
	main()