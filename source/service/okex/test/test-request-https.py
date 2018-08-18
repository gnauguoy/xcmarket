import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
# url = 'https://www.python.org'
# url = 'https://www.okex.com/api/v1/kline.do?symbol=ltc_btc&type=1min'
url = 'https://www.okex.com/api/v1/ticker.do?symbol=ltc_btc'
# url = 'https://www.ip.cn'
# url = 'http://www.baidu.com'
headers = {"Content-type": "application/x-www-form-urlencoded",
           'Accept-Language': 'zh-CN,zh;q=0.8',
           'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Connection": "close",
           "Cache-Control": "no-cache"}
req = urllib.request.Request(url, None, headers)
response = urllib.request.urlopen(req)
content = response.read().decode('utf-8')
print(content)
