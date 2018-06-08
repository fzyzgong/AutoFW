#coding=utf-8
import os

import time

'''
function:在运行脚本时，对脚本的异常要有捕捉，并把捕捉到的信息打到日志中去。
'''
class Mylogging:
    @staticmethod
    def error(message):

        filePath = os.path.abspath(os.path.dirname(__file__))

        logFilePath = os.path.join(os.path.dirname(filePath),'log','error.log')

        execTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

        with open(logFilePath,'a') as f:#安全模式，自动关闭文件流

            f.write('[Exception]['+execTime+ ']>>  ' +message+'\n')


    @staticmethod
    def interface(message):
        filePath = os.path.abspath(os.path.dirname(__file__))

        logFilePath = os.path.join(os.path.dirname(filePath), 'log', 'script.log')

        execTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        with open(logFilePath, 'a') as f:  # 安全模式，自动关闭文件流

            f.write('[Myloggin][' + execTime + ']>>  ' + message + '\n')

if __name__ == '__main__':

    Mylogging.error('123')