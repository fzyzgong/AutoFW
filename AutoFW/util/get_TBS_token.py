#coding=utf-8

import requests
import MySQLdb

def get_TBS_token(user_id,customer_id):

    # user_id = 444445209
    # user_id = 171631

    #test env
    conn = MySQLdb.connect(host='mysql.test.tuboshi.co',port=3306,db='sHouseApp_pre',user='gongliping',passwd='rd@HSf12@#Tcba',charset='utf8')
    # prd env
    # conn = MySQLdb.connect(host='192.168.36.133',port=3306,db='db_name',user='username',passwd='passwd',charset='utf8')
    handle = conn.cursor()
    username = handle.execute("select access_token from users_access_token a where a.user_id='%s'" % user_id)
    #select a.user_id,b.mobile,c.customer_id from users_access_token a,users_info b,users_customers_relations c where b.mobile='17607081946' and a.user_id=b.user_id and b.user_id=c.user_id;

    # token_id = handle.fetchone()
    return  handle.fetchmany(size=2)

if __name__ == "__main__":
    print (get_TBS_token(171631,2))