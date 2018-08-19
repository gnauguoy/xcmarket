# version 2018-07-18 04:18
from urllib import request, parse
import json
import re
import threading
try:
    import thread
except ImportError:
    import _thread as thread
from chengutil import mysqlutil, util
import time
import os
import sys


def get_sina_rate_usdcny():
    url = 'http://hq.sinajs.cn/rn=1531609137914list=fx_susdcny'
    response = request.urlopen(url)
    content = response.read().decode('gbk')
    # print(content)

    matchObj = re.search(
        r',([^,]*?),美元兑人民币即期汇率', content, re.I)
    usdcny = matchObj.group(1)
    print('美元兑人民币即期汇率 >>>', usdcny)
    print(util.getLocaleDateStrBy10(time.time()))

    return usdcny


def main():

    db = mysqlutil.init()
    cursor = db.cursor()

    try:
        usdcny = get_sina_rate_usdcny()
        
        sql = '''INSERT INTO `xcm_exchange_rate` 
        (base_currency, quote_currency, rate, create_time)
        VALUES
        (%s, %s, %s, %s)'''
        now = int(time.time())
        cursor.execute(sql,('usd', 'cny', usdcny,now))
        rowcount = cursor.rowcount
        if rowcount == 0:
            print('\033[0;30;41m insert exchange rate result >>> \033[0m', rowcount)
        else:
            print('\033[0;30;42m insert exchange rate result >>> \033[0m', rowcount)
            db.commit()
            
    except:
        print('\033[0;30;41m main except >>> \033[0m')
        filename = os.path.basename(sys.argv[0]).split(".")[0]
        util.printExcept(filename)
    finally:
        cursor.close()
        db.close()


def main_timer():
    thread.start_new_thread(main, ())
    timer = threading.Timer(60*2, main_timer)
    timer.start()


if __name__ == '__main__':
    # get_sina_rate_usdcny()
    main_timer()
    # util.daemonize(main_timer)
