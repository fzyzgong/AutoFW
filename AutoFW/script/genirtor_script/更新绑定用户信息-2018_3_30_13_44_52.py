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
            r = requests.post(self.protocol + domian + url, data=param, timeout=8)
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
    url = "/superior/v1/im/imUpdateCustomer"
    headers = ''
    param = {"userId":"171631","customer_id":"20150554"}
    expected = {"resultCode":0}

    t = TestAPI()
    t.testDemo(protocol,domian,url,headers,param,expected)
