import _thread, okexklineutil


_thread.start_new_thread(okexklineutil.get_kline, ('1min',))
_thread.start_new_thread(okexklineutil.get_kline, ('3min',))
_thread.start_new_thread(okexklineutil.get_kline, ('5min',))

input('### 服务正在运行 ###')
