#coding=utf-8
import subprocess


def execute_script_Popen(script_path):

    p = subprocess.Popen(['python', script_path], stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
    stdout , stderr = p.commmunicate()
    p.wait()
    r = stdout + stderr
    return r