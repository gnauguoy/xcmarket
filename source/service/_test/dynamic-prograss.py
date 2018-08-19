import os
import sys
import time
while 1:
    s = "\r[%.3f]" % (time.time())
    msg = bytes(s, encoding="utf8")
    os.write(1, msg)
    sys.stdout.flush()
    time.sleep(1)