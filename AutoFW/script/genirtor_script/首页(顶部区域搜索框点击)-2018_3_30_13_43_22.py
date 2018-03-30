#coding=utf-8
import requests

class TestAPI:

    def testDemo(self,protocol,domian,url,headers,param,expected):

        self.protocol = protocol+'://'

        if param == '' and headers == '':
            r = requests.post(self.protocol + domian + url, timeout=8)
        elif param == '':
            r = requests.post(self.protocol + domian + url, headers=headers, timeout=8)
        elif headers == '':
            r = requests.post(self.protocol + domian + url, json=param, timeout=8)
        else:
            r = requests.post(self.protocol + domian + url, headers=headers, json=param, timeout=8)

        rs = r.json()

        print (rs)
        # 断言 判断接口返回数据是否正常
        if 'resultCode' not in rs.keys():
            print ("AutoFW test reslut:FAILED", str(rs))
        elif rs[expected.keys()[0]] == expected.values()[0]:
            print ("AutoFW test reslut:PASS", str(rs))
        else:
            print ("AutoFW test reslut:FAILED", str(rs))


if __name__ == "__main__":
    protocol = "HTTPS"
    domian = "ta.2boss.cn"
    url = "/estimate/customer/event/recordUserAccessInfo"
    headers = { "TBSAccessToken":"2395a9cc328a4091a0c6d25f35178e34"}
    param = {"eventId":503,"userId":155054,"attrtxtStr":"{\"cityId\":605,\"userId\":155054,\"chanelName\":\"oppo应用商店\",\"appVersion\":\"8.0.2\",\"appName\":\"兔博士用户版\",\"appId\":\"1\",\"machinetype\":\"ONEPLUS A5000_7.1.1\"}"}
    expected = {"resultCode":0}

    t = TestAPI()
    t.testDemo(protocol,domian,url,headers,param,expected)
