# version 2018-08-19 17:53
import json
import socket
from urllib import request

from chengutil import mysqlutil, util


def get_symbols(table, format='tuple'):

    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        sql = 'SELECT symbol, base, quote FROM xcm_%s_symbol' % (table)
        cursor.execute(sql)
        symbols = cursor.fetchall()
        if format == 'dict':
            dict = {}
            for s in symbols:
                dict[s[0]] = {'base': s[1], 'quote': s[2]}
            symbols = dict
        return symbols
    except:
        util.printExcept()
    finally:
        cursor.close()
        db.close()

    return False

def get_ticker(restUrl):
    try:
        url = restUrl
        # print(url)
        socket.setdefaulttimeout(20)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0"
        }
        req = request.Request(url, None, headers)
        response = request.urlopen(req)
        content = response.read().decode('utf-8')

        # print(content)
        content = json.loads(content)
        # print('data len >>>', len(content))
        return content
    except:
        util.printExcept(target='CommonApi > get_ticker')
        return False