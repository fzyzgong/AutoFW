#coding=utf-8
import requests
import sys
import traceback
sys.path.append('/home/fzyzgong/project/AutoFWOG/AutoFW/util')
from Mylogging import mylogging

class TestAPI:

    def testDemo(self,protocol,domian,url,headers,param,expected):

        self.protocol = protocol+'://'
        try:
            if param == '' and headers == '':
                r = requests.put(self.protocol + domian + url, timeout=8)
            elif param == '':
                r = requests.put(self.protocol + domian + url, headers=headers, timeout=8)
            elif headers == '':
                r = requests.put(self.protocol + domian + url, json=param, timeout=8)
            else:
                r = requests.put(self.protocol + domian + url, headers=headers, json=param, timeout=8)
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
            mylogging("[" + str(__file__).split('/')[-1] + "][" + self.protocol + domian + url + "] <EXCEPTION>\r" + traceback.format_exc())
            print (traceback.format_exc())
        except requests.exceptions.InvalidHeader:
            mylogging("[" + str(__file__).split('/')[-1] + "]  [" + self.protocol + domian + url + "] <EXCEPTION>\r" + traceback.format_exc())
            print (traceback.format_exc())
        except AttributeError:
            mylogging("["+str(__file__).split('/')[-1]+"]  ["+self.protocol + domian + url+"] <EXCEPTION>\r"+traceback.format_exc())
            print (traceback.format_exc())


if __name__ == "__main__":
    protocol = "HTTP"
    domian = "www.og.demo.com"
    url = "/og/demo"
    headers = {"demo_headers":"demo_headers"}
    param = {"demo_param":"demo_param"}
    expected = {"demo":"Success !"}

    t = TestAPI()
    t.testDemo(protocol,domian,url,headers,param,expected)
