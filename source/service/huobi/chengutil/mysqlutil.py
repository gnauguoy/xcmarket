# version 2018-07-17 10:38
import pymysql, json, time
from chengutil import util
import sys

def init():
    return pymysql.connect(
        host="localhost", 
        port=8889, 
        user="root", 
        passwd="root", 
        db="xcmarket")

def getCursor():
    db = init()
    return db.cursor()

def insertHuobiProKline(klineStr):

    klineObj = json.loads(klineStr)

    if 'tick' not in klineObj:
        return False

    klineObj = util.convertKlineJson(klineStr)
    tick = klineObj['tick']

    # 初始化数据库连接
    db = init()
    cursor = db.cursor()

    # 定义 _id
    nowTime = time.time()
    nowTime *= 1000000

    try:
        sql = """
            INSERT INTO 
            `xcm_huobi_kline` 
            (_id,symbol,period,ts,
            id,amount,count,open,close,
            low,high,vol) 
            VALUES 
            (%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s)
            """
        cursor.execute(sql, (
            nowTime, tick['symbol'], tick['period'], klineObj['ts'], 
            tick['id'], tick['amount'], tick['count'], tick['open'], tick['close'], 
            tick['low'], tick['high'], tick['vol']))
        db.commit()
    finally:
        pass

    # 关闭数据库连接
    cursor.close()
    db.close()

    return True

def insertHuobiProKlineHistory(klineStr):

    klineObj = json.loads(klineStr)

    if 'data' not in klineObj:
        return False

    klineObj = json.loads(klineStr)
    data = klineObj['data']

    # 初始化数据库连接
    db = init()
    cursor = db.cursor()

    sql = '%s'
    param = ('not set')
    tick = 'not set'

    try:

        for tick in data:

            tick = util.convertKlineJsonByTick(tick, klineObj['rep'])
            # print(tick)
            # 定义 _id
            nowTime = time.time()
            nowTime *= 1000000

            sql = """
                INSERT INTO 
                `xcm_huobi_kline_history` 
                (_id,symbol,period,
                id,amount,count,open,close,
                low,high,vol) 
                VALUES 
                (%s,%s,%s,
                %s,%s,%s,%s,%s,
                %s,%s,%s)
                """
            param = (
                nowTime, tick['symbol'], tick['period'], 
                tick['id'], tick['amount'], tick['count'], tick['open'], tick['close'], 
                tick['low'], tick['high'], tick['vol'])
            cursor.execute(sql, param)
        
        db.commit()

        return len(data)
    except:
        print('\033[0;30;41m get_kline except >>> \033[0m', sys.exc_info()[0])
        print('\033[0;30;43m get_kline except sql symbol >>> \033[0m', tick['symbol'])
        print('\033[0;30;43m get_kline except sql period >>> \033[0m', tick['period'])
        print('\033[0;30;43m get_kline except sql id >>> \033[0m', util.getLocaleDateStrBy10(tick['id']))
        # print('get_kline except sql >>>', sql%param)
        util.printExcept()

    # 关闭数据库连接
    cursor.close()
    db.close()

    return True

def get_kline_history_total():

    db = init()
    cursor = db.cursor()

    total = -1
    
    try:
        cursor.execute('SELECT COUNT(_id) FROM xcm_huobi_kline_history')
        kdata = cursor.fetchall()
        if len(kdata) != 0:
            total = kdata[0][0]
    except:
        print('\033[0;30;41m get_kline_history_total except >>> \033[0m', sys.exc_info()[0])

    if total == -1:
        print('get_kline_history_total error')
        total = 0

    cursor.close()
    db.close()

    return total
