#coding=utf-8
import requests,parser
import json

class Test_request_PUT:

    def testDemo(self,protocol,domian,url,headers,param,expected):

        self.protocol = protocol+'://'

        # if param == '' and headers == '':
        #     r = requests.put(self.protocol + domian + url)
        # elif param == '':
        #     r = requests.put(self.protocol + domian + url, headers=headers)
        # elif headers == '':
        #     r = requests.put(self.protocol + domian + url, data=param)
        # else:
        #     r = requests.put(self.protocol + domian + url,  data=param)
        # data = {"clientId":"1","sessionId":"2"}
        # url = 'https://ta.2boss.cn/ubt/api/session'
        # s = requests.Session()
        # header = {
        #     "Content-Type": "application/vnd.ptc.sc+json;version=1",
        #     "Referer":"https://ta.2boss.cn/rabbit/v1/event/getEventList?platformType=2&clientEventVersionNo=110&appType=1",
        #     "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT)",
        #     "Accept-Encoding": "gzip, deflate",
        #     "Accept": "*/*",
        #     "Host": "ta.2boss.cn",
        #     "Content-Length": "102",
        #     "Connection": "Keep-Alive",
        #     "Cache-Control": "no-cache",
        # }
        # s.headers.update(header)
        # r = s.put(url,data)
        r = requests.put(self.protocol + domian + url,json = param)
        print (r.text)
        print (r.headers["Content-Type"])

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
    protocol = "https"
    domian = "ta.2boss.cn"
    url = "/ubt/api/session"
    # "Content-Type": "application/vnd.ptc.sc+json;version=1",
    headers = {

        # "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT)",
        # "Accept-Encoding": "gzip, deflate",
        # "Accept": "*/*",
        # "Host": "ta.2boss.cn",
        # "Content-Length": "102",
        # "Connection": "Keep-Alive",
        # "Cache-Control": "no-cache",
    }

    param = {"clientId":"933e801d-a350-4d0a-bae1-8bf063434da","sessionId":"a6373ac4-34ea-4314-abab-29007260c6d1"}
    expected = {"resultCode":0}

    t = Test_request_PUT()
    t.testDemo(protocol,domian,url,headers,param,expected)
