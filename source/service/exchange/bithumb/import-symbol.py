import socket
from urllib import request
import json
from chengutil import mysqlutil, util


db = mysqlutil.init()
cursor = db.cursor()

try:

    currencies = 'BTC, ETH, DASH, LTC, ETC, XRP, BCH, XMR, ZEC, QTUM, BTG, EOS, ICX, VEN, TRX, ELF, MITH, MCO, OMG, KNC, GNT, HSR, ZIL, ETHOS, PAY, WAX, POWR, LRC, GTO, STEEM, STRAT, ZRX, REP, AE, XEM, SNT, ADA';
    currencies = currencies.split(',')
    for s in currencies:

        s = s.strip('')

        sql = '''
        SELECT COUNT(id) FROM `xcm_bithumb_currency` WHERE currency=%s'''
        cursor.execute(sql, (s))
        rows = cursor.fetchall()
        if rows[0][0] > 0:
            continue

        print('currency >>>', s)
        sql = '''
        INSERT INTO `xcm_bithumb_currency` 
        (currency) 
        VALUES 
        (%s)'''
        param = (s)
        print(param)
        cursor.execute(sql, param)

    db.commit()
    print('\n### successed ###\n')
except:
    util.printExcept()
finally:
    cursor.close()
    db.close()
