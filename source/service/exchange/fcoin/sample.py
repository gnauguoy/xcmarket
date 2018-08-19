import fcoin


api = fcoin.authorize('key', 'secret')
print(api.server_time())

symbols = api.symbols()
print('symbols len >>>', len(symbols['data']))

kdata = api.market.get_candle_info('M1', 'btcusdt')
print('kdata len >>>', len(kdata['data']))

ticker = api.market.get_ticker('btcusdt')
print('ticker >>>', ticker)
