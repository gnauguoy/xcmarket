import json, sys
import socket
from urllib import request

from chengutil import mysqlutil, util

db = mysqlutil.init()
cursor = db.cursor()


# f = open('huobi_symbol.json')
# content = f.read()
# # print(content)
# f.close()

def get_huobipro_symbol():
    try:
        url = 'https://api.huobi.pro/v1/common/symbols'
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
        symbol = json.loads(content)
        print('data len >>>', len(symbol))
        return symbol
    except:
        util.printExcept()
        return False


def import_huobipro_symbol():
    symbol = get_huobipro_symbol()
    symbol = symbol['data']
    print(len(symbol))

    try:
        for s in symbol:
            sql = '''
                SELECT COUNT(_id) FROM `xcm_huobipro_symbol` WHERE symbol=%s'''
            cursor.execute(sql, (s['symbol']))
            rows = cursor.fetchall()
            if rows[0][0] > 0:
                continue

            sql = '''
            INSERT INTO `xcm_huobipro_symbol` 
            (base,quote,price_precision,
            amount_precision,symbol,symbol_partition) 
            VALUES (%s,%s,%s,%s,%s,%s)'''
            cursor.execute(sql, (
                s['base-currency'], s['quote-currency'], s['price-precision'],
                s['amount-precision'], s['symbol'], s['symbol-partition']))

        db.commit()
        print('### Successed ###')
    except:
        util.printExcept(target='import-huobipro-symbol > import_huobipro_symbol')
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    import_huobipro_symbol()