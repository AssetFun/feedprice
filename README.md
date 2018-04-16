# feedprice
feed price for assetfun system. The program is written by python3.

## install python3 and pip3
```
sudo apt-get install python3
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
```

## install libraries
>sudo apt-get install libffi-dev libssl-dev python3-dev -y

## install python3 modules
```
sudo pip3 install graphenelib
sudo pip3 install demjson
```


## config.json
```json
{ 
"host":"127.0.0.1", 
"port":11014,
"password":"password_to_unlock_cli_wallet",
"login_account":"nathan",
"witnesses":[],
"witness_config_file":"/data/assetfun/node1/witness_node_data_dir/config.ini",
"interval":10,
"time_offset":60,
"log_file":"./log/feed_price.log",
"feed_price":{
       "Bitfinex":{
            "BTC/USD":"price_assetfun_get_price.GetPrice",
            "ETH/USD":"price_assetfun_get_price.GetPrice",
            "BCH/USD":"price_assetfun_get_price.GetPrice",
            "LTC/USD":"price_assetfun_get_price.GetPrice"
        },
        "Poloniex":{
            "BCH/BTC":"price_assetfun_get_price.GetPrice",
            "ETH/BTC":"price_assetfun_get_price.GetPrice",
            "LTC/BTC":"price_assetfun_get_price.GetPrice"
        } 
    }   
}
```

### host
set the ip address of the server which feedprice is going to connect to.Usually it is 127.0.0.1.

### port
set the port of the server which feedprice is going to connect to,for example 11014.You can check your cli_wallet command to get this value,for example if the cli_wallet command is 
nohup /data/assetfun/console/bin/cli_wallet --wallet-file=/data/feedprice/wallet.json --chain-id=1f17d122a5f217003d9210be64840aa2dcdc67c1bfeda363f1565b637900dec1 --server-rpc-endpoint=ws://127.0.0.1:11011 --rpc-endpoint=0.0.0.0:11014 -d 2>&1  log/wallet.log &
then the port is 11014.

### password
the cli_wallet unlock password.

### login_account
account name used to login cli_wallet.you'd better set your witness account name.

### witnesses
the list of witness which runs on this witness node.

### witness_config_file
another way to get the list of witness.Put the path of your witness configuration file here.
If the value of "witnesses" is empty then the program will read "witness_config_file" to get the witnesses.

### interval
the interval time of feedprice runs, which is 10 seconds.So we set it 10.

### time_offset
we can not feed the price of now,so we feed the history price.when i say history price, I mean the time before now, for example 60 seconds ago.If we feed the price of 60 seconds ago, we set this value 60.

### log_file
set the path of log file.

### feed_price
set the functions to get the feed price.for example
```javascript
"Bitfinex":{
            "BTC/USD":"price_assetfun_get_price.GetPrice",
            "ETH/USD":"price_assetfun_get_price.GetPrice",
            "BCH/USD":"price_assetfun_get_price.GetPrice",
            "LTC/USD":"price_assetfun_get_price.GetPrice"
},
```
it means if we want to get the price of "BTC/USD" on Bitfinex, we use the function GetPrice of price_assetfun_get_price module.

# Start feedprice
run script
> ./start_feeder.sh