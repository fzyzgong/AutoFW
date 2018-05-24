#coding=utf-8
import MySQLdb
#funcation desc: 测试环境数据精彩被生产环境同步数据，导致用例的某些参数失效，
# 该功能就是每次都获取一次最新的数据，然后修改传入的参数（user_id/customer_id/token/userCode）

class Get_userId:

    @staticmethod
    def get_token_userid_customer(mobile_id):

        #链接测试环境库 sHouseApp_pre
        conn = MySQLdb.connect(host='mysql.test.tuboshi.co',port=3306,db='sHouseApp_pre',user='gongliping',passwd='rd@HSf12',charset='utf8')
        handle = conn.cursor()
        result = handle.execute("select a.user_id,a.access_token,c.customer_id from users_access_token a,users_info b,"
                                  "users_customers_relations c where a.user_id=b.user_id and b.user_id=c.user_id and  b.mobile='%s'" % mobile_id)

        result = handle.fetchall() #嵌套元组
        user_id = int(result[0][0]) #用户id
        access_token = str(result[0][1])  # token_id
        customer_id = int(result[0][2]) #客户id
        userCode = Get_userId.encodeUserId(user_id)

        return str(user_id),str(userCode), access_token, str(customer_id)

    @staticmethod
    def get_user_id_encode(mobile_id):
        #经济版使用user_id会进行编码后在使用
        # 链接测试环境库 sHouseApp_pre
        conn = MySQLdb.connect(host='mysql.test.tuboshi.co', port=3306, db='sHouseApp_pre', user='gongliping',
                               passwd='rd@HSf12', charset='utf8')
        handle = conn.cursor()
        result = handle.execute("select a.user_id,b.userid from users_info a,customer_info b where a.user_id=b.user_id and a.mobile='%s'" % mobile_id)
        result = handle.fetchall()  # 嵌套元组
        user_id = int(result[0][0])  # 用户id
        customer_id = int(result[0][1]) #客户id
        userCode = Get_userId.encodeUserId(user_id)
        return str(user_id),str(userCode),str(customer_id)

    @staticmethod
    def encodeUserId(user_id):
        conInt = 10000000
        tmpint = conInt + user_id;
        signUserId = Get_userId.swapStrChar(Get_userId.swapStrChar(str(tmpint), 2, 4), 5, 7);

        return signUserId

    @staticmethod
    def swapStrChar(originalString,a,b):

        strlist = []
        for s in originalString:
            strlist.append(s)

        temp = strlist[a]
        strlist[a] = strlist[b]
        strlist[b] = temp
        originalString = ''.join(strlist) #将数组转成字符串
        return originalString



if __name__ == "__main__":
    a,b,c = Get_userId.get_token_userid_customer("17607081946")
    #a = Get_userId.get_user_id_encode("17620367177")
    print a,b,c