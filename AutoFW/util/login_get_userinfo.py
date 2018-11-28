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
    def login_get_userinfo(**kwargs):

        androidId = '4416fbcb-1ee4-3517-85f2-238389ff16d9'
        imei = '862484032325188'
        #http://test.2boss.cn/superior/v1/sms/mobileVerify JJB
        #{"type":"10","mobile":"17620367177"}
        #https://test02.2boss.cn/api/v1/sms/mobileVerifyCode2  YHB
        #{"type":0,"mobile":"17607081946"}

        userinfo_dict = {}

        system_info_initialization_k_list = kwargs.keys()
        print(system_info_initialization_k_list)
        if 'TBS_USER_20180424' in system_info_initialization_k_list:

            #--------------------------------新增clientId-------------------------------------------

            '''
                兔博士用户版初始化参数：user_id/customer_id/userCode/verifyCode/token/clientId
                2018-11-14 新增clientId  模拟新用户安装兔博士获取clientId,并与用户信息绑定，设计到的接口如下：
                1：生成clientID
                POST https://test02.2boss.cn/ubt/api/client
                2:生成customer_id
                POST https://test02.2boss.cn/uc/other-api/customer-info/id
                3：clientId与customer_id绑定
                POST https://test02.2boss.cn/rabbit/v1/user/bindUserInfo
                4：绑定当前登录用户
                POST https://test02.2boss.cn/api/v1/user/current/bindoldcustomer
            '''
            clientId = LoginGetUserInfo.getClientId(androidId=androidId, imei=imei)
            print(clientId)
            customerId = LoginGetUserInfo.getCustomerId(androidId=androidId, imei=imei)
            print(customerId)
            if LoginGetUserInfo.bindCustomerId(androidId=androidId, customerId=customerId):
                pass
            else:
                userinfo_dict = 'init_failed'
                return userinfo_dict
            #------------------------------------------------------------------------

            YHB_URL = 'https://test02.2boss.cn/api/v1/sms/mobileVerifyCode2'
            YHB_parame = {"type": "0", "mobile": kwargs['TBS_USER_20180424']}

            # 需要重新建立链接 否则会脏读数据
            conn = MySQLdb.connect(host='10.236.0.71', port=3306, db='sHouseApp_pre', user='gongliping',
                                   passwd='rd@HSf12', charset='utf8')
            handle = conn.cursor()

            YHB_r = requests.post(url=YHB_URL, json=YHB_parame, timeout=8)  # 发送验证码请求
            time.sleep(3)
            YHB_DICT = json.loads(YHB_r.content)
            # print YHB_DICT
            YHB_userinfo_dict = {}
            if GetDictParam.get_value(YHB_DICT, "success") == "true":  # 判断request的返回值是否正常
                # print " YHB pass"
                result2 = handle.execute("select a.verify_code,b.user_id from user_verifycode a,users_info b where a.uri=b.mobile and b.mobile='" + str(
                        kwargs['TBS_USER_20180424']) + "' ORDER BY a.create_time desc LIMIT 1;")
                # result2 = handle.execute(
                #     "select c.verify_code,a.userid,a.user_id from customer_info a,users_info b,user_verifycode c where a.user_id=b.user_id and b.mobile=c.uri and b.mobile='" + str(
                #         kwargs['TBS_USER_20180424']) + "' ORDER BY c.create_time desc LIMIT 1;")
                result2 = handle.fetchone()  # 获取验证码元组
                #print(result2)
                verifyN = str(result2[0])
                user_id = str(result2[1])
                userCode = LoginGetUserInfo.encodeUserId(int(user_id))
                customer_id = str(customerId)
                handle.close()
                # print verifyN
                # YHB_login_url = "https://test02.2boss.cn/api/v1/user/login"
                # YHB_param = {"devicesToken": "f8afa393-87c9-3f26-92fa-bee05259c485", "customer_id": customer_id,
                #              "verifyCode": verifyN,
                #              "userAccount": str(kwargs['TBS_USER_20180424'])}  # devicesToken后台未校验
                # YHB_l = requests.post(url=YHB_login_url, json=YHB_param, timeout=8)
                # time.sleep(1)
                # YHB_l_dict = YHB_l.json()
                # # print YHB_l_dict
                # token = str(GetDictParam.get_value(YHB_l_dict, "accessToken"))  # 获取token
                token = LoginGetUserInfo.login(mobile=kwargs['TBS_USER_20180424'], veriflyCode=verifyN,customerId=customer_id, clientId=clientId)
                #-----------------新增clientId  bindUserId-----------------------------

                LoginGetUserInfo.bindUserId(token=token, clientId=clientId, customerId=customer_id)

                #------------------------------------------------



                # print token
                YHB_userinfo_dict['token'] = token
                YHB_userinfo_dict['user_id'] = user_id
                YHB_userinfo_dict['userCode'] = userCode
                YHB_userinfo_dict['customer_id'] = customer_id
                YHB_userinfo_dict['verify'] = verifyN
                #---------------------------------------------------
                YHB_userinfo_dict['clientId'] = clientId
                # ---------------------------------------------------
                userinfo_dict["YHB_userInfo"] = YHB_userinfo_dict
            else:
                print "########  YHB Exception:服务器返回异常，获取YHB_token失败！  ########"
                print YHB_r.content
                userinfo_dict = 'init_failed'
                return userinfo_dict

        if 'TBS_JJD_20180518' in system_info_initialization_k_list:
            JJB_URL = 'http://test.2boss.cn/superior/v1/sms/mobileVerify'
            JJB_parame = {"type":"10","mobile": kwargs['TBS_JJD_20180518']}
            JJB_r = requests.post(url=JJB_URL,json=JJB_parame,timeout=8)#发送验证码请求
            time.sleep(3)
            JJB_DICT = JJB_r.json()
            # print JJB_DICT

            # 链接测试环境库 sHouseApp_pre
            conn = MySQLdb.connect(host='10.236.0.71', port=3306, db='sHouseApp_pre', user='gongliping',
                                   passwd='rd@HSf12', charset='utf8')
            handle = conn.cursor()

            JJB_userinfo_dict = {}
            if GetDictParam.get_value(JJB_DICT,"resultCode") == 0:#判断request的返回值是否正常
                # print " JJB pass"
                result1 = handle.execute("select c.verify_code,b.user_id,a.userid from customer_info a,users_info b,user_verifycode c where a.user_id=b.user_id and b.mobile=c.uri and b.mobile='"+str(kwargs['TBS_JJD_20180518'])+"' order by create_time desc LIMIT 1;")
                #经济端如果用户和客户id绑定关系被消除了，这行代码会出异常
                result1 = handle.fetchone()  # 获取验证码元组

                verifyV = str(result1[0])
                user_id = str(result1[1])
                userCode = LoginGetUserInfo.encodeUserId(int(user_id))#user_id 编码
                customer_id = str(result1[2])
                handle.close()
                # print verifyV,user_id,userCode,customer_id
                JJB_login_url = "http://test.2boss.cn/superior/v1/user/login"
                JJB_param = 'verifyCode='+verifyV+'&userAccount='+str(kwargs['TBS_JJD_20180518'])
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

                userinfo_dict["JJB_userInfo"] = JJB_userinfo_dict
            else:
                print "########  JJB Exception:服务器返回异常，获取JJB_token失败！  ########"
                print JJB_r.content
                userinfo_dict = 'init_failed'
                return userinfo_dict

        if 'TBS_JJD_20180518' not in system_info_initialization_k_list and 'TBS_USER_20180424' not in system_info_initialization_k_list:
            return userinfo_dict

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


    @staticmethod
    def getClientId(imei, androidId):
        '''
        生成client_id
        :return: ClientId
        '''
        client_URL = 'https://test02.2boss.cn/ubt/api/client'
        client_param = {"market": "tuboshi", "appName": "兔博士", "imei": imei, "brand": "Meizu", "model": "M5",
                        "userAgent": "Mozilla/5.0 (Linux; Android 6.0; M5 Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/44.0.2403.147 Mobile Safari/537.36",
                        "clientType": "Android", "androidId": androidId}

        YHB_client_r = requests.post(url=client_URL, json=client_param, timeout=8)  # 发送验证码请求
        time.sleep(1)
        client_DICT = json.loads(YHB_client_r.content)

        clientId = GetDictParam.get_value(client_DICT, "clientId")

        return clientId


    @staticmethod
    def getCustomerId(imei, androidId):
        '''
        生成customerId
        :return: customerId
        '''
        url = "https://test02.2boss.cn/uc/other-api/customer-info/id"

        payload = {"token": androidId, "imei": imei, "osType": 0, "machinetype": "M5"}

        response = requests.request("POST", url, json=payload, timeout=8)
        time.sleep(1)
        customerId_DICT = json.loads(response.content)
        customerId = GetDictParam.get_value(customerId_DICT, 'body')

        return customerId


    @staticmethod
    def bindCustomerId(androidId, customerId):
        '''
            绑定customerId结果
        '''
        url = "https://test02.2boss.cn/rabbit/v1/user/bindUserInfo"
        #clientId = testClientId()
        #customerId = LoginGetUserInfo.getCustomerId()
        # 需要重新建立链接 否则会脏读数据
        conn = MySQLdb.connect(host='10.236.0.71', port=3306, db='sHouseApp_pre', user='gongliping',
                               passwd='rd@HSf12', charset='utf8')
        handle = conn.cursor()
        handle.execute(
            "select cid from customer_info where userid="+str(customerId)+";")
        cid_tuple = handle.fetchone()  # 获取验证码元组
        cid = str(cid_tuple[0])

        payload = "customerId="+str(customerId)+"&cid="+cid+"&token="+str(androidId)
        headers = {
            'content-type': "application/x-www-form-urlencoded",
        }

        response = requests.request("POST", url, data=payload, headers=headers)
        bind_dict = json.loads(response.content)

        if GetDictParam.get_value(bind_dict,'count') == 1:
            print("bind customerId SUCCESS")
            return True
        else:
            print("bind customerId FAILED")
            return False


    @staticmethod
    def bindUserId(token, clientId, customerId):
        '''
        绑定用户登录信息
        :param token: 用户token
        :param clientId: cid
        :param customerId: 客户id
        :return:
        '''
        url = "https://test02.2boss.cn/api/v1/user/current/bindoldcustomer"

        payload = {"customerId": customerId}
        headers = {
            'content-type': "application/json",
            'tbsaccesstoken': token,
            'clientid': clientId,
        }

        response = requests.request("POST", url, json=payload, headers=headers)

        print("绑定结果：服务器无返回或None为正常  ["+response.text+"]")


    @staticmethod
    def login(mobile, veriflyCode, customerId, clientId):
        '''
        获取用户token
        :param mobile: 手机号码
        :param veriflyCode: 验证码
        :return: token
        '''
        url = "https://test02.2boss.cn/rabbit/v1/app/login/login-by-verifycode"

        payload = {"mobile": mobile, "code": veriflyCode}
        headers = {
            'content-type': "application/json",
            'customerid': customerId,
            'clientid': clientId,
        }
        response = requests.request("POST", url, json=payload, headers=headers, timeout=8)

        accessTokenDict = json.loads(response.content)

        token = GetDictParam.get_value(accessTokenDict, 'accessToken')

        return token

if __name__ == "__main__":
    user_dicts = {"TBS_USER_20180424":"17607081946"}
    # login = LoginGetUserInfo()#,JJB_mobile=17620367177
    LoginGetUserInfo.login_get_userinfo(**user_dicts)