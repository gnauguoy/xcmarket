# final date: 2018-07-14 16:22
# desc: 此版本已经可以定时循环获取所有交易对 1min 的K线数据，并保存在数据库中。

import websocket
import threading
import time
import json
import util
import mysqlutil
import sys


def on_open(ws):

    print('\n### connected ###\n')

    nowTime = int(time.time() * 1000000)

    def run(*args):
        ws.send(
            '{"sub": "market.btcusdt.kline.1min","id": "kline_' + str(nowTime) + '"}')

    ts = util.getTimeStamp('2018-1-1 00:00:00')
    get1MinKlineTimer(60, ws, ts)


global timer

# 定时获取 1min K线数据
def get1MinKlineTimer(interval, ws, initTimestamp):
    
    global timer

    # 检查 websocket 是否已经关闭
    if not ws.sock:
        print('\n### websocket was closed. ###\n')
        timer.cancel()
        return

    get1MinKline(ws, initTimestamp)
    timer = threading.Timer(interval, get1MinKlineTimer, [interval, ws, initTimestamp])
    timer.start()


getKlineCount = 0

# 获取 1min K线数据
def get1MinKline(ws, initTimestamp):

    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        # 获取交易对清单，循环请求K线数据。
        cursor.execute("SELECT symbol FROM xcm_huobi_symbol ORDER BY _id ASC")
        rows = cursor.fetchall()

        nowTime = int(time.time() * 1000000)

        global getKlineCount
        print('get1MinKline rows len:', len(rows))

        count = 0
        for r in rows:

            # 分批获取数据。火币Pro交易所的 WebSocket 似乎不能同时请求太多，单次请求的上限似乎为 27 个。
            count += 1
            if getKlineCount >= count:
                continue

            symbol = r[0]
            # print('symbol:', symbol)

            # 获取数据表中最后一条记录，获取它的时间戳，作为请求的开始时间戳。
            sql = """
            SELECT id 
            FROM xcm_huobi_kline_history 
            WHERE period='1min' AND symbol=%s
            ORDER BY id DESC LIMIT 1"""
            # print(sql)
            cursor.execute(sql, (symbol))
            kdata = cursor.fetchall()
            if len(kdata) != 0:
                print('get1MinKline kdata:', kdata)
                fromTimeStamp = kdata[0][0] + 1
            else:
                fromTimeStamp = initTimestamp

            req = '{"req": "market.%s.kline.1min","id": "kline_%d","from":%d}'%(symbol, nowTime, fromTimeStamp)
            print('get1MinKline req:', req)
            ws.send(req)
            print('get1MinKline count:', count)

            if count % 20 == 0:
                getKlineCount = count
                break

            time.sleep(1)

        # 如果一组交易对已经处理完，重置获取计数。
        if count == len(rows):
            getKlineCount = 0

        print('getKlineCount:', getKlineCount)

    except:
        print('get1MinKline except:', sys.exc_info()[0])

    cursor.close()
    db.close()

def get1MinKlineBySymbol(ws, initTimestamp, symbol):

    db = mysqlutil.init()
    cursor = db.cursor()

    try:
        # 获取数据表中最后一条记录，获取它的时间戳，作为请求的开始时间戳。
        sql = """
        SELECT id 
        FROM xcm_huobi_kline_history 
        WHERE period='1min' AND symbol=%s
        ORDER BY id DESC LIMIT 1"""
        # print(sql)
        cursor.execute(sql, (symbol))
        kdata = cursor.fetchall()
        if len(kdata) != 0:
            print('get1MinKlineBySymbol kdata:', kdata)
            fromTimeStamp = kdata[0][0] + 1
        else:
            fromTimeStamp = initTimestamp

        nowTime = int(time.time() * 1000000)
        req = '{"req": "market.%s.kline.1min","id": "kline_%d","from":%d}'%(symbol, nowTime, fromTimeStamp)
        print('get1MinKlineBySymbol req:', req)
        ws.send(req)
    except:
        print('get1MinKlineBySymbol except:', sys.exc_info()[0])

    cursor.close()
    db.close()

historySaveCount = 0
repCount = 0

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
        print('on_message rep data len:', len(data))
        # 如果返回的数据量为零，代表没有更多的数据。这时，将终止请求。
        if len(data) == 0:
            return
        
        # 将交易对的历史 kline 写入表中
        result = mysqlutil.insertHuobiProKlineHistory(message)
        # 监测写入数据的数量
        if type(result) == int:
            global historySaveCount
            historySaveCount += result
            print('historySaveCount:', historySaveCount)
        print('on_message insertHuobiProKlineHistory result:', result)
        
        # 监测收到多少次数据
        global repCount
        repCount += 1
        print('on_message repCount:', repCount)

        # 获取最后一条K线的时间，继续发送请求，获取下一组数据。
        lastElemIndex = len(data) -1
        nextTimestamp = data[lastElemIndex]['id'] + 1
        # print(nextTimestamp)
        chanel = jsonObj['rep']
        chanel = chanel.split('.')
        symbol = chanel[1]
        get1MinKlineBySymbol(ws, nextTimestamp, symbol)
    else:
        pass


def on_error(ws, error):
    print(error)


def on_close(ws):
    timer.cancel()
    print("\n### closed ###\n")


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "wss://api.huobi.pro/ws", on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
