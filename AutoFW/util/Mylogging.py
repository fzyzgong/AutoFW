#coding=utf-8
import os

import time

'''
function:在运行脚本时，对脚本的异常要有捕捉，并把捕捉到的信息打到日志中去。
'''
def mylogging(log):

    filePath = os.path.abspath(os.path.dirname(__file__))
    # filePath = os.path.dirname(__file__)
    # print (filePath)

    logFilePath = os.path.join(os.path.dirname(filePath),'log','log.txt')
    # print (logFilePath)

    execTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    # print (execTime)

    open(logFilePath,'a').write('['+execTime+ ']>>  ' +log+'\n')

if __name__ == '__main__':

    mylogging('123')