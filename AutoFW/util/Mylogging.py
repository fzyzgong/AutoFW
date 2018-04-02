#coding=utf-8
import os

import time

'''
function:在运行脚本时，对脚本的异常要有捕捉，并把捕捉到的信息打到日志中去。
'''

def mylogging(message):

    filePath = os.path.abspath(os.path.dirname(__file__))
    # filePath = os.path.dirname(__file__)
    # print (filePath)

    logFilePath = os.path.join(os.path.dirname(filePath),'log','error.log')
    # print (logFilePath)

    execTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    # print (execTime)

    # f = open(logFilePath,'a').write('['+execTime+ ']>>  ' +log+'\n')
    # f.close()
    with open(logFilePath,'a') as f:#安全模式，自动关闭文件流

        f.write('[Exception]['+execTime+ ']>>  ' +message+'\n')

if __name__ == '__main__':

    mylogging('123')