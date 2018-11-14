#coding=utf-8
import json
import sys
import codecs
import time
import MySQLdb

from util.json_d import GetDictParam



def parse_har(filePath):
    with codecs.open(filePath, 'r',"utf8") as readObj:
        f = readObj.read()
        print(f.encode("utf-8"))
        harDirct = json.loads(f)
        # print(harDirct)


import requests

androidId = '4416fbcb-1ee4-3517-85f2-238389ff16d9'
imei = '862484032325188'
def testClientId():

    client_URL = 'https://test02.2boss.cn/ubt/api/client'
    client_param = {"market": "tuboshi", "appName": "兔博士", "imei": imei, "brand": "Meizu", "model": "M5",
                    "userAgent": "Mozilla/5.0 (Linux; Android 6.0; M5 Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/44.0.2403.147 Mobile Safari/537.36",
                    "clientType": "Android", "androidId": androidId}

    YHB_client_r = requests.post(url=client_URL, json=client_param, timeout=8)  # 发送验证码请求
    time.sleep(1)
    client_DICT = json.loads(YHB_client_r.content)

    clientId = GetDictParam.get_value(client_DICT, "clientId")


    return clientId



def testCustomerId():
    url = "https://test02.2boss.cn/uc/other-api/customer-info/id"

    payload = {"token":androidId,"imei":imei,"osType":0,"machinetype":"M5"}

    response = requests.request("POST", url, json=payload, timeout=8)
    time.sleep(1)
    customerId_DICT = json.loads(response.content)
    customerId = GetDictParam.get_value(customerId_DICT,'body')

    return customerId


def bindCustomerId():
    '''
        绑定customerId结果
    '''
    url = "https://test02.2boss.cn/rabbit/v1/user/bindUserInfo"
    #clientId = testClientId()
    customerId = testCustomerId()
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
        'cache-control': "no-cache",
        'postman-token': "20d82806-3e5b-a239-52aa-67ec6c0e75fc"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    bind_dict = json.loads(response.content)

    if GetDictParam.get_value(bind_dict,'count') == 1:
        print("bind customerId SUCCESS")
        return True
    else:
        print("bind customerId FAILED")
        return False




def bindUserId(token,clientId):
    '''
    绑定用户登录信息
    :param token: 用户token
    :param clientId: cid
    :return:
    '''
    url = "https://test02.2boss.cn/api/v1/user/current/bindoldcustomer"

    payload = {"customerId":20794114}
    headers = {
        'content-type': "application/json",
        'tbsaccesstoken': token,
        'clientid': clientId,
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)



def login(mobile,veriflyCode):
    '''
    获取用户token
    :param mobile: 手机号码
    :param veriflyCode: 验证码
    :return: token
    '''
    url = "https://test02.2boss.cn/rabbit/v1/app/login/login-by-verifycode"

    payload = {"mobile":mobile,"code":veriflyCode}

    response = requests.request("POST", url, json=payload, timeout=8)

    accessTokenDict = json.loads(response.content)

    token = GetDictParam.get_value(accessTokenDict,'accessToken')

    return token


if __name__ == "__main__":
    # print(sys.getfilesystemencoding())
    # print(sys.getdefaultencoding())
    # fail_path = '/home/fzyzgong/project/test1.har'
    # parse_har(fail_path)

    # testClientId()
    # testCustomerId()

    #bindCustomerId()

    login('17607081946','1234')