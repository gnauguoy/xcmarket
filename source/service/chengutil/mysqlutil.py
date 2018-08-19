# version 2018-08-18 06:18
import pymysql, json, time
from chengutil import util
import sys
import datetime


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
    nowTime *= 10000000

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
            nowTime *= 10000000

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


def log(tableName, *param):
    print(logToDB(tableName, param))


def logWithList(table, list, show=False):
    logContent = logToDB(table, list)
    if show:
        print(logContent)


def logToDB(tableName, param):
    db = init()
    cursor = db.cursor()

    logContent = ''

    try:

        for s in param:
            s = str(s)
            logContent += s + ' '

        if logContent != '':
            nowTime = time.time() * 10000000

            sql = '''
            INSERT INTO xcm_log_%s (ts,content) VALUES ('%s','%s')''' % (
            tableName, nowTime, logContent.replace('\'', '\\\''))
            cursor.execute(sql, ())
            db.commit()
            return logContent
    except:
        util.printExcept()
    finally:
        cursor.close()
        db.close()

    return False


def logToExcept(content, target='', msg='', show=True, table='exception'):
    db = init()
    cursor = db.cursor()

    nowTime = str(time.time() * 10000000)
    logContent = 'target: ' + target + '\nmessage: ' + msg + '\ntimestamp: ' + nowTime + '\ncontent: ' + content + '\n'
    if show:
        print('\033[0;30;41m' + logContent + '\033[0m')

    try:
        sql = '''
        INSERT INTO xcm_log_%s (ts, content, target, msg) VALUES ('%s', '%s', '%s', '%s')''' % (
        table, nowTime, content.replace('\'', '\\\''), target, msg)
        cursor.execute(sql, ())
        db.commit()
        return True
    except:
        util.logToFile(logContent, 'logToExcept_Error_')
    finally:
        cursor.close()
        db.close()

    return False
