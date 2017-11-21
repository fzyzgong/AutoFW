#coding=utf-8
import requests


class TestAPI:

    def testDemo(self,ip,url,param,expected):

        r = requests.get(ip + url,params=param)
        rs = r.json()
        print (rs)
        #断言 判断接口返回数据是否正常
        if rs[expected.keys()[0]] == expected.values()[0]:
            print ("AutoFW test reslut:PASS")
        else:
            print ("AutoFW test reslut:FAILED")



if __name__ == "__main__":

    ip = "http://www.og.demo.com"
    url = "/og/demo"
    param = {"demo":"demo"}
    expected = {"demo":"Success !"}

    t = TestAPI()
    t.testDemo(ip,url,param,expected)
