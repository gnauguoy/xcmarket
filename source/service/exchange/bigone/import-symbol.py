import socket
from urllib import request
import json
from chengutil import mysqlutil, util


def request_bigone_symbol():
    try:
        url = 'https://big.one/api/v2/markets'
        print(url)
        socket.setdefaulttimeout(20)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0"
        }
        req = request.Request(url, None, headers)
        response = request.urlopen(req)
        content = response.read().decode('utf-8')

        print(content)
        symbol = json.loads(content)
        symbol = symbol['data']
        print('data len >>>', len(symbol))
        return symbol
    except:
        util.printExcept()
        return False


db = mysqlutil.init()
cursor = db.cursor()

try:

    symbol = request_bigone_symbol()
    for s in symbol:
        sql = '''
        SELECT COUNT(_id) FROM `xcm_bigone_symbol` WHERE symbol=%s'''
        cursor.execute(sql, (s['name']))
        rows = cursor.fetchall()
        if rows[0][0] > 0:
            continue

        print('symbol >>>', s)
        sql = '''
        INSERT INTO `xcm_bigone_symbol` 
        (symbol, base, base_scale, quote, quote_scale) 
        VALUES (%s, %s, %s, %s, %s)'''
        param = (s['name'], s['baseAsset']['symbol'], s['baseScale'], s['quoteAsset']['symbol'], s['quoteScale'])
        print(param)
        cursor.execute(sql, param)

    db.commit()
    print('\n### successed ###\n')
except:
    util.printExcept()
finally:
    cursor.close()
    db.close()
