#coding=utf-8
import json
import requests
import MySQLdb
import os

"""
功能介绍：通过fiddler抓包工具导出的.har文件，把导出的.har文件存到一个指定dirPath下，然后指定给parse_har函数调用
调用前需要获取dirPath下的所有.har文件list，传给parse_har执行
"""


'''
:funcation get_dir_filePath_list
:param dirPath
:note 获取某目录下所有文件list
:author OG
'''
file_list = []
def get_dir_filePath_list(dirPath):
    # for root,dirs,files in os.walk(dirPath):
    #     current_dir = root #当前目录路径
    #     dir_list = dirs #当前路径下所有子目录
    #     file_list = files #当前路径下所有非目录子文件
    # print(file_list)
    # print(dir_list)
    for file in os.listdir(dirPath):
        file_path = os.path.join(dirPath, file)
        if os.path.isdir(file_path):
            get_dir_filePath_list(file_path)
        else:
            file_list.append(file_path)
    return file_list


def remove_not_har(file_list):
    for file in file_list:
        if os.path.splitext(file)[1] != '.har':
            file_list.remove(file)
    return file_list


'''
:funcation get_userinfo
:param mobile
:note 获取验证码
:author OG
'''
def get_userinfo(mobile='17607081946'):
    user_info_dict = {}
    url1 = 'https://test02.2boss.cn/api/v1/sms/mobileVerifyCode2'
    param1 = {"type":0,"mobile":mobile}
    get_result1 = requests.post(url=url1,json=param1)
    print(get_result1.text)

    conn = MySQLdb.connect(host='10.236.0.71',port=3306,db='sHouseApp_pre',user='gongliping',passwd='rd@HSf12',charset='utf8')
    handle = conn.cursor()
    handles = handle.execute("select b.userid,b.user_id,c.`code` from users_info a,customer_info b, sms_log c where a.user_id=b.user_id and a.mobile=c.mobile and a.mobile='%s' order by send_time desc LIMIT 1;" % mobile)
    userinfo = handle.fetchone()
    print(userinfo)
    user_info_dict['customer_id'] = userinfo[0]
    user_info_dict['user_id'] = userinfo[1]
    user_info_dict['verify_code'] = userinfo[2]

    url2 = 'https://test02.2boss.cn/api/v1/user/login'
    param2 = {"devicesToken":"f8afa393-87c9-3f26-92fa-bee05259c485","customer_id":user_info_dict['customer_id'],"verifyCode":user_info_dict['verify_code'],"userAccount":mobile}
    get_result2 = requests.post(url=url2, json=param2)
    login_dict = json.loads(get_result2.text)
    user_info_dict['accessToken'] = login_dict['accessToken']
    print(user_info_dict)
    return user_info_dict


'''
:funcation parse_har
:param filePath,mobile
:note 解析har文件
:author OG
'''
def parse_har(filePath,token):
    with open(filePath, 'r') as readObj:
        harDirct = json.loads(readObj.read().encode('gbk').decode('utf-8-sig'))
        interface_count = len(harDirct['log']['entries'])
        for i in range(interface_count):
            method = harDirct['log']['entries'][i]['request']['method']
            url = harDirct['log']['entries'][i]['request']['url']
            header_list = harDirct['log']['entries'][i]['request']['headers']
            header_dict = {}
            print("%s:%s" % (method, url))
            for header in header_list:
                if header['name'] == "TBSAccessToken":
                    header_dict[header['name']] = token
                else:
                    header_dict[header['name']] = header['value']
            if method == 'GET':
            #     # print(harDirct['log']['entries'][2]['request']['queryString'])#parameter
                r = requests.get(url=url,headers=header_dict)
            elif method == 'POST':
                for header in header_list:
                    if header['name'] == "Content-Type":
                        content_type = header['value']#content_type
                        print(content_type)
                        break
                if "application/x-www-form-urlencoded" in content_type:
                    parameter = harDirct['log']['entries'][i]['request']['postData']['params']
                    param_dict = {}
                    for p_list in parameter:
                        param_dict[p_list['name']] = p_list['value']
                    r = requests.post(url=url,headers=header_dict,data=param_dict)
                # elif "application/json" in content_type:
                else:
                    param_dict = harDirct['log']['entries'][i]['request']['postData']['text']
                    r = requests.post(url=url, headers=header_dict, json=json.loads(param_dict))
            print(r.text)

if __name__ == "__main__":
    mobile = '17607081946'
    # filePath = 'D:\\har_file\\login_grzx.har'
    # filePath = 'D:\\har_file\\imUpdateCustomer.har'
    # filePath = 'D:\\har_file\\YHB_GRZX_JB_022.har'
    # parse_har(filePath,mobile)
    dirPath = 'D:\\har_file'
    file_list = get_dir_filePath_list(dirPath)#获取目录下所有文件
    file_list = remove_not_har(file_list)#出去后缀不是.har文件
    user_info_dict = get_userinfo(mobile)#获取最新用户信息(accessToken、user_id、customer_id,verify_code)
    token = user_info_dict['accessToken']
    print(file_list)
    print(len(file_list))
    for filePath in file_list:
        parse_har(filePath,token)