#coding=utf-8
import requests
import sys
import traceback
import os
import json
import urlparse
import logging
from requests.exceptions import ReadTimeout
util_path = os.path.join(os.path.abspath(os.path.dirname(__file__)+ os.path.sep + "../.."),"util")
sys.path.append(util_path)
from Mylogging import Mylogging
from json_d import GetDictParam

class Execute_Fixed_Interface:

    @staticmethod
    def execute_interface(url,method,parameter_format,headers,parameter,expected,user_info):

        if '' != headers:
            headers = json.loads(headers)

        Mylogging.interface("--------------------------------------------------------------------------")
        Mylogging.interface("####################################################")
        Mylogging.interface("url_path : " + str(url))
        Mylogging.interface("method   : " + str(method))
        Mylogging.interface("headers  : " + str(headers))
        Mylogging.interface("parameter: " + str(parameter))
        Mylogging.interface("####################################################")


        print ("####################################################")
        print ("url_path:" + str(url))
        print ("method:" + str(method))
        print ("headers:" + str(headers))
        print ("parameter:" + str(parameter))
        print ("####################################################")

        try:
            if str(method).upper() == "GET":
                if parameter == '' and headers == '':
                    r = requests.get(url, timeout=8)
                elif parameter == '':
                    r = requests.get(url, headers=headers, timeout=8)
                elif headers == '':
                    #避免中文
                    param_tmp = urlparse.urlparse(parameter).path
                    parameter = dict((k, v[0]) for k, v in urlparse.parse_qs(param_tmp).items())
                    r = requests.get(url, params=parameter, timeout=8)
                else:
                    # 避免中文
                    param_tmp = urlparse.urlparse(parameter).path
                    parameter = dict((k, v[0]) for k, v in urlparse.parse_qs(param_tmp).items())
                    r = requests.get(url, headers=headers, params=parameter, timeout=8)

            elif str(method).upper() == "POST":
                if parameter_format == 'application/x-www-form-urlencoded':
                    if parameter == '' and headers == '':
                        r = requests.post(url, timeout=8)
                    elif parameter == '':
                        r = requests.post(url, headers=headers, timeout=8)
                    elif headers == '':
                        # 字符串参数转字典
                        param_tmp = urlparse.urlparse(parameter).path
                        parameter = dict((k, v[0]) for k, v in urlparse.parse_qs(param_tmp).items())
                        r = requests.post(url, data=parameter, timeout=8)
                    else:
                        # 字符串参数转字典
                        param_tmp = urlparse.urlparse(parameter).path
                        parameter = dict((k, v[0]) for k, v in urlparse.parse_qs(param_tmp).items())
                        r = requests.post(url, headers=headers, data=parameter, timeout=8)
                elif parameter_format == 'application/json':

                    if parameter == '' and headers == '':
                        r = requests.post(url, timeout=8)
                    elif parameter == '':
                        r = requests.post(url, headers=headers, timeout=8)
                    elif headers == '':
                        #print parameter
                        parameter = json.loads(parameter)
                        r = requests.post(url, json=parameter, timeout=8)
                    else:
                        parameter = json.loads(parameter)
                        r = requests.post(url, headers=headers, json=parameter, timeout=8)
                elif parameter_format == 'multipart/form-data':
                    if parameter == '' and headers == '':
                        r = requests.post(url, timeout=8)
                    elif parameter == '':
                        r = requests.post(url, headers=headers, timeout=8)
                    elif headers == '':
                        r = requests.post(url, json=parameter, timeout=8)
                    else:
                        r = requests.post(url, headers=headers, json=parameter, timeout=8)
                elif parameter_format == 'text/plain':
                    if parameter == '' and headers == '':
                        r = requests.post(url, timeout=8)
                    elif parameter == '':
                        r = requests.post(url, headers=headers, timeout=8)
                    elif headers == '':
                        r = requests.post(url, json=parameter, timeout=8)
                    else:
                        r = requests.post(url, headers=headers, json=parameter, timeout=8)
                elif parameter_format == 'text/xml':
                    if parameter == '' and headers == '':
                        r = requests.post(url, timeout=8)
                    elif parameter == '':
                        r = requests.post(url, headers=headers, timeout=8)
                    elif headers == '':
                        r = requests.post(url, json=parameter, timeout=8)
                    else:
                        r = requests.post(url, headers=headers, json=parameter, timeout=8)
            else:
                api_log = 'AutoFW test reslut:SKIP\'' +str(method)+" 方法还未支持"
                return api_log
            time_consuming = str(r.elapsed.total_seconds())  # 计算接口被调用耗时

            rs_str = r.content
            print rs_str

            if rs_str[0] == '{' and rs_str[-1] == '}':#判断返回报文是否是字典
                rs_dic = json.loads(rs_str)

                if ":" in str(expected) and "{" in str(expected):
                    expected_d = json.loads(str(expected))#unicode转字典

                    if isinstance(expected_d, dict):

                        dict_count = len(expected_d)
                        if dict_count == 1:  # 匹配单参数
                            actual_value = GetDictParam.get_value(rs_dic, expected_d.keys()[0])
                            if actual_value == expected_d.get(expected_d.keys()[0]):
                                api_log = 'AutoFW test reslut:PASS\'' + "[time_consuming:" + str(time_consuming) + '] ' + \
                                          'response_expected_actual_value:<' + str(expected) + '>: expected_value:' + \
                                          str(expected_d.values()[0])+ ' actual_values:'+ str(actual_value) + '] '+str(rs_str)
                            else:
                                api_log = 'AutoFW test reslut:FAILED\' [By casuse <' + str(expected_d.keys()[0]) + '>: expected_value:'+ \
                                          str(expected_d.values()[0])+', actual_values:'+str(actual_value)+'' +'] '+str(rs_str)

                        elif dict_count > 1:  # 匹配多参数
                            dic_key_str = []
                            for i in range(dict_count):
                                dic_key_str.append(expected_d.keys()[i])  # 存放字典所有的key
                            actual_value = GetDictParam.list_for_key_to_dict(rs_dic, dic_key_str)  # 返回一个字典

                            print expected_d,actual_value

                            if cmp(expected_d, actual_value) == 0:  # 返回0，说明两个字典相同，返回其他，说明字典不一样
                                api_log = 'AutoFW test reslut:PASS\'' + "[time_consuming:" + str(time_consuming) + '] ' + \
                                          'response_expected_actual_value:<' + str(expected) + '>: expected_value:' + \
                                          str(expected_d.values()[0]) + ' actual_values:' + str(actual_value) + '] '+str(rs_str)
                            else:
                                api_log = 'AutoFW test reslut:FAILED\' [By casuse <' + str(expected.keys()[0]) + '>: expected_value:' + \
                                          str(expected_d.values()[0]) + ', actual_values:' + str(actual_value) + '' + '] ' + str(rs_str)
                        else:
                            print ("expected is NULL")
                else:
                    if str(expected) in rs_str:
                        api_log = 'AutoFW test reslut:PASS\'' + "[time_consuming:" + str(time_consuming) + '] ' + \
                                  'response_expected_actual_value:<' + str(expected) + '>: expected_value:'+str(expected)+', actual_values:'+str(expected)+' ]' + str(rs_str)
                    else:
                        api_log = 'AutoFW test reslut:FAILED\'[By casuse <' + str(expected) + '>: expected_value:'+str(expected)+' response:' + str(rs_str)
            else:#服务器返回报文不是字典时处理
                if str(expected) in rs_str:
                    api_log = 'AutoFW test reslut:PASS\'' + "[time_consuming:" + str(time_consuming) + '] ' + \
                              'response_expected_actual_value:<' + str(expected) + '>: expected_value:' + str(expected) + ', actual_values:' + str(expected) + ' ]' + str(rs_str)
                else:
                    api_log = 'AutoFW test reslut:FAILED\'[By casuse <' + str(expected) + '>: expected_value:'+str(expected)+' response:' + str(rs_str)

        except requests.exceptions.ConnectionError:
            Mylogging.error("[" + str(__file__).split('/')[-1] + "][" + url + "] <EXCEPTION>\r" + traceback.format_exc())
            print (traceback.format_exc())
            api_log = 'AutoFW test reslut:SKIP\' requests.exceptions.ConnectionError exception:' + str(traceback.format_exc())
        except requests.exceptions.InvalidHeader:
            Mylogging.error("[" + str(__file__).split('/')[-1] + "]  [" + url + "] <EXCEPTION>\r" + traceback.format_exc())
            print (traceback.format_exc())
            api_log = 'AutoFW test reslut:SKIP\' requests.exceptions.InvalidHeader exception:' + str(traceback.format_exc())
        except AttributeError:
            Mylogging.error("["+str(__file__).split('/')[-1]+"]  ["+url+"] <EXCEPTION>\r"+traceback.format_exc())
            print (traceback.format_exc())
            api_log = 'AutoFW test reslut:SKIP\' AttributeError exception:' + str(traceback.format_exc())
        except ValueError:
            Mylogging.error("[" + str(__file__).split('/')[-1] + "]  [" + url + "] <EXCEPTION>\r" + traceback.format_exc())
            print (traceback.format_exc())
            api_log = 'AutoFW test reslut:SKIP\' ValueError exception:' + str(traceback.format_exc())
        except ReadTimeout:
            Mylogging.error("[" + str(__file__).split('/')[-1] + "]  [" + url + "] <EXCEPTION>\r" + traceback.format_exc())
            print (traceback.format_exc())
            api_log = 'AutoFW test reslut:SKIP\' ReadTimeout exception:' + str(traceback.format_exc())



        return api_log


if __name__ in "__main__":
    #url,method,parameter_format,headers,parameter,expected,user_info
    url = 'https://test02.2boss.cn/rabbit/v1/customer/house/search'
    method = 'POST'
    parameter_format = 'application/json'
    headers = ''
    parameter = '{"pageType":0,"pageSize":20,"targetId":0,"page":1,"lat":0.0,"type":3,"cityId":605,"lng":0.0,"keywords":"奉贤金汇"}'
    expected = '{"resultCode":0}'#{"resultCode":0,"nearLocation":"null"}
    user_info = 'test'
    Execute_Fixed_Interface.execute_interface(url,method,parameter_format,headers,parameter,expected,user_info)