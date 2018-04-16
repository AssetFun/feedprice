#coding=utf-8
import urllib.request
import socket
import demjson
import math
from decimal import *
import log

_logger= log.LogInit("./log/assetfun_price.log", when="D", log_name="assetfunprice")
price_url = "https://price.assetfun.net/api/strategy/getHistoryPrice?date_start=%d&date_end=%d&symbol=%s_%s&platform=%s"

#通过url获取网页
def GetHtml(url,timeout=5,referer=""):
    socket.setdefaulttimeout(timeout)
    # 要设置请求头，让服务器知道不是机器人
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'
    headers = {'User-Agent': user_agent}
    re=urllib.request.Request(url,headers=headers);
    print(referer)
    if referer != "":
        re.add_header("Referer", referer)
    page = urllib.request.urlopen(re);
    html = page.read()
    return html
def SetInvalidPrices(start_timestamp, end_timestamp):
    prices=[]
    while start_timestamp <= end_timestamp:
        price=[]
        price.append(start_timestamp)
        price.append("-1")
        price.append("-404")
        prices.append(price)
        start_timestamp = start_timestamp + 60
    prices = str(prices)
    prices = bytes(prices, encoding="utf-8")
    return prices

def CompletePrices(start_timestamp,end_timestamp,prices):
    index_timestamp = start_timestamp
    i = 0
    while index_timestamp<=end_timestamp and i < len(prices):
        if index_timestamp != prices[i][0]:
            _logger.info("Price at timstamp(%d) is empty." %(index_timestamp))
            empty_price=[]
            empty_price.append(index_timestamp)
            empty_price.append(-1*pow(10,8))
            prices.insert(i,empty_price)
        i = i+1
        index_timestamp = index_timestamp + 60
    while index_timestamp<=end_timestamp:
        _logger.info("Price at timstamp(%d) is empty." %(index_timestamp))
        empty_price=[]
        empty_price.append(index_timestamp)
        empty_price.append(-1*pow(10,8))
        prices.append(empty_price)
        index_timestamp = index_timestamp + 60
    return prices

'''
@price_quote      交易对分子
@quote_base       交易对分母
@platform         交易平台
@start_timestamp  起始时间戳
@end_timestamp    结束时间戳
@return           返回对应对应时间的对应价格
@note             最终价格是整数形式字符串，要把原来的浮点型数据乘以10^8
'''
def GetPrice(price_quote, price_base, platform, start_timestamp, end_timestamp):
    getcontext().prec = 8
    global price_url
    url  = price_url %(start_timestamp,end_timestamp,price_quote.lower(),price_base.lower(),platform)
    _logger.info(url)
    prices = []
    try:
        prices = GetHtml(url)
    except Exception as e:
        prices = SetInvalidPrices(start_timestamp,end_timestamp)
    _logger.info(prices)
    if str(prices, encoding="utf-8").find("[[") != 0:#b'{"status":-1,"info":null,"msg":"网络错误"}'
        prices = SetInvalidPrices(start_timestamp,end_timestamp)
    prices=demjson.decode(str(prices, encoding="utf-8"))
    for one in prices:
        one[0] = int(one[0]/60)*60
        if one[2] not in ["1","2","3","-2"]:
            _logger.error("price[timestamp=%d] source is unnormal[status:%s]" %(one[0],one[2]))
            one[1]=(-1)*pow(10,8)
        else:
            one[1] = int(Decimal(one[1])*pow(10,8))
        one.pop()
    #处理时间不连续的特殊情况
    if (end_timestamp-start_timestamp)/60+1 != len(prices):
        prices = CompletePrices(start_timestamp,end_timestamp,prices)
    return prices
    
##############################################################################################################################
#https://beta.bitfid.com/api/strategy/getHistoryPrice?date_start=1505881740&date_end=1505881940
def GetLatestPriceTest():
    import time
    import threading
    uint_time=int(time.time())
    uint_time=int(uint_time/60)*60-360
    html=GetPrice("btc","usd","Bitfinex",uint_time,uint_time)
    print(html)
   

    _timer = threading.Timer(10, GetLatestPriceTest)
    _timer.start()
        
    

def main():

#    import demjson
#    ret=GetCoinPrice("BTC",1506431640,1506431640)
#    print(ret)
#    prices=demjson.decode(str(ret, encoding="utf-8"))
#    prices=wrap_coin_prices(prices)
    
    GetLatestPriceTest()

if __name__ == '__main__':
    main()  
    
    
    
