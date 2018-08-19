import _thread
import time

lock = False


def thread1():
    global lock
    lock = _thread.allocate_lock()
    lock.acquire()
    time.sleep(5)
    lock.release()

def thread2():
    print(type(lock))
    while lock.locked():
        print('thread1 is locking.')
        time.sleep(1)
    print('thread1 was released.')

_thread.start_new_thread(thread1, ())
_thread.start_new_thread(thread2, ())

while True:
    time.sleep(10)
    if lock.locked() == False:
        break