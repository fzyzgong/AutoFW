#coding=utf-8
import json
import requests
import urlparse



if __name__ == "__main__":

    '''
    url_path:/rabbit/v1/customer/house/getNewBargainDetailInfo
    method:GET
    headers:{u'TBSAccessToken': '10c20c71afe547548b622dc9613789ba'}
    parameter:sourcetype=99&bargainId=4711456&cityId=605&priceTag=行情参考
    
    
    url_path:/rabbit/v1/customer/newHouse2/houseDetail
    method:GET
    headers:{u'TBSAccessToken': '10c20c71afe547548b622dc9613789ba'}
    parameter:cityId=605&houseId=24190
    <type 'unicode'>

    '''
    url = "https://test02.2boss.cn/rabbit/v1/customer/house/getNewBargainDetailInfo"
    headers = {u'TBSAccessToken': '10c20c71afe547548b622dc9613789ba'}
    parameter1 = u'sourcetype=99&bargainId=4711456&cityId=605&priceTag=行情参考'  #"cityId=605&houseId=24190"

    # p1 = json.dumps(parameter1)
    param_tmp = urlparse.urlparse(parameter1).path
    parameter2 = dict((k, v[0]) for k, v in urlparse.parse_qs(param_tmp).items())
    print parameter2
    r = requests.get(url=url, headers=headers, params=parameter2, timeout=8)
    # r = requests.post(url=url, headers=headers, data=parameter1, timeout=8)

    print r.text
