import http.client

conn = http.client.HTTPSConnection('www.okex.com', timeout=10)
conn.request("GET", '/api/v1/ticker.do')
response = conn.getresponse()
data = response.read().decode('utf-8')
