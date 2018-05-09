#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class GetDictParam:
    """
        这是一个解析dict 参数的类
        可以用于多参数的指定key 、 指定key集合解析key
    """
    def __init__(self):
        """
            初始化函数
        """
        pass

    @staticmethod
    def get_value(my_dict, key):#self,
        """
            这是一个递归函数
                amount
                data = {"code": 0, "message": "操作成功", "result": {"amount": 950.0000,
                                                     "totalBaoLiFee": None, "pageNo": 1, "data": [{"goodsId": 100}]}}
        """

        if isinstance(my_dict, dict):
            if my_dict.get(key) or my_dict.get(key) == 0 or my_dict.get(key) == '' and my_dict.get(key) is False:#and my_dict.get(key) is False
                return my_dict.get(key)

            for my_dict_key in my_dict:
                if GetDictParam.get_value(my_dict.get(my_dict_key), key) or GetDictParam.get_value(my_dict.get(my_dict_key), key) is False:#or self.get_value(my_dict.get(my_dict_key), key) is False
                    return GetDictParam.get_value(my_dict.get(my_dict_key), key)

        if isinstance(my_dict, list):
            for my_dict_arr in my_dict:
                if GetDictParam.get_value(my_dict_arr, key) or GetDictParam.get_value(my_dict_arr, key) is False :#or self.get_value(my_dict_arr, key) is False
                    return GetDictParam.get_value(my_dict_arr, key)

    @staticmethod
    def list_for_key_to_dict( my_dict, args_list):#self,
        """
            接收需要解析的dict和 需要包含需要解析my_dict的keys的list
        :param my_dict: 需要解析的字典
        :param args_list: 包含需要解析的key的list字符串
            # list_for_key_to_dict("code", "pageNo", "goodsId", my_dict=dict)
        :return: 一个解析后重新拼装的dict
        """
        result = {}
        if len(args_list) > 0:
            for key in args_list:
                result.update({key: GetDictParam.get_value(my_dict, key)})
        return result

if __name__=="__main__":
    # gdp = GetDictParam()
    # gdp.get_value(dict, get_values_key)
    data = {"code": 0, "message": "操作成功", "result": {"amount": 950.0000,
                                                     "totalBaoLiFee": None, "pageNo": 1, "data": [{"goodsId": 100}]}}
    print(GetDictParam.get_value(data, "goodsId"))

    args_list = ["totalBaoLiFee","amount"]

    print(GetDictParam.list_for_key_to_dict(data, args_list))