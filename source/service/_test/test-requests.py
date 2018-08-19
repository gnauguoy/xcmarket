import requests
import time, json

url = "https://api.bitfinex.com/v1/pubticker/btcusd"
response = requests.get(url)
print(response.text)
data = json.loads(response.text)
print(float(data['last_price'])*6.8269)
print(float(data['last_price'])*6.2755)

url = "https://api.bitfinex.com/v1/lends/usd?limit_lends=1"
response = requests.request("GET", url)
print(response.text)
data = json.loads(response.text)
print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[0]['timestamp'])))