#coding=utf-8
import os
import shutil


def copyFile(sourceFile, targetFile, fileName, ip, url, param, expected):
    parent_path = os.getcwd()
    # print (d)
    # parent_path = os.path.dirname(d)
    # print (parent_path)
    sourceFile_script_path = os.path.join(parent_path,sourceFile)
    targetFile_script_path = os.path.join(parent_path, targetFile)

    '''复制文件'''
    shutil.copy(sourceFile_script_path+"case_templates.py", targetFile_script_path+fileName)

    '''修改参数
    # 将文件读取到内存中'''
    with open(targetFile_script_path+fileName, "r") as f:
        lines = f.readlines()

        '''写的方式打开文件'''
    with open(targetFile_script_path+fileName, "w") as f_w:
        for line in lines:
            if "http://www.og.demo.com" in line:
                line = line.replace("http://www.og.demo.com", ip)
            if "/og/demo" in line:
                line = line.replace("/og/demo", url)
            if '{"demo":"demo"}' in line:
                line = line.replace('{"demo":"demo"}', param)
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