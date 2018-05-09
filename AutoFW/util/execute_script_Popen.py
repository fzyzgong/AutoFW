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


if __name__ == "__main__":
    script_path = "/home/fzyzgong/project/AutoFWOG/AutoFW/script/genirtor_script/实时获取tab标签发现（信息）-2018_5_2_13_34_18.py"
    r = execute_script_Popen(script_path,0.1)

    print r