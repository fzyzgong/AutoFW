from django.test import TestCase
import requests
# Create your tests here.
def test_post_url():

    # method = "GET"
    # protocol = "HTTPS"
    # domain = "test02.2boss.cn"
    # url = "/rabbit/v1/question/superior/list"
    # headers = ''#{"TBSAccessToken":"d69b6b575a3f40f19d488bdde969c807"}
    # parameter = 'superiorCode=10681955'
    # expected = '{"superiorTel":"18522222222"}'

    r = requests.post("https://test.2boss.cn/superior/v1/question/reply?questionId=390966&content=%E6%94%B6%E5%88%B0%EF%BC%8Cover&userCode=10681765", timeout=8)
    print r.text

if __name__ == "__main__":
    test_post_url()