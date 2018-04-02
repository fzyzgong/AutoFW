#coding=utf-8
import requests
import sys
sys.path.append('/home/fzyzgong/project/AutoFWOG/AutoFW/util')
from Mylogging import mylogging

#还未实现该功能
class TestAPI:

    def testDemo(self,protocol,domian,url,headers,param,expected):

        self.protocol = protocol+'://'
        try:
            if param == '' and headers == '':
                r = requests.post(self.protocol + domian + url, timeout=8)
            elif param == '':
                r = requests.post(self.protocol + domian + url, headers=headers, timeout=8)
            elif headers == '':
                r = requests.post(self.protocol + domian + url, json=param, timeout=8)
            else:
                r = requests.post(self.protocol + domian + url, headers=headers, json=param, timeout=8)
            time_consuming = str(r.elapsed.total_seconds())  # 计算接口被调用耗时
            rs = r.json()

            print (rs)
            # 断言 判断接口返回数据是否正常
            if 'resultCode' not in rs.keys():
                print ("AutoFW test reslut:FAILED", str(rs))
            elif rs[expected.keys()[0]] == expected.values()[0]:
                print ('AutoFW test reslut:PASS\'' + "[time_consuming:"+ time_consuming + '] ', str(rs))
            else:
                print ("AutoFW test reslut:FAILED", str(rs))

        except requests.exceptions.ConnectionError:
            mylogging("[" + str(__file__) + "][" + self.protocol + domian + url + "]:[requests.exceptions.ConnectionError]")

if __name__ == "__main__":
    protocol = "HTTP"
    domian = "www.og.demo.com"
    url = "/og/demo"
    headers = {"demo_headers":"demo_headers"}
    param = {"demo_param":"demo_param"}
    expected = {"demo":"Success !"}

    t = TestAPI()
    t.testDemo(protocol,domian,url,headers,param,expected)
