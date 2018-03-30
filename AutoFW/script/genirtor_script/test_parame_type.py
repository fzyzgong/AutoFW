#encode=utf-8
from AutoFWOG.AutoFW.util import Mylogging

def test_Type(param):

    # if type(param) == str and param == '':
    #     print (param + 'null')
    #     # line = line.replace('{"demo_param":"demo_param"}', "''")
    # elif type(param) == str:
    #     print (param + ' str')
    #     # line = line.replace('{"demo_param":"demo_param"}', param1)
    # elif type(param) == dict:
    #     print (type(param))
    # else:
    #     print ("error")
    #     Mylogging.mylogging('data type error')

    if '{' in param:
        print ("in")
    else:
        print ("not")

if __name__=="__main__":
    param1 = "?sdfsdf=1&12=2"
    param2 = ''
    param3 = '"key1":1,"value1":2'

    test_Type(param3)