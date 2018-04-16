#coding=utf-8
import sys
import json
import datetime
import time
import re
sys.path.append("./base")
from base import feeder
from base import price_assetfun_get_price


#等待秒为10的整数倍的时刻
def wait_for_time(now_second):
    tail = now_second%10
    if tail != 0:
        time.sleep(10-tail)


def main():
    now_second = datetime.datetime.now().strftime("%S")
    now_second = int(now_second)
    wait_for_time(now_second)

    feed_process = feeder.Feeder("config.json")
    feed_process.start()
    

if __name__ == '__main__':
    main()
