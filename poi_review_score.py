# -*- coding: utf8 -*-
import MySQLdb
import requests

DB_SERVER = "192.168.0.186"
DB_SERVER_PORT = 34890
DB_USER = "kantuban"
DB_PASSWORD = "UmkVpysZnsOh9hucwG22"
DB_NAME = "ptpq"
POI_IDS_QUERY = "select tag_id from tag_product group by tag_id"
PRODUCT_IDS_QUERY = "select source, product_id, tag_id from tag_product where tag_id = %d group by source having max(create_date)"

PRODUCT_IDS_HTTP = "http://192.168.0.186:7070/tag_products/%d"

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

def percentile_to_5(percentile_score):
	return 5 * percentile_score
	
def score_pencentile (db, product_id, table_name):
	_cursor = db.cursor()
	_cursor.execute('select sum(recommend_type), count(id) from %s where source_id=\'%s\''%(table_name, product_id))
	_review_count = 0
	_calculated_review_rate = -1
	if _cursor.rowcount > 0:
		_record = _cursor.fetchone()
		if _record[0] and _record[1]:
			_recommended_review_count = _record[0]
			_review_count= _record[1]
			_calculated_review_rate = percentile_to_5(float(_recommended_review_count) / _review_count)
		
	_cursor.close
	
	#print 'Percentage:', _calculated_review_rate
	
	return (_calculated_review_rate, _review_count)
	
def score_5 (db, product_id, table_name):
	_cursor = db.cursor()
	_cursor.execute('select avg(score), count(id) from %s where source_id=%s'%(table_name, product_id))
	_review_count = 0
	_avg_score = -1
	if _cursor.rowcount > 0:
		_record = _cursor.fetchone()
		if _record[0] and _record[1]:
			_avg_score = _record[0]
			_review_count= _record[1]
		
	_cursor.close
	
	#print '5:', _avg_score
	return (_avg_score, _review_count)

#Function and voting power
score_dict = {
				1:(score_5, 'tc_comment_detail', 1), 5:(score_5, 'tc_comment_detail', 1), 
			 	2:(score_5, 'ctrip_comment_detail',1), 3:(score_5, 'ctrip_comment_detail',1),
			 	41:(score_5, 'ctrip_comment_detail', 1), 42:(score_5, 'ctrip_comment_detail', 1),
			 	43:(score_5, 'ctrip_comment_detail', 1), 44:(score_5, 'ctrip_comment_detail', 1), 45:(score_5, 'ctrip_comment_detail', 1),
			 	6:(score_pencentile, 'elong_comment_detail',1), 
			 	51:(score_5, 'dianping_comment_detail',1),
			 	52:(score_5, 'daodao_comment_detail',1),
			 }

def get_score(db, product_ids):
	_scores = {}
	for (_source_id, _product_id) in product_ids:
		if score_dict.has_key(_source_id):
			_avg_score, _review_count = score_dict[_source_id][0](db, _product_id, score_dict[_source_id][1])
			if (_avg_score > 0 and _review_count > 0):
				_scores[_source_id] = [_avg_score, _review_count]

	if _scores:			
		weight_score(_scores)
		return calculate_score(_scores)
	else:
		return -1

#Multiple review count to influence the review weight of different OTA
def weight_score(scores):
	print scores
	_total_weight = 0
	for (_source_id, _score) in scores.iteritems():
		_score[1] = _score[1] * score_dict[_source_id][2]


def calculate_score(scores):
	_total_review_count = 0
	for (_source_id, _score) in scores.iteritems():
		_total_review_count += _score[1]
	
	_final_score = 0
	for (_source_id, _score) in scores.iteritems():
		_final_score += _score[0] * (float(_score[1]) / _total_review_count)
	
	return _final_score

def get_product_ids(poi_id):
	_req = requests.get(PRODUCT_IDS_HTTP%(poi_id))
	if _req.status_code == 200:
		_list = _req.json()
		return [(_item['Source'], _item['ProductId']) for _item in _list]
	else:
		return []

def update_review_score(db, poi_id, score):
	_cursor = db.cursor()
	_cursor.execute("update tag set review_score=%f where id=%d"%(score, poi_id))
	db.commit()

def main():
	db = MySQLdb.connect(host=DB_SERVER,port=DB_SERVER_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
	write_db = MySQLdb.connect(host=DB_SERVER,port=DB_SERVER_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
	poi_cursor = db.cursor()
	poi_cursor.execute(POI_IDS_QUERY)
	
	#product_db = MySQLdb.connect(host=DB_SERVER,port=DB_SERVER_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
	#product_cursor = db.cursor()
	
	for _ in range(poi_cursor.rowcount):
		poi_record = poi_cursor.fetchone()
		#product_cursor.execute(PRODUCT_IDS_QUERY%(poi_record[0]))
		#product_records = product_cursor.fetchall()
		#poi_product = [(int(_record[0]), _record[1]) for _record in product_records]
		product_ids = get_product_ids(poi_record[0])
		if product_ids:
			_score = get_score(db, product_ids)
			if _score > 0:
				print _score
				update_review_score(write_db, poi_record[0], _score)
	
	write_db.close()
	
	poi_cursor.close()
	#product_cursor.close()
	db.close()


if __name__ == '__main__':
	main()