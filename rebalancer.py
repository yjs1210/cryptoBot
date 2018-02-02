# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 04:46:06 2017

@author: james.lee
"""
from xapi import XApi
from xapi import Exchange
from xapi import BaseQuotePair
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
from bittrex.bittrex import Bittrex
import pytest
import json
import time
import datetime
import pickle
import pandas as pd
import numpy as np
import template_conf
from trader_conf import ARB_BANS as arb_bans
from trader_conf import ARB_PRIORITY as arb_priority

def save_object(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)
        
xapi_client = XApi()


##get balances
balances = xapi_client.get_holdings()

with open('arb_log.pkl', 'rb') as input:
    df= pickle.load(input)

##get highest spread 
latest_time = df.loc[df['time'].idxmax()]['time']
latest_df = df[((latest_time- df.time) < datetime.timedelta(seconds=5))]
latest_df

#stop if no arbs exists, 
if len(latest_df) ==0:
    time.sleep(5)
    break


execute = latest_df.loc[latest_df['spread'].idxmax()]

##assign buy exchange
if(execute['buy_exchange'] =='BTX'):
    buy_exchange = Exchange.BTX
else: 
    buy_exchange = Exchange.BNC

##assign sell exchange
if(execute['sell_exchange'] =='BTX'):
    sell_exchange = Exchange.BTX
else: 
    sell_exchange = Exchange.BNC

security = execute['base_security']

buy_price = execute['price_buy_exchange']

try:
   execute_balance = balances[sell_exchange][security]['available']
##stop go on to the next security if we don't have any to sell
except KeyError:
    break


##less than .05 BTC trade, not worthwhile
if(execute_balance*buy_price<.05):
    break

##we have things to sell, now make sure there are enough BTC's on the other side
if('BTC' in balances[buy_exchange]):
     if (balances[buy_exchange]['BTC']['available'] >= .05):
         buy_with_btc = max(balances[buy_exchange]['BTC']['available'], execute_balance*buy_price )


if((sell_exchange=='BTX') &  :
    
balances[Exchange.BNC]['MON']['available']

if(buy_exchange=='BNC'):
if ('BTC' in balances[Exchange.BNC]):
    if (balances[Exchange.BNC]['BTC']['available'] > .1)
    
if 'BTC' not in balances[Exchange.BTX]:
    raise ValueError("No BTC avilable in Bittrex")

bnc_reserves = balances[Exchange.BNC]['BTC']['available']
bit_reserves = balances[Exchange.BTX]['BTC']['available']




##if any of the priority arbs exist, then execute
for key in balances[Exchange.BNC]:
    print(key)
    
        






##xlm 

###if on priority list execute first
###next, if not on a ban list, then see if it is increasing momentum and spread increasing, execute

time1 = datetime.datetime.now()
time2 = datetime.datetime.now() # waited a few minutes before pressing enter
elapsedTime = time2 - time1
elapsedTime

df.loc[df['time'].idxmax()]
df.loc[df['spread'].idxmax()]





