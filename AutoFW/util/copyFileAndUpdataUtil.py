#coding=utf-8
import os,sys
import shutil
import Mylogging

def copyFile(sourceFile, targetFile, fileName, protocol, method, domain, url,headers, param, expected):
    parent_path = os.getcwd() + "/AutoFW/"

    sourceFile_script_path = os.path.join(parent_path,sourceFile)
    targetFile_script_path = os.path.join(parent_path, targetFile)

    method = str(method).upper()

    if method=='GET':
        '''复制文件 GET请求模板'''
        shutil.copy(sourceFile_script_path+"case_templates_GET.py", targetFile_script_path+fileName)
    elif method=='POST':
        shutil.copy(sourceFile_script_path + "case_templates_POST.py", targetFile_script_path + fileName)
    elif method == 'PUT':
        shutil.copy(sourceFile_script_path + "case_templates_PUT.py", targetFile_script_path + fileName)
    elif method == 'DELETE':
        shutil.copy(sourceFile_script_path + "case_templates_DELETE.py", targetFile_script_path + fileName)
    else:
        print ("不存在该协议模板")
        sys.exit(1)

    '''修改参数
    # 将文件读取到内存中'''
    with open(targetFile_script_path+fileName, "r") as f:
        lines = f.readlines()

        '''写的方式打开文件'''
    with open(targetFile_script_path+fileName, "w") as f_w:
        for line in lines:
            if "HTTP" in line:
                line = line.replace("HTTP", protocol)
            if "www.og.demo.com" in line:
                line = line.replace("www.og.demo.com", domain)
            if "/og/demo" in line:
                line = line.replace("/og/demo", url)
            if '{"demo_headers":"demo_headers"}' in line:
                if headers=='':
                    print ("headers null")
                    line = line.replace('{"demo_headers":"demo_headers"}', "''")
                else:
                    print ("headers not null")
                    line = line.replace('{"demo_headers":"demo_headers"}', headers)
            if '{"demo_param":"demo_param"}' in line:
                if type(param) == str and param=='':
                    line = line.replace('{"demo_param":"demo_param"}', "''")
                elif type(param) == str and '{' not in param:
                    line = line.replace('{"demo_param":"demo_param"}', "'"+param+"'")
                elif type(param) == str and '{' in param and ':' in param:
                    line = line.replace('{"demo_param":"demo_param"}', param)
                else:
                    Mylogging.mylogging("Error_Message" + fileName + "生成脚本失败" + "parameter data type error;not in(str/dict)!")
            if '{"demo":"Success !"}' in line:
                line = line.replace('{"demo":"Success !"}',expected)
            f_w.write(line)


# if __name__ == "__main__":
#
#     '''sourceFile/targetFile相对路径'''
#     sourceFile = "script/HTTP_API_case_templates/"
#     targetFile = "script/genirtor_script/"
#
#     '''复制重命名'''
#     fileName = "1234.py"
#     ip = "http://www.sojson.com"
#     url = "/open/api/weather/json.shtml"
#
#     '''以字符串格式传给复制替换，否则遇中文转码'''
#     param = '{"city": "北京"}'
#     expected = '{"message": "Success !"}'
#
#     copyFile(sourceFile, targetFile, fileName, ip, url, param, expected)