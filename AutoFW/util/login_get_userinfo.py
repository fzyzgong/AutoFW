#coding=utf-8

import requests
import json
from json_d import GetDictParam
import MySQLdb
import urlparse
import time
from requests.exceptions import ReadTimeout

class LoginGetUserInfo:

    @staticmethod
    def login_get_userinfo(YHB_mobile,JJB_mobile):
        #http://test.2boss.cn/superior/v1/sms/mobileVerify JJB
        #{"type":"10","mobile":"17620367177"}
        #https://test02.2boss.cn/api/v1/sms/mobileVerifyCode2  YHB
        #{"type":0,"mobile":"17607081946"}

        JJB_URL = 'http://test.2boss.cn/superior/v1/sms/mobileVerify'
        JJB_parame = {"type":"10","mobile":JJB_mobile}

        YHB_URL = 'https://test02.2boss.cn/api/v1/sms/mobileVerifyCode2'
        YHB_parame = {"type": "0", "mobile": YHB_mobile}

        JJB_r = requests.post(url=JJB_URL,json=JJB_parame,timeout=8)#发送验证码请求
        time.sleep(3)
        JJB_DICT = JJB_r.json()
        # print JJB_DICT

        # 链接测试环境库 sHouseApp_pre
        conn = MySQLdb.connect(host='mysql.test.tuboshi.co', port=3306, db='sHouseApp_pre', user='gongliping',
                               passwd='rd@HSf12', charset='utf8')
        handle = conn.cursor()

        userinfo_dict = {}

        JJB_userinfo_dict = {}
        if GetDictParam.get_value(JJB_DICT,"resultCode") == 0:#判断request的返回值是否正常
            # print " JJB pass"
            result1 = handle.execute("select c.verify_code,b.user_id,a.userid from customer_info a,users_info b,user_verifycode c where a.user_id=b.user_id and b.mobile=c.uri and b.mobile='"+str(JJB_mobile)+"' order by create_time desc LIMIT 1;")
            result1 = handle.fetchone()  # 获取验证码元组
            verifyV = str(result1[0])
            user_id = str(result1[1])
            userCode = LoginGetUserInfo.encodeUserId(int(user_id))#user_id 编码
            customer_id = str(result1[2])
            handle.close()
            # print verifyV,user_id,userCode,customer_id
            JJB_login_url = "http://test.2boss.cn/superior/v1/user/login"
            JJB_param = 'verifyCode='+verifyV+'&userAccount='+str(JJB_mobile)
            # 字符串参数转字典
            param_tmp = urlparse.urlparse(JJB_param).path
            JJB_param = dict((k, v[0]) for k, v in urlparse.parse_qs(param_tmp).items())

            JJB_l = requests.post(url=JJB_login_url, data=JJB_param, timeout=8)
            time.sleep(1)
            JJB_l_dict = JJB_l.json()
            # print JJB_l_dict
            token = str(GetDictParam.get_value(JJB_l_dict, "TBSAccessToken"))  # 获取token
            # print token
            JJB_userinfo_dict['token'] = token
            JJB_userinfo_dict['user_id'] = user_id
            JJB_userinfo_dict['userCode'] = userCode
            JJB_userinfo_dict['customer_id'] = customer_id
            JJB_userinfo_dict['verify'] = verifyV


        else:
            print "########  JJB Exception:服务器返回异常，获取JJB_token失败！  ########"
            print JJB_r.content

        #需要重新建立链接 否则会脏读数据
        conn = MySQLdb.connect(host='mysql.test.tuboshi.co', port=3306, db='sHouseApp_pre', user='gongliping',
                               passwd='rd@HSf12', charset='utf8')
        handle = conn.cursor()

        YHB_r = requests.post(url=YHB_URL, json=YHB_parame, timeout=8)#发送验证码请求
        time.sleep(3)
        YHB_DICT = YHB_r.json()
        # print YHB_DICT
        YHB_userinfo_dict = {}
        if GetDictParam.get_value(YHB_DICT,"success") == "true":#判断request的返回值是否正常
            # print " YHB pass"
            result2 = handle.execute("select c.`code`,a.userid,a.user_id from customer_info a,users_info b,sms_log c where a.user_id=b.user_id and b.mobile=c.mobile and b.mobile='"+str(YHB_mobile)+"' ORDER BY c.send_time desc LIMIT 1;")
            result2 = handle.fetchone()#获取验证码元组
            verifyN = str(result2[0])
            user_id = str(result2[2])
            userCode = LoginGetUserInfo.encodeUserId(int(user_id))
            customer_id = str(result2[1])
            handle.close()
            # print verifyN
            YHB_login_url = "https://test02.2boss.cn/api/v1/user/login"
            YHB_param = {"devicesToken":"f8afa393-87c9-3f26-92fa-bee05259c485","customer_id":customer_id,"verifyCode":verifyN,"userAccount":str(YHB_mobile)}#devicesToken后台未校验
            YHB_l = requests.post(url=YHB_login_url,json=YHB_param,timeout=8)
            time.sleep(1)
            YHB_l_dict = YHB_l.json()
            # print YHB_l_dict
            token = str(GetDictParam.get_value(YHB_l_dict,"accessToken"))#获取token
            # print token
            YHB_userinfo_dict['token'] = token
            YHB_userinfo_dict['user_id'] = user_id
            YHB_userinfo_dict['userCode'] = userCode
            YHB_userinfo_dict['customer_id'] = customer_id
            YHB_userinfo_dict['verify'] = verifyN

        else:
            print "########  YHB Exception:服务器返回异常，获取YHB_token失败！  ########"
            print YHB_r.content

        userinfo_dict["YHB_userInfo"] = YHB_userinfo_dict
        userinfo_dict["JJB_userInfo"] = JJB_userinfo_dict
        print userinfo_dict
        return userinfo_dict
    '''
    返回值{'YHB_userInfo': {'user_id': '186539', 'customer_id': '20766346', 'YHB_token': '10c20c71afe547548b622dc9613789ba', 
    'userCode': '10681935'}, 'JJB_userInfo': {'customer_id': '20766204', 'user_id': '186567', 
    'JJB_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vbGl5b3UuY28iLCJleHAiOjE1NDUxNDU4NDEsInVzZXJJZ
    CI6MTg2NTY3LCJyZWZyZXNoRXhwaXJlc0F0IjoxNTYzMTQ1ODQxfQ.1K1-Z-r-KKHwWkG1ZdWHew-w-97sIXuNj0KXFSMJsU4', 
    'userCode': '10681765'}}
    '''


    @staticmethod
    def encodeUserId(user_id):#user_id转换编码
        conInt = 10000000
        tmpint = conInt + user_id;
        user_id = LoginGetUserInfo.swapStrChar(LoginGetUserInfo.swapStrChar(str(tmpint), 2, 4), 5, 7);

        return str(user_id)

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
    LoginGetUserInfo.login_get_userinfo(YHB_mobile=17607081946,JJB_mobile=17620367177)