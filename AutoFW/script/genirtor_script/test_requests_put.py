#coding=utf-8
import requests
import sys
import traceback
import os
import json
util_path = os.path.join(os.path.abspath(os.path.dirname(__file__)+ os.path.sep + "../.."),"util")
sys.path.append(util_path)
from Mylogging import mylogging
from json_d import GetDictParam

class TestAPI:

    def testDemo(self,protocol,domian,url,headers,param,expected):
        self.protocol = protocol+'://'
        try:
            if param == '' and headers=='':
                r = requests.get(self.protocol + domian + url, timeout=8)
            elif param == '':
                r = requests.get(self.protocol + domian  + url, headers=headers, timeout=8)
            elif headers == '':
                r = requests.get(self.protocol + domian  + url,params=param, timeout=8)
            else:
                r = requests.get(self.protocol + domian  + url,headers=headers, params=param, timeout=8)
            time_consuming = str(r.elapsed.total_seconds())  # 计算接口被调用耗时
            # rs = r.json()

            rs_str = r.content
            rs_dic = json.loads(rs_str)#此处null的key或者value会被转成None  中文也会被转成unicode

            if isinstance(expected, dict):
                dict_count = len(expected)
                if dict_count == 1:  # 匹配单参数
                    actual_value = GetDictParam.get_value(rs_dic, expected.keys()[0])
                    if actual_value == expected.get(expected.keys()[0]):
                        print ('AutoFW test reslut:PASS\'' + "[time_consuming:" + time_consuming + '] ',
                               "response_expected_actual_value:<" + str(
                                   expected) + ">: expected_value:%s, actual_values:%s ]" % (
                               expected.values()[0], actual_value))
                    else:
                        print ("AutoFW test reslut:FAILED",
                               "[By casuse <" + expected.keys()[0] + ">: expected_value:%s, actual_values:%s ]" % (
                               expected.values()[0], actual_value),
                               str(rs_dic))

                elif dict_count > 1:  # 匹配多参数
                    dic_key_str = []
                    for i in range(dict_count):
                        dic_key_str.append(expected.keys()[i])  # 存放字典所有的key
                    actual_value = GetDictParam.list_for_key_to_dict(rs_dic, dic_key_str)  # 返回一个字典

                    if cmp(expected, actual_value) == 0:  # 返回0，说明两个字典相同，返回其他，说明字典不一样
                        print ('AutoFW test reslut:PASS\'' + "[time_consuming:" + time_consuming + '] ',
                               "response_expected_actual_value:<" + str(
                                   expected) + ">: expected_value:%s, actual_values:%s ]" % (expected, actual_value))
                    else:
                        print ("AutoFW test reslut:FAILED",
                               "[By casuse <" + str(expected) + ">: expected_value:%s, actual_values:%s ]" % (
                               expected, actual_value),
                               str(rs_dic))
                else:
                    print ("expected is NULL")
            else:
                if str(expected) in rs_str:
                    print ('AutoFW test reslut:PASS\'' + "[time_consuming:" + time_consuming + '] ',
                           "response_expected_actual_value:<" + str(
                               expected) + ">: expected_value:%s, actual_values:%s ]" % (str(expected), str(expected)))
                else:
                    print ("AutoFW test reslut:FAILED",
                           "[By casuse <" + str(expected) + ">: expected_value:%s, response:%s ]" % (
                               str(expected), str(rs_dic)))
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
    protocol = "HTTPS"
    domian = "test02.2boss.cn"
    url = "/rabbit/v1/customer/home/getCityInfo"
    headers = ''
    param = 'stationId=0&lat=31.212055&cityId=0&lng=121.607539&plateId=0'
    expected = {"title":"附近小区"}

    t = TestAPI()
    t.testDemo(protocol,domian,url,headers,param,expected)
