#coding=utf-8
import subprocess
import time


def execute_script_Popen(script_path,sleep_time):

    p = subprocess.Popen(['python', script_path], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    stdout, stderr = p.communicate()



    time.sleep(sleep_time)

    r = stdout + stderr

    return r