#coding=utf-8
import requests
import sys
import traceback
import os
import json
import urlparse
import MySQLdb
from requests.exceptions import ReadTimeout
util_path = os.path.join(os.path.abspath(os.path.dirname(__file__)+ os.path.sep + "../.."),"util")
sys.path.append(util_path)
from Mylogging import mylogging
from get_token_userid_customer import Get_userId
from json_d import GetDictParam


class Execute_Interface:
    @staticmethod
    def execute_interface(project_name,protocol,method,parameter_format,domain,url_path,headers,parameter,expected,flag,dynamic,user_info):
        if '' != headers:
            headers = json.loads(headers)
        #替换动态值， headers/parameter/url_path
        if '兔博士经济版' == str(project_name):
            userInfo = user_info["JJB_userInfo"]
        elif '兔博士用户端' == str(project_name):
            userInfo = user_info["YHB_userInfo"]
        verify = userInfo["verify"] #验证码
        user_id = userInfo["user_id"]
        userCode = userInfo["userCode"]
        customer_id = userInfo["customer_id"]
        access_token = userInfo["token"]

        #分表判断 headers/parameter/url_path中是否存在需要替换的变量 ${user_id} ${customer_id} ${access_token} ${userCode}
        if '${userCode}' in url_path:
            old_p = "${userCode}"
            new_p = userCode
            url_path = str(url_path).replace(old_p, new_p)

        if '${user_id}' in url_path:
            old_p = "${user_id}"
            new_p = user_id
            url_path = str(url_path).replace(old_p, new_p)

        if '${customer_id}' in url_path:
            old_p = "${customer_id}"
            new_p = customer_id
            url_path = str(url_path).replace(old_p, new_p)

        if '${access_token}' in url_path:
            old_p = "${access_token}"
            new_p = access_token
            url_path = str(url_path).replace(old_p, new_p)

        if headers != '':
            for h_key in headers.keys():
                if headers[h_key] == '${userCode}':
                    headers[h_key] = userCode
                if headers[h_key] == '${user_id}':
                    headers[h_key] = user_id
                if headers[h_key] == '${customer_id}':
                    headers[h_key] = customer_id
                if headers[h_key] == '${access_token}':
                    headers[h_key] = access_token


        if parameter != '':
            if isinstance(parameter,dict):
                for p_key in parameter.keys():
                    if parameter[p_key] == '${userCode}':
                        parameter[p_key] = userCode
                    if parameter[p_key] == '${user_id}':
                        parameter[p_key] = user_id
                    if parameter[p_key] == '${customer_id}':
                        parameter[p_key] = customer_id
                    if parameter[p_key] == '${access_token}':
                        parameter[p_key] = access_token
            else:
                if '${userCode}' in parameter:
                    old_p = '${userCode}'
                    new_p = userCode
                    parameter = str(parameter).replace(old_p,new_p)
                if '${user_id}' in parameter:
                    old_p = '${user_id}'
                    new_p = user_id
                    parameter = str(parameter).replace(old_p,new_p)
                if '${customer_id}' in parameter:
                    old_p = '${customer_id}'
                    new_p = customer_id
                    parameter = str(parameter).replace(old_p,new_p)
                if '${access_token}' in parameter:
                    old_p = '${access_token}'
                    new_p = access_token
                    parameter = str(parameter).replace(old_p,new_p)

        protocol = protocol+'://'

        if flag == 2:#传入动态变量值 修改 header 和 parameter  dynamic入参为{变量名：变量值}
            if headers != '':
            #     headers = json.loads(headers)
                for h_key in headers.keys():
                    if headers[h_key] == "${"+str(dynamic.keys()[0])+"}":
                        headers[h_key] = dynamic.values()[0]

            if parameter != '':
                if isinstance(parameter,dict):
                    for p_key in parameter.keys():
                        if parameter[p_key] == "${"+str(dynamic.keys()[0])+"}":
                            parameter[p_key] = dynamic.values()[0]
                else:
                    if "${"+str(dynamic.keys()[0])+"}" in parameter:
                        old_p = "${"+str(dynamic.keys()[0])+"}"
                        new_p = str(dynamic.values()[0])
                        parameter = str(parameter).replace(old_p,new_p)


            if "${"+str(dynamic.keys()[0])+"}" in url_path:
                old_p = "${"+str(dynamic.keys()[0])+"}"
                new_p = str(dynamic.values()[0])
                url_path = str(url_path).replace(old_p,new_p)

        elif flag == 3:#不需要关联动态变量值
            pass

        print ("####################################################")
        print ("url_path:"+str(url_path))
        print ("method:" + str(method))
        print ("headers:" + str(headers))
        print ("parameter:"+str(parameter))
        print ("####################################################")

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
            #rs_str = rs_str.replace("㎡","m")
            #rs_str = rs_str.replace("／", "/")
            #print (rs_str)
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
            mylogging("[" + str(__file__).split('/')[-1] + "][" + protocol + domain + url_path + "] <EXCEPTION>\r" + traceback.format_exc())
            print (traceback.format_exc())
            api_log = 'AutoFW test reslut:FAILED\' requests.exceptions.ConnectionError exception:' + str(traceback.format_exc())
        except requests.exceptions.InvalidHeader:
            mylogging("[" + str(__file__).split('/')[-1] + "]  [" + protocol + domain + url_path + "] <EXCEPTION>\r" + traceback.format_exc())
            print (traceback.format_exc())
            api_log = 'AutoFW test reslut:FAILED\' requests.exceptions.InvalidHeader exception:' + str(traceback.format_exc())
        except AttributeError:
            mylogging("["+str(__file__).split('/')[-1]+"]  ["+protocol + domain + url_path+"] <EXCEPTION>\r"+traceback.format_exc())
            print (traceback.format_exc())
            api_log = 'AutoFW test reslut:FAILED\' AttributeError exception:' + str(traceback.format_exc())
        except ValueError:
            mylogging("[" + str(__file__).split('/')[-1] + "]  [" + protocol + domain + url_path + "] <EXCEPTION>\r" + traceback.format_exc())
            print (traceback.format_exc())
            api_log = 'AutoFW test reslut:FAILED\' ValueError exception:' + str(traceback.format_exc())
        except ReadTimeout:
            mylogging("[" + str(__file__).split('/')[-1] + "]  [" + protocol + domain + url_path + "] <EXCEPTION>\r" + traceback.format_exc())
            print (traceback.format_exc())
            api_log = 'AutoFW test reslut:FAILED\' ReadTimeout exception:' + str(traceback.format_exc())

        if flag == 1:  # 需要抓取动态变量值   **dynamic入参为{需要抓取接口名：变量值}
            #-------start-----抓取验证码特例------------------------
            if "verifyCode" == dynamic.values()[0]:# and "login_get_mobileVerifyCode" == dynamic.keys()[0]
                # conn = MySQLdb.connect(host='mysql.test.tuboshi.co', port=3306, db='sHouseApp_pre', user='gongliping', passwd='rd@HSf12@#Tcba',
                #                        charset='utf8')
                # handle = conn.cursor()
                # verifyCode = handle.execute("SELECT code from sms_log a where a.mobile =17607081946 ORDER BY a.send_time desc LIMIT 1;")
                # verifyCode = handle.fetchone()[0]
                return verify,api_log
            # ---------end---抓取验证码特例------------------------

            for k, v in dynamic.items():
                dynamic_value = v
            dynamic_values = GetDictParam.get_value(rs_dic, dynamic_value)  # 获取动态变量值
            print ("****************dynamic_values:%s"%(dynamic_values))#None为未抓到
            if dynamic_values is None:
                dynamic_values = "None"
            return dynamic_values,api_log

        if flag == 2:
            return api_log

        if flag == 3:
            return api_log

if __name__ == "__main__":
    method = "GET"
    protocol = "HTTPS"
    domain = "test02.2boss.cn"
    url = "/rabbit/v1/question/superior/list"
    headers = ''#{"TBSAccessToken":"d69b6b575a3f40f19d488bdde969c807"}
    parameter = 'superiorCode=10681955'
    expected = '{"superiorTel":"18522222222"}'
    user_info = {}
    t = Execute_Interface()
    dynamic = None
    #execute_interface(self,method,parameter_format,domain,url_path,headers,parameter,expected,falg,**dynamic)
    t.execute_interface(protocol,method,"GET方法选该参数格式",domain,url,headers,parameter,expected,3,dynamic,user_info)