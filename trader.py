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
        
# sample usage
with open('arb_log.pkl', 'rb') as input:
    df= pickle.load(input)

##get highest spread 
latest_time = df.loc[df['time'].idxmax()]['time']
latest_df = df[((latest_time- df.time) < datetime.timedelta(seconds=5)) & (~df.base_security.isin(arb_bans)) ]
priority_df = latest_df[(latest_df.security.isin(arb_priority))]
latest_df

xapi_client = XApi()
##get balances
balances = xapi_client.get_holdings()

##if priority coin exists, then execute right away
if (len(priority_df)) > 0 :
    priority_execute = priority_df.loc[priority_df['spread'].idxmax()]    

if 'BTC' not in balances[Exchange.BNC]:
    raise ValueError("No BTC available in Binance")

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





