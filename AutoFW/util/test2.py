#coding=utf-8
import json
import requests
import re


if __name__ == "__main__":
    url = "https://test02.2boss.cn/rabbit/v1/config/share-link"
    # url = "https://test02.2boss.cn/estimate/customer/event/recordUserAccessInfo"
    headers = {u'TBSAccessToken': '10c20c71afe547548b622dc9613789ba','content-type': "application/json",}
    parameter1 = u'{"extra":"{\"houseId\":18048,\"cityId\":605}","type":2}'

    # parameter1 = u'{"eventId":9902,"userId":20767990,"attrtxtStr":"{\"timeLimitStr\":\"3个月\",\"cityId\":605,\"userId\":\"20767990\",\"chanelName\":\"tuboshi\",\"appVersion\":\"8.1.2\",\"appName\":\"兔博士用户版\",\"appId\":\"1\",\"machinetype\":\"ONEPLUS A5000_7.1.1\"}"}'

    pstart = parameter1.split("\"{")[0]
    print pstart
    pend = parameter1.split("}\"")[1]
    print pend

    p1 = parameter1.encode('unicode-escape').decode('string_escape')
    val_d = re.search(r'"{(.*)}"',p1).group(1)
    val_d = val_d.replace("\"","\\\"")
    print val_d
    val_new = pstart+"\"{"+val_d+"}\""+pend

    print val_new
    print type(val_new)
    r = requests.post(url=url, headers=headers, json=json.loads(val_new), timeout=8)
    # #
    print r.text