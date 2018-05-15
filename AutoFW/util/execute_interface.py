#coding=utf-8
import requests
import sys
import traceback
import os
import json
import urlparse
import MySQLdb
util_path = os.path.join(os.path.abspath(os.path.dirname(__file__)+ os.path.sep + "../.."),"util")
sys.path.append(util_path)
from Mylogging import mylogging
from json_d import GetDictParam

class Execute_Interface:
    @staticmethod
    def execute_interface(protocol,method,parameter_format,domain,url_path,headers,parameter,expected,flag,dynamic):

        # print (type(protocol))
        # print (type(method))
        # print (type(parameter_format))
        # print (type(url_path))
        # print (type(parameter))
        # print (type(expected))
        # print (type(headers))
        # print (type(domain))
        # print (type(dynamic))

        protocol = protocol+'://'

        if flag == 2:#传入动态变量值 修改 header 和 parameter  dynamic入参为{变量名：变量值}
            if headers != '':
                headers = json.loads(headers)
                for h_key in headers.keys():
                    if headers[h_key] == "${"+dynamic.keys()[0]+"}":
                        headers[h_key] = dynamic.values()[0]

            if parameter != '':
                if isinstance(parameter,dict):
                    for p_key in parameter.keys():
                        if parameter[p_key] == "${"+dynamic.keys()[0]+"}":
                            parameter[p_key] = dynamic.values()[0]
                else:
                    if "${"+dynamic.keys()[0]+"}" in parameter:
                        old_p = "${"+dynamic.keys()[0]+"}"
                        new_p = "${"+dynamic.values()[0]+"}"
                        str(parameter).replace(old_p,new_p)

        elif flag == 3:#不需要关联动态变量值
            pass

        try:
            if str(method).upper() == "GET":
                if parameter == '' and headers == '':
                    r = requests.get(protocol + domain + url_path, timeout=8)
                elif parameter == '':
                    r = requests.get(protocol + domain + url_path, headers=headers, timeout=8)
                elif headers == '':
                    r = requests.get(protocol + domain + url_path, params=parameter, timeout=8)
                else:
                    r = requests.get(protocol + domain + url_path, headers=headers, params=parameter, timeout=8)

            elif str(method).upper() == "POST":
                if parameter_format == 'application/x-www-form-urlencoded':

                    if parameter == '' and headers == '':
                        r = requests.post(protocol + domain + url_path, timeout=8)
                    elif parameter == '':
                        r = requests.post(protocol + domain + url_path, headers=headers, timeout=8)
                    elif headers == '':
                        # 字符串参数转字典
                        param_tmp = urlparse.urlparse(parameter).path
                        parameter = dict((k, v[0]) for k, v in urlparse.parse_qs(param_tmp).items())
                        r = requests.post(protocol + domain + url_path, data=parameter, timeout=8)
                    else:
                        # 字符串参数转字典
                        param_tmp = urlparse.urlparse(parameter).path
                        parameter = dict((k, v[0]) for k, v in urlparse.parse_qs(param_tmp).items())
                        r = requests.post(protocol + domain + url_path, headers=headers, data=parameter, timeout=8)
                elif parameter_format == 'application/json':

                    if parameter == '' and headers == '':
                        r = requests.post(protocol + domain + url_path, timeout=8)
                    elif parameter == '':
                        r = requests.post(protocol + domain + url_path, headers=headers, timeout=8)
                    elif headers == '':
                        r = requests.post(protocol + domain + url_path, json=parameter, timeout=8)
                    else:
                        r = requests.post(protocol + domain + url_path, headers=headers, json=parameter, timeout=8)
                elif parameter_format == 'multipart/form-data':
                    if parameter == '' and headers == '':
                        r = requests.post(protocol + domain + url_path, timeout=8)
                    elif parameter == '':
                        r = requests.post(protocol + domain + url_path, headers=headers, timeout=8)
                    elif headers == '':
                        r = requests.post(protocol + domain + url_path, json=parameter, timeout=8)
                    else:
                        r = requests.post(protocol + domain + url_path, headers=headers, json=parameter, timeout=8)
                elif parameter_format == 'text/plain':
                    if parameter == '' and headers == '':
                        r = requests.post(protocol + domain + url_path, timeout=8)
                    elif parameter == '':
                        r = requests.post(protocol + domain + url_path, headers=headers, timeout=8)
                    elif headers == '':
                        r = requests.post(protocol + domain + url_path, json=parameter, timeout=8)
                    else:
                        r = requests.post(protocol + domain + url_path, headers=headers, json=parameter, timeout=8)
                elif parameter_format == 'text/xml':
                    if parameter == '' and headers == '':
                        r = requests.post(protocol + domain + url_path, timeout=8)
                    elif parameter == '':
                        r = requests.post(protocol + domain + url_path, headers=headers, timeout=8)
                    elif headers == '':
                        r = requests.post(protocol + domain + url_path, json=parameter, timeout=8)
                    else:
                        r = requests.post(protocol + domain + url_path, headers=headers, json=parameter, timeout=8)


            time_consuming = str(r.elapsed.total_seconds())  # 计算接口被调用耗时
            # rs = r.json()

            rs_str = r.content
            print (rs_str)
            rs_dic = json.loads(rs_str)

            expected = json.loads(str(expected))#unicode转字典
            # print type(expected)

            dict_count = len(expected)
            if dict_count == 1:  # 匹配单参数
                actual_value = GetDictParam.get_value(rs_dic, expected.keys()[0])
                if actual_value == expected.get(expected.keys()[0]):
                    api_log = 'AutoFW test reslut:PASS\'' + "[time_consuming:" + time_consuming + '] ' + \
                              'response_expected_actual_value:<' + str(expected) + '>: expected_value:' +\
                              expected.values()[0]+ ' actual_values:'+ str(actual_value)+'] '+str(rs_str)
                else:
                    api_log = 'AutoFW test reslut:FAILED\' [By casuse <' + expected.keys()[0] + '>: expected_value:'+\
                              expected.values()[0]+', actual_values:'+str(actual_value)+'' +'] '+str(rs_str)

            elif dict_count > 1:  # 匹配多参数
                dic_key_str = []
                for i in range(dict_count):
                    dic_key_str.append(expected.keys()[i])  # 存放字典所有的key
                actual_value = GetDictParam.list_for_key_to_dict(rs_dic, dic_key_str)  # 返回一个字典

                if cmp(expected, actual_value) == 0:  # 返回0，说明两个字典相同，返回其他，说明字典不一样
                    api_log = 'AutoFW test reslut:PASS\'' + "[time_consuming:" + time_consuming + '] ' + \
                              'response_expected_actual_value:<' + str(expected) + '>: expected_value:' + \
                              expected.values()[0] + ' actual_values:' + str(actual_value) + '] '+str(rs_str)
                else:
                    api_log = 'AutoFW test reslut:FAILED\' [By casuse <' + expected.keys()[0] + '>: expected_value:' + \
                              expected.values()[0] + ', actual_values:' + str(actual_value) + '' + '] ' + str(rs_str)
            else:
                print ("expected is NULL")
        except requests.exceptions.ConnectionError:
            mylogging("[" + str(__file__).split('/')[-1] + "][" + protocol + domain + url_path + "] <EXCEPTION>\r" + traceback.format_exc())
            print (traceback.format_exc())
        except requests.exceptions.InvalidHeader:
            mylogging("[" + str(__file__).split('/')[-1] + "]  [" + protocol + domain + url_path + "] <EXCEPTION>\r" + traceback.format_exc())
            print (traceback.format_exc())
        except AttributeError:
            mylogging("["+str(__file__).split('/')[-1]+"]  ["+protocol + domain + url_path+"] <EXCEPTION>\r"+traceback.format_exc())
            print (traceback.format_exc())

        if flag == 1:  # 需要抓取动态变量值   **dynamic入参为{需要抓取接口名：变量值}
            #-------start-----抓取验证码特例------------------------
            if "verifyCode" == dynamic.values()[0]:# and "login_get_mobileVerifyCode" == dynamic.keys()[0]
                conn = MySQLdb.connect(host='mysql.test.tuboshi.co', port=3306, db='sHouseApp_pre', user='gongliping', passwd='rd@HSf12@#Tcba',
                                       charset='utf8')
                handle = conn.cursor()
                verifyCode = handle.execute("SELECT code from sms_log a where a.mobile ='17607081946' ORDER BY a.send_time desc LIMIT 1;")
                verifyCode = handle.fetchone()[0]
                return verifyCode,api_log
            # ---------end---抓取验证码特例------------------------

            for k, v in dynamic.items():
                dynamic_value = v
            dynamic_values = GetDictParam.get_value(rs_dic, dynamic_value)  # 获取动态变量值
            print ("****************dynamic_values:%s"%(dynamic_values))#None为未抓到
            if dynamic_values is None:
                dynamic_values = "ab6fa173260d4b58a5e7bd83417a4d2f"
            return dynamic_values,api_log

        if flag == 2:
            return api_log

        if flag == 3:
            return api_log

if __name__ == "__main__":
    method = "POST"
    protocol = "HTTPS"
    domain = "test02.2boss.cn"
    url = "/api/v1/user/login"
    headers = '' #{"TBSAccessToken":"ab6fa173260d4b58a5e7bd83417a4d2f"}
    parameter = {"devicesToken":"f8afa393-87c9-3f26-92fa-bee05259c485","customer_id":"4527767","verifyCode":"5446","userAccount":"17607081946"}
    expected = '{"mobile": "17607081946"}'

    t = Execute_Interface()
    dynamic = {"test1":"accessToken"}
    #execute_interface(self,method,parameter_format,domain,url_path,headers,parameter,expected,falg,**dynamic)
    t.execute_interface(protocol,method,"application/json",domain,url,headers,parameter,expected,1,dynamic)
