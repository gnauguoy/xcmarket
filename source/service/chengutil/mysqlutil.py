# version 2018-08-19 17:53
import pymysql, json, time
from chengutil import util
import sys
import datetime


def init():
    # return pymysql.connect(
    #     host="localhost",
    #     port=8889,
    #     user="root",
    #     passwd="root",
    #     db="xcmarket")
    return pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        passwd="d20180731mysql",
        db="xcmarket")


def getCursor():
    db = init()
    return db.cursor()


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
