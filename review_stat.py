#! /usr/bin/env python
#coding=utf-8
import sys
import logging
from mylib.thrift_go import go_tag
import MySQLdb
import requests

DB_SERVER = "cheetah"
DB_SERVER_PORT = 34890
DB_USER = "kantuban"
DB_PASSWORD = "UmkVpysZnsOh9hucwG22"
DB_NAME = "ptpq"
POI_IDS_QUERY = "select tag_id from tag_product group by tag_id"

def main():
        db = MySQLdb.connect(host=DB_SERVER,port=DB_SERVER_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
        poi_cursor = db.cursor()
        poi_cursor.execute(POI_IDS_QUERY)
        counts = []

        for _ in range(poi_cursor.rowcount):
                _record = poi_cursor.fetchone()
                _count = go_tag.TagGetCommentCount(_record[0])
                if _count:
                    counts.append(_count)
                print _record[0], ':', _count

        counts = sorted(counts)
        print 'lowest 20:'
        for i in range(20):
            print counts[i]

        print 'total pois:', len(counts)
        print '20% index:', int(round(len(counts) * 0.2))
        print '20% value:', counts[int(round(len(counts) * 0.2))]


        poi_cursor.close()
        db.close()


if __name__ == '__main__':
        #print go_tag.TagGetCommentCount(88737)
        main()
