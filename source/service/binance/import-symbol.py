import socket
from urllib import request
import json
from chengutil import mysqlutil, util


def request_binance_symbol():
    try:
        url = 'https://api.binance.com//api/v1/exchangeInfo'
        print(url)
        socket.setdefaulttimeout(20)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0"
        }
        req = request.Request(url, None, headers)
        response = request.urlopen(req)
        content = response.read().decode('utf-8')

        # print(content)
        symbol = json.loads(content)['symbols']
        print('data len >>>', len(symbol))
        return symbol
    except:
        util.printExcept()
        return False


db = mysqlutil.init()
cursor = db.cursor()

try:

    symbol = request_binance_symbol()
    for s in symbol:
        sql = '''
        SELECT COUNT(_id) FROM `xcm_binance_symbol` WHERE symbol=%s'''
        cursor.execute(sql, (s['symbol']))
        rows = cursor.fetchall()
        if rows[0][0] > 0:
            continue

        print(s)
        sql = '''
        INSERT INTO `xcm_binance_symbol` 
        (symbol,base_asset,base_asset_precision,quote_asset_precision,quote_asset) 
        VALUES (%s,%s,%s,%s,%s)'''
        cursor.execute(sql, (
            s['symbol'], s['baseAsset'], s['baseAssetPrecision'], s['quotePrecision'], s['quoteAsset']))

    db.commit()
    print('\n### successed ###\n')
except:
    util.printExcept()
finally:
    cursor.close()
    db.close()
