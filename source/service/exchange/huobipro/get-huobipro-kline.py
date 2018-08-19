# version 2018-08-19 10:11
import websocket
import threading
import time
import json
from chengutil import mysqlutil, util, CommonApi
import sys

try:
    import thread
except ImportError:
    import _thread as thread
import os

TABLE = 'huobipro'
SYMBOLS = {}

# 获取K线的初始日期
initDateStr = '2018-1-1 00:00:00'
# 已保存数据的总数
historySaveCount = 0
# websocket 连接对象
ws = 0
# K线周期
periods = {
    '1min': 60, '5min': 60 * 2, '15min': 60 * 3, '30min': 60 * 4, '60min': 60 * 5,
    '1day': 60 * 15  # x保证一天执行两次 300/20=15次1组*2次*48m=1440m=1day
}
# 定时器
timer = {'1min': False, '5min': False, '15min': False,
         '30min': False, '60min': False, '1day': False}
# 线程是否运行标签
threadRunning = {'1min': False, '5min': False, '15min': False,
                 '30min': False, '60min': False, '1day': False}
# 分批获取K线的当前索引
getKlineCount = {'1min': 0, '5min': 0,
                 '15min': 0, '30min': 0, '60min': 0, '1day': 0}
# 接收到的K线数据数量
repCount = 0
# 进程运行次数
runTime = {'1min': 0, '5min': 0, '15min': 0, '30min': 0, '60min': 0, '1day': 0}
# 交易对完整获取次数
fullTime = {'1min': 0, '5min': 0, '15min': 0,
            '30min': 0, '60min': 0, '1day': 0}


def on_open(ws):
    mysqlutil.log(TABLE, '\n### Connected ###\n')

    global SYMBOLS
    SYMBOLS = CommonApi.get_symbols(TABLE, 'dict')
    mysqlutil.log(TABLE, SYMBOLS)

    # nowTime = int(time.time() * 1000000)

    # def run(*args):
    #     ws.send(
    #         '{"sub": "market.btcusdt.kline.1min","id": "kline_' + str(nowTime) + '"}')

    ts = util.getTimeStamp(initDateStr)

    # 根据周期字典启动定时器
    for key in periods:
        period = periods[key]
        if period == 0:
            continue
        get_kline_timer(period, key, ts)


def get_kline_total():
    db = mysqlutil.init()
    cursor = db.cursor()

    total = -1

    try:

        cursor.execute('SELECT COUNT(_id) FROM xcm_huobipro_kline')
        kdata = cursor.fetchall()
        if len(kdata) != 0:
            total = kdata[0][0]
    except:
        mysqlutil.log(TABLE, '\033[0;30;41m get_kline_total except >>> \033[0m', sys.exc_info()[0])

    if total == -1:
        mysqlutil.log(TABLE, 'get_kline_total error')
        total = 0

    cursor.close()
    db.close()

    return total


# 定时获取K线数据
def get_kline_timer(interval, period, initTimestamp):
    global timer

    # 检查 websocket 是否已经关闭
    if not ws.sock:
        mysqlutil.log(TABLE, '\n### websocket was closed. ###\n')
        timer[period].cancel()
        return

    # get_kline(period, initTimestamp)
    thread.start_new_thread(get_kline, (period, initTimestamp, interval))
    # interval + 60 是给定时器添加 1 分钟的缓冲时间，避免相同周期的进程同时运行。
    timer[period] = threading.Timer(interval + 60, get_kline_timer, [
        interval, period, initTimestamp])
    timer[period].start()


# 获取K线数据
def get_kline(period, initTimestamp, sleep):
    if not ws.sock:
        mysqlutil.log(TABLE, '\n### websocket was closed. ###\n')
        timer[period].cancel()
        return

    # 防止相同周期的进程重复运行
    if threadRunning[period]:
        mysqlutil.log(TABLE, 'threadRunning', period, 'was running.')
        return

    # 延迟执行
    time.sleep(sleep)
    threadRunning[period] = True
    global runTime
    runTime[period] += 1

    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        # 获取交易对清单，循环请求K线数据。
        cursor.execute("SELECT symbol FROM xcm_huobipro_symbol ORDER BY _id ASC")
        rows = cursor.fetchall()

        nowTime = int(time.time() * 1000000)

        global getKlineCount
        mysqlutil.log(TABLE, 'get_kline rows len >>>', len(rows))

        count = 0
        for r in rows:

            # 分批获取数据。火币Pro交易所的 WebSocket 似乎不能同时请求太多，单次请求的上限似乎为 27 个。
            count += 1
            if getKlineCount[period] >= count:
                continue

            symbol = r[0]
            # mysqlutil.log(TABLE, 'symbol >>>', symbol)

            # 获取数据表中最后一条记录，获取它的时间戳，作为请求的开始时间戳。
            sql = """
            SELECT ts 
            FROM xcm_huobipro_kline 
            WHERE period=%s AND symbol=%s
            ORDER BY ts DESC LIMIT 1"""
            # mysqlutil.log(TABLE, sql)
            cursor.execute(sql, (period, symbol))
            kdata = cursor.fetchall()
            if len(kdata) != 0:
                # mysqlutil.log(TABLE, 'get_kline', period, 'kdata >>>', kdata)
                fromTimeStamp = kdata[0][0] + 1
            else:
                fromTimeStamp = initTimestamp

            req = '{"req": "market.%s.kline.%s","id": "kline_%d","from":%d}' % (
                symbol, period, nowTime, fromTimeStamp)
            mysqlutil.log(TABLE, '\033[0;30;44m get_kline req >>> \033[0m', req)
            mysqlutil.log(TABLE, '\033[0;30;43m get_kline req symbol >>> \033[0m', symbol)
            mysqlutil.log(TABLE, '\033[0;30;43m get_kline req period >>> \033[0m', period)
            mysqlutil.log(TABLE, '\033[0;30;43m get_kline req fromTimeStamp >>> \033[0m',
                          util.getLocaleDateStrBy10(fromTimeStamp))

            if not ws.sock:
                mysqlutil.log(TABLE, '\n### websocket was closed. ###\n')
                timer[period].cancel()
                return
            ws.send(req)
            mysqlutil.log(TABLE, 'get_kline count', period + ' >>>', count)  # 执行进度。已经将数据库表中的交易对清单执行到第几个。

            if count % 20 == 0:
                getKlineCount[period] = count
                break

            time.sleep(1)

        # 如果一组交易对已经处理完，重置获取计数。
        if count == len(rows):
            getKlineCount[period] = 0
            fullTime[period] += 1

        mysqlutil.log(TABLE, '\033[0;30;42m getKlineCount', period + ' >>> \033[0m', getKlineCount[period])

    except:
        mysqlutil.log(TABLE, '\033[0;30;41m get_kline except >>> \033[0m')
        filename = os.path.basename(sys.argv[0]).split(".")[0]
        util.printExcept(filename)
    finally:
        cursor.close()
        db.close()

    # 恢复进程未运行的标签
    threadRunning[period] = False

    mysqlutil.log(TABLE, '==========> runTime  ===> ', runTime)
    mysqlutil.log(TABLE, '==========> fullTime ===> ', fullTime)


def get_kline_by_symbol(period, initTimestamp, symbol):
    if not ws.sock:
        mysqlutil.log(TABLE, '\n### websocket was closed. ###\n')
        timer[period].cancel()
        return

    db = mysqlutil.init()
    cursor = db.cursor()

    try:
        # 获取数据表中最后一条记录，获取它的时间戳，作为请求的开始时间戳。
        sql = """
        SELECT ts 
        FROM xcm_huobipro_kline 
        WHERE period=%s AND symbol=%s
        ORDER BY ts DESC LIMIT 1"""
        # mysqlutil.log(TABLE, sql)
        cursor.execute(sql, (period, symbol))
        kdata = cursor.fetchall()
        if len(kdata) != 0:
            mysqlutil.log(TABLE, 'get_kline_by_symbol kdata >>>', kdata)
            fromTimeStamp = kdata[0][0] + 1
        else:
            fromTimeStamp = initTimestamp

        nowTime = int(time.time() * 1000000)
        req = '{"req": "market.%s.kline.%s","id": "kline_%d","from":%d}' % (
            symbol, period, nowTime, fromTimeStamp)
        mysqlutil.log(TABLE, 'get_kline_by_symbol req >>>', req)
        mysqlutil.log(TABLE, '\033[0;30;43m get_kline_by_symbol req symbol >>> \033[0m', symbol)
        mysqlutil.log(TABLE, '\033[0;30;43m get_kline_by_symbol req period >>> \033[0m', period)
        mysqlutil.log(TABLE, '\033[0;30;43m get_kline_by_symbol req fromTimeStamp >>> \033[0m',
                      util.getLocaleDateStrBy10(fromTimeStamp))
        ws.send(req)
    except:
        mysqlutil.log(TABLE, '\033[0;30;41m get_kline_by_symbol except >>> \033[0m')
        filename = os.path.basename(sys.argv[0]).split(".")[0]
        util.printExcept(filename)
    finally:
        cursor.close()
        db.close()


def on_message(ws, message):
    message = util.gzip_uncompress(message)
    message = message.decode('ascii')

    # mysqlutil.log(TABLE, '==========> message ===> ' + message)

    jsonObj = json.loads(message)

    if ('ping' in jsonObj) == True:
        # 回应心跳检测
        pong = '{"pong":' + str(jsonObj['ping']) + '}'
        mysqlutil.log(TABLE, '==========> ping ===> ' + str(jsonObj['ping']))
        ws.send(pong)
    elif ('ch' in jsonObj) == True:
        # 将交易对的实时 kline 写入数据表中
        result = insert_huobipro_kline(message)
        mysqlutil.log(TABLE, result, util.getLocaleDateStr(jsonObj['ts']))
    elif ('rep' in jsonObj) == True:

        data = jsonObj['data']
        mysqlutil.log(TABLE, '\033[0;30;44m on_message rep data len >>> \033[0m', format(len(data), ','))
        mysqlutil.log(TABLE, '\033[0;30;44m on_message rep >>> \033[0m', jsonObj['rep'])
        # 如果返回的数据量为零，代表没有更多的数据。这时，将终止请求。
        if len(data) == 0:
            return

        # 将交易对的历史 kline 写入表中
        result = insert_huobipro_kline_history(message)
        # 监测写入数据的数量
        if type(result) == int:
            global historySaveCount
            historySaveCount += result
            mysqlutil.log(TABLE, 'historySaveCount >>>', format(historySaveCount, ','))

        chanel = jsonObj['rep']
        chanel = chanel.split('.')
        period = chanel[3]
        symbol = chanel[1]

        mysqlutil.log(TABLE, 'on_message insert_huobipro_kline_history',
                      period, 'result >>>', result)

        # 监测收到多少次数据
        global repCount
        repCount += 1
        mysqlutil.log(TABLE, 'on_message repCount >>>', format(repCount, ','))

        # 获取最后一条K线的时间，继续发送请求，获取下一组数据。
        lastElemIndex = len(data) - 1
        nextTimestamp = data[lastElemIndex]['id'] + 1
        # mysqlutil.log(TABLE, nextTimestamp)
        get_kline_by_symbol(period, nextTimestamp, symbol)
    else:
        pass


def insert_huobipro_kline(klineStr):
    mysqlutil.log(TABLE, klineStr)
    klineObj = json.loads(klineStr)

    if 'tick' not in klineObj:
        return False

    klineObj = convert_kline_json(klineStr)
    tick = klineObj['tick']

    # 初始化数据库连接
    db = mysqlutil.init()
    cursor = db.cursor()

    # 定义 _id
    nowTime = time.time()
    nowTime *= 10000000

    try:
        sql = """
            INSERT INTO 
            `xcm_huobipro_kline` 
            (_id,symbol,base,quote,period,ts,
            ts,amount,count,open,close,
            low,high,vol) 
            VALUES 
            (%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s)
            """
        cursor.execute(sql, (
            nowTime, tick['symbol'], tick['base'], tick['quote'], tick['period'], klineObj['ts'],
            tick['id'], tick['amount'], tick['count'], tick['open'], tick['close'],
            tick['low'], tick['high'], tick['vol']))
        db.commit()
    finally:
        pass

    # 关闭数据库连接
    cursor.close()
    db.close()

    return True


def insert_huobipro_kline_history(klineStr):
    mysqlutil.log(TABLE, klineStr)
    klineObj = json.loads(klineStr)

    if 'data' not in klineObj:
        return False

    klineObj = json.loads(klineStr)
    data = klineObj['data']

    # 初始化数据库连接
    db = mysqlutil.init()
    cursor = db.cursor()

    sql = '%s'
    param = ('not set')
    tick = 'not set'

    try:

        for tick in data:
            tick = convert_kline_json_by_ticker(tick, klineObj['rep'])
            # mysqlutil.log(TABLE,tick)
            # 定义 _id
            nowTime = time.time()
            nowTime *= 10000000

            sql = '''INSERT INTO `xcm_huobipro_kline` 
              (_id, symbol, base, quote, period, ts, amount, `count`, `open`, `close`, low, high, vol) 
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            param = (
                nowTime, tick['symbol'], tick['base'], tick['quote'], tick['period'],
                tick['id'], tick['amount'], tick['count'], tick['open'], tick['close'],
                tick['low'], tick['high'], tick['vol'])
            # print(param)
            cursor.execute(sql, param)

        db.commit()

        return len(data)
    except:
        ex = sys.exc_info()
        mysqlutil.log(TABLE, '\033[0;30;41m get_kline except >>> \033[0m \nEX_NAME:', ex[0], '\nEX_VAL:', ex[1], '\nEX_TRACK:\n', ex[2])
        mysqlutil.log(TABLE, '\033[0;30;43m get_kline except sql symbol >>> \033[0m', tick['symbol'])
        mysqlutil.log(TABLE, '\033[0;30;43m get_kline except sql period >>> \033[0m', tick['period'])
        mysqlutil.log(TABLE, '\033[0;30;43m get_kline except sql ts >>> \033[0m', util.getLocaleDateStrBy10(tick['id']))
        # mysqlutil.log(TABLE,'get_kline except sql >>>', sql%param)
        util.printExcept()

    # 关闭数据库连接
    cursor.close()
    db.close()

    return True


# 将 kline 数据调整成数据库表需要的格式
def convert_kline_json(klineStr):
    klineObj = json.loads(klineStr)
    tick = klineObj['tick']
    ch = klineObj['ch'].split('.')
    symbol = ch[1]
    period = ch[3]
    tick['symbol'] = symbol
    global SYMBOLS
    tick['base'] = SYMBOLS[symbol]['base']
    tick['quote'] = SYMBOLS[symbol]['quote']
    tick['period'] = period
    return klineObj


def convert_kline_json_by_ticker(tick, chanel):
    chanel = chanel.split('.')
    symbol = chanel[1]
    period = chanel[3]
    tick['symbol'] = symbol
    global SYMBOLS
    tick['base'] = SYMBOLS[symbol]['base']
    tick['quote'] = SYMBOLS[symbol]['quote']
    tick['period'] = period
    return tick


def on_error(ws, error):
    mysqlutil.log(TABLE, error)


def on_close(ws):
    mysqlutil.log(TABLE, "\n### Closed ###\n")
    # 关闭后重新启动
    init()


def init():
    websocket.enableTrace(True)
    global ws
    ws = websocket.WebSocketApp(
        "wss://api.huobi.pro/ws", on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()


if __name__ == "__main__":

    print('\n### 正在获取当前K线数据总数 ###\n')
    historySaveCount = get_kline_total()
    print('### 当前K线数据总数获取完毕 ###')
    print('historySaveCount >>>', format(historySaveCount, ','), '\n')

    init()
    # util.daemonize(init)
