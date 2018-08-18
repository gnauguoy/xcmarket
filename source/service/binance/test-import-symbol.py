import socket
import ssl
from urllib import request
import re

url = 'https://www.binance.com/cn'
# url = 'https://www.googl.com'
socket.setdefaulttimeout(20)
ssl._create_default_https_context = ssl._create_unverified_context
headers = {
    # "Content-type": "application/x-www-form-urlencoded",
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "close",
    "Cache-Control": "no-cache"
}
req = request.Request(url, None, headers)
response = request.urlopen(req)
content = response.read().decode('utf-8')
# print(content)

regex = r'\<a href="\/cn\/trade\/([A-Z_]+?)"\>'
matchObj = re.findall(regex, content, re.I)

print(len(matchObj))

symbols = []

for s in matchObj:
    symbols.append(s)

print(symbols)