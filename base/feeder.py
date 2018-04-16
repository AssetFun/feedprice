#coding=utf-8
import json
import time
import math
import demjson
from grapheneapi import grapheneapi 
import log
import price_assetfun_get_price
import threading
import re

class Feeder(object):
    def __init__(self, self_config_file): 
        self_config=[]
        self.feeded_invalid_price=[] #[2018-1-15 lilianwen add]
        with open(self_config_file,"r",encoding='utf-8') as cf:
            self_config = json.load(cf)
            print(self_config)
            self._host             = self_config["host"]
            self._port             = self_config["port"]
            self._login_account    = self_config["login_account"]
            self._password         = self_config["password"]
            self._time_offset      = self_config["time_offset"]
            self._interval         = self_config["interval"]
            self._logger           = log.LogInit(self_config["log_file"], when="D", log_name="feed_price")
            self._feed_func_config = self_config["feed_price"]
            print(self._feed_func_config)
            if len(self_config["witnesses"]) == 0:
                config_file = self_config["witness_config_file"]
                print(config_file)
                self._witnesses = self.get_witness_ids( config_file )
            else:
                self._witnesses = self_config["witnesses"]
            
        
    def connect(self, host, port, login_account, passwd):
        self._rpc_ro   = grapheneapi.GrapheneAPI(host, port, "", "")
        self._rpc_feed = grapheneapi.GrapheneAPI(host, port, login_account, passwd)
        ret = self._rpc_feed.is_locked()
        if ret:
            self._rpc_feed.unlock(passwd)

    #根据配置文件决定见证人列表
    def get_witness_ids(self, config_file):
        witness_ids=[]
        with open(config_file,"r") as f:    
            lines = f.readlines()#读取全部内容  
            for line in lines:  
                if line.find("witness-id") != -1 and line.find("#") == -1:
                    pattern = re.compile('"(.*)"')
                    witness_ids.append(pattern.findall(line)[0])
        return witness_ids

    def feed_coin(self):
        print("======================================feed one time==============================")
        dyn_prop = self._rpc_ro.get_dynamic_global_properties()
        print(dyn_prop["current_witness"])
        print(self._witnesses)
        self._feed_account = self._rpc_ro.get_witness(dyn_prop["current_witness"])["witness_account"]
        if dyn_prop["current_witness"] in self._witnesses:
            for one_index in self._feed_records:
                if one_index[0] == "1":#只喂数字货币
                    for one_platform in self._feed_records[one_index]:
                        for one_trade_pair in self._feed_records[one_index][one_platform]:
                            self.feed(one_index, one_platform, one_trade_pair)

            #曾经喂过的非法币价的时间戳列表
            give_up=[]
            if self.feeded_invalid_price:
                for one in self.feeded_invalid_price:
                    self._logger.info("Reset coin price")
                    uint_time=int(time.time())
                    if uint_time - one[3] < 300 and uint_time - one[3]>120:#时间是否已经超过5分钟,超过五分钟后喂价网站那边不再更新价格
                        index      = one[0]
                        quote_base = one[2]
                        platform   = one[1]
                        uint_time  = one[3]
                        quote = quote_base.split("/")[0]
                        base  = quote_base.split("/")[1]
                        
                        price = self._rpc_ro.get_coin_price(index, quote_base, str(uint_time))
                        if price["price"] == -100000000:#读区块链上该价格是否为非法喂价
                            get_feed_func = self._feed_records[index][platform][quote_base]
                            prices = get_feed_func(quote,base,platform,uint_time,uint_time)
                            self._logger.info("[Refeed invalid price]GetPrices(%s:%s):%s" %(platform,quote_base,str(prices)))
                            try:
                                self._rpc_feed.reset_coin_price(self._feed_account,index,quote_base,prices,True)
                                self._logger.info("[Refeed invalid price success.")
                            except Exception as err:
                                self._logger.error(err)
                        else:
                            self._logger.info("Price on blockchain is %s,so not reset it." %(str(price["price"])))
                            give_up.append(one)
                    else:
                        self._logger.info("Current reset coin price time is not valid(%s,not in[5,300])." %(uint_time - one[3]))
                        give_up.append(one)

                if give_up:
                    for one in give_up:
                        self.feeded_invalid_price.remove(one)

        uint_time=int(time.time())
        if uint_time%10==0:
            _timer = threading.Timer(self._interval, self.feed_coin)
            _timer.start()
        else:
            _timer = threading.Timer(self._interval-(uint_time%10), self.feed_coin)
            _timer.start()
        

    def feed(self, index, platform, quote_base):
        quote=quote_base.split("/")[0]
        base=quote_base.split("/")[1]
        uint_time=int(time.time())
        uint_time=int((uint_time-self._time_offset)/60)*60
        get_feed_func = self._feed_records[index][platform][quote_base]
        prices = get_feed_func(quote,base,platform,uint_time,uint_time)
        print("result get prices,before feed price:")
        print(prices)
        one_invalid_price=[]
        for one in prices:
            if one[1] == -100000000:
                one_invalid_price.append(index)
                one_invalid_price.append(platform)
                one_invalid_price.append(quote_base)
                one_invalid_price.append(one[0])
                self.feeded_invalid_price.append(one_invalid_price)
                self._logger.info("put one invalid price case in list")




        self._logger.info("[Feed]GetPrices(%s:%s_%s):%s" %(platform,quote,base,str(prices)))
        try:
            ret=self._rpc_feed.feed_coin_price(self._feed_account,index,quote_base,prices,True)
            print(ret)
            print("feed price success.")
        except Exception as err:
            err = str(err)
            npos=err.find("Feed coin price time not continuous")
            if npos != -1:
                start=err.index("{start:")+len("{start:")
                end=err.index(", end:now}")
                start_timestamp=int(err[start:end])
                end_timestamp=int((time.time()-self._time_offset)/60)*60
                if end_timestamp < start_timestamp:#[lilianwen add 2018-1-15 修复结束时间戳大于起始时间戳的bug]
                    self._logger.error("start timestamp(%d) is large than end timestamp(%d).Maybe time offset(%d) is too large" %(start_timestamp, end_timestamp, self._time_offset))
                    end_timestamp=int((time.time()-60)/60)*60
                prices = get_feed_func(quote,base,platform,start_timestamp,end_timestamp)
                print("result get prices,before refeed price:")
                print(prices)
                self._logger.info("[Refeed]GetPrices(%s:%s_%s):%s" %(platform,quote,base,str(prices)))
                self.refeed(index, platform, quote_base, prices)
            else:
                self._logger.error(err)

        


        
        
    def refeed(self,index, platform, quote_base, prices):
        try:
            ret=self._rpc_feed.feed_coin_price(self._feed_account,index,quote_base,prices,True)
            print(ret)
            print("refeed price success.")
        except Exception as err:
            self._logger.exception(err)

    #分析区块链上的喂价配置信息，返回重新组织过的信息
    def analyze_blockchain_config(self, strJson):
        result={}
        for one in strJson["module_cfg"]:
            platform=strJson["module_cfg"][one]["platform_en"]
            platform_trade_pair={}
            quote_bases=[]
            for one_trade_pair in strJson["module_cfg"][one]["quote_bases"]:
                if strJson["module_cfg"][one]["quote_bases"][one_trade_pair] == "1":
                    quote_bases.append(one_trade_pair)
            platform_trade_pair[platform]=quote_bases
            result[one]=platform_trade_pair 
        return result

    #注册喂价函数
    def register_feed_price_func(self, blockCfg, feedFuncCfg):
        result={}
        for platform in feedFuncCfg:
            result_no_index={}
            for index in blockCfg:
                if platform in blockCfg[index]:
                    quote_base_func={}
                    for quote_base in feedFuncCfg[platform]:
                        if quote_base in blockCfg[index][platform]:
                            quote_base_func[quote_base] = eval(feedFuncCfg[platform][quote_base])
                    result_no_index[platform]=quote_base_func
                    result[index] = result_no_index
        return result

    def start(self):
        self.connect(self._host, self._port, self._login_account, self._password)
        blokchain_cfg = self._rpc_ro.get_module_cfg("COIN")
        blokchain_cfg = self.analyze_blockchain_config(blokchain_cfg)
        self._feed_records  = self.register_feed_price_func(blokchain_cfg,self._feed_func_config)

        _timer = threading.Timer(self._interval, self.feed_coin)
        _timer.start()


        #遍历gold喂价
        #遍历stock喂价


        
