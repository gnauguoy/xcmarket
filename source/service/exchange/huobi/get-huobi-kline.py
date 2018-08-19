# version 2018-07-18 04:18
import websocket
import threading
import time
import json
from chengutil import mysqlutil, util
import sys
try:
    import thread
except ImportError:
    import _thread as thread
import os

# 获取K线的初始日期
initDateStr = '2018-1-1 00:00:00'
# 已保存数据的总数
historySaveCount = 0
# websocket 连接对象
ws = 0
# K线周期
periods = {
    '1min': 60, '5min': 60*2, '15min': 60*3, '30min': 60*4, '60min': 60*5,
    '1day': 60*15  # x保证一天执行两次 300/20=15次1组*2次*48m=1440m=1day
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

    print('\n### connected ###\n')

    # nowTime = int(time.time() * 1000000)

    # def run(*args):
    #     ws.send(
    #         '{"sub": "market.btcusdt.kline.1min","id": "kline_' + str(nowTime) + '"}')

    global historySaveCount
    historySaveCount = mysqlutil.get_kline_history_total()

    ts = util.getTimeStamp(initDateStr)

    # 根据周期字典启动定时器
    for key in periods:
        period = periods[key]
        if period == 0:
            continue
        get_kline_timer(period, key, ts)


# 定时获取K线数据
def get_kline_timer(interval, period, initTimestamp):

    global timer

    # 检查 websocket 是否已经关闭
    if not ws.sock:
        print('\n### websocket was closed. ###\n')
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
        print('\n### websocket was closed. ###\n')
        timer[period].cancel()
        return

    # 防止相同周期的进程重复运行
    if threadRunning[period]:
        print('threadRunning', period, 'was running.')
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
        cursor.execute("SELECT symbol FROM xcm_huobi_symbol ORDER BY _id ASC")
        rows = cursor.fetchall()

        nowTime = int(time.time() * 1000000)

        global getKlineCount
        print('get_kline rows len >>>', len(rows))

        count = 0
        for r in rows:

            # 分批获取数据。火币Pro交易所的 WebSocket 似乎不能同时请求太多，单次请求的上限似乎为 27 个。
            count += 1
            if getKlineCount[period] >= count:
                continue

            symbol = r[0]
            # print('symbol >>>', symbol)

            # 获取数据表中最后一条记录，获取它的时间戳，作为请求的开始时间戳。
            sql = """
            SELECT id 
            FROM xcm_huobi_kline_history 
            WHERE period=%s AND symbol=%s
            ORDER BY id DESC LIMIT 1"""
            # print(sql)
            cursor.execute(sql, (period, symbol))
            kdata = cursor.fetchall()
            if len(kdata) != 0:
                # print('get_kline', period, 'kdata >>>', kdata)
                fromTimeStamp = kdata[0][0] + 1
            else:
                fromTimeStamp = initTimestamp

            req = '{"req": "market.%s.kline.%s","id": "kline_%d","from":%d}' % (
                symbol, period, nowTime, fromTimeStamp)
            print('\033[0;30;44m get_kline req >>> \033[0m', req)
            print('\033[0;30;43m get_kline req symbol >>> \033[0m', symbol)
            print('\033[0;30;43m get_kline req period >>> \033[0m', period)
            print('\033[0;30;43m get_kline req fromTimeStamp >>> \033[0m', util.getLocaleDateStrBy10(fromTimeStamp))

            if not ws.sock:
                print('\n### websocket was closed. ###\n')
                timer[period].cancel()
                return
            ws.send(req)
            print('get_kline count', period + ' >>>', count) # 执行进度。已经将数据库表中的交易对清单执行到第几个。

            if count % 20 == 0:
                getKlineCount[period] = count
                break

            time.sleep(1)

        # 如果一组交易对已经处理完，重置获取计数。
        if count == len(rows):
            getKlineCount[period] = 0
            fullTime[period] += 1

        print('\033[0;30;42m getKlineCount', period + ' >>> \033[0m', getKlineCount[period])

    except:
        print('\033[0;30;41m get_kline except >>> \033[0m')
        filename = os.path.basename(sys.argv[0]).split(".")[0]
        util.printExcept(filename)
    finally:
        cursor.close()
        db.close()

    # 恢复进程未运行的标签
    threadRunning[period] = False

    print('==========> runTime  ===> ', runTime)
    print('==========> fullTime ===> ', fullTime)


def get_kline_by_symbol(period, initTimestamp, symbol):

    if not ws.sock:
        print('\n### websocket was closed. ###\n')
        timer[period].cancel()
        return

    db = mysqlutil.init()
    cursor = db.cursor()

    try:
        # 获取数据表中最后一条记录，获取它的时间戳，作为请求的开始时间戳。
        sql = """
        SELECT id 
        FROM xcm_huobi_kline_history 
        WHERE period=%s AND symbol=%s
        ORDER BY id DESC LIMIT 1"""
        # print(sql)
        cursor.execute(sql, (period, symbol))
        kdata = cursor.fetchall()
        if len(kdata) != 0:
            print('get_kline_by_symbol kdata >>>', kdata)
            fromTimeStamp = kdata[0][0] + 1
        else:
            fromTimeStamp = initTimestamp

        nowTime = int(time.time() * 1000000)
        req = '{"req": "market.%s.kline.%s","id": "kline_%d","from":%d}' % (
            symbol, period, nowTime, fromTimeStamp)
        print('get_kline_by_symbol req >>>', req)
        print('\033[0;30;43m get_kline_by_symbol req symbol >>> \033[0m', symbol)
        print('\033[0;30;43m get_kline_by_symbol req period >>> \033[0m', period)
        print('\033[0;30;43m get_kline_by_symbol req fromTimeStamp >>> \033[0m', util.getLocaleDateStrBy10(fromTimeStamp))
        ws.send(req)
    except:
        print('\033[0;30;41m get_kline_by_symbol except >>> \033[0m')
        filename = os.path.basename(sys.argv[0]).split(".")[0]
        util.printExcept(filename)
    finally:
        cursor.close()
        db.close()


def on_message(ws, message):

    message = util.gzip_uncompress(message)
    message = message.decode('ascii')

    # print('==========> message ===> ' + message)

    jsonObj = json.loads(message)

    if ('ping' in jsonObj) == True:
        # 回应心跳检测
        pong = '{"pong":' + str(jsonObj['ping']) + '}'
        print('==========> ping ===> ' + str(jsonObj['ping']))
        ws.send(pong)
    elif ('ch' in jsonObj) == True:
        # 将交易对的实时 kline 写入数据表中
        result = mysqlutil.insertHuobiProKline(message)
        print(result, util.getLocaleDateStr(jsonObj['ts']))
    elif ('rep' in jsonObj) == True:

        data = jsonObj['data']
        print('\033[0;30;44m on_message rep data len >>> \033[0m', len(data))
        print('\033[0;30;44m on_message rep >>> \033[0m', jsonObj['rep'])
        # 如果返回的数据量为零，代表没有更多的数据。这时，将终止请求。
        if len(data) == 0:
            return

        # 将交易对的历史 kline 写入表中
        result = mysqlutil.insertHuobiProKlineHistory(message)
        # 监测写入数据的数量
        if type(result) == int:
            global historySaveCount
            historySaveCount += result
            print('historySaveCount >>>', historySaveCount)

        chanel = jsonObj['rep']
        chanel = chanel.split('.')
        period = chanel[3]
        symbol = chanel[1]

        print('on_message insertHuobiProKlineHistory',
              period, 'result >>>', result)

        # 监测收到多少次数据
        global repCount
        repCount += 1
        print('on_message repCount >>>', repCount)

        # 获取最后一条K线的时间，继续发送请求，获取下一组数据。
        lastElemIndex = len(data) - 1
        nextTimestamp = data[lastElemIndex]['id'] + 1
        # print(nextTimestamp)
        get_kline_by_symbol(period, nextTimestamp, symbol)
    else:
        pass


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("\n### closed ###\n")
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
    init()
    # util.daemonize(init)
