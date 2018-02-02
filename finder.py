# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 05:42:48 2017

@author: james.lee
"""

"""
collect data and create a log of arb opportunities
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

def save_object(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)
# sample usage

xapi_client = XApi()
prices = xapi_client.exchange_info()

try:
    with open('arb_log.pkl', 'rb') as input:
        df= pickle.load(input)
except FileNotFoundError:
     df = pd.DataFrame(columns=['security', 'base_security', 'quote_security','buy_exchange', 'sell_exchange','price_buy_exchange','price_sell_exchange','spread','time','descr'])


while True:
    prices = xapi_client.exchange_info()
    for security in prices:
        bncbid = prices[security][Exchange.BNC]['bid_price']
        bncask = prices[security][Exchange.BNC]['ask_price']
        bitbid = prices[security][Exchange.BTX]['bid_price']
        bitask = prices[security][Exchange.BTX]['ask_price']
        buyBncArb = (bitbid- bncask)/bncask    
        buyBitArb = (bncbid - bitask)/bitask
        if(buyBncArb > .015):
            insert = [security, security.base, security.quote, Exchange.BNC.name, Exchange.BTX.name, bncask, bitbid, round(buyBncArb,4), datetime.datetime.now(), 'buy ' + security.base + ' at BNC'+' and sell it at BIT' ]
            df.loc[len(df)+1] = insert
        if(buyBitArb > .015):
            insert = [security, security.base, security.quote, Exchange.BTX.name, Exchange.BNC.name, bitask, bncbid, round(buyBitArb,4), datetime.datetime.now(), 'buy ' + security.base + ' at BIT'+' and sell it at BIN' ]
            df.loc[len(df)+1] = insert
    if(len(df))>10000:
        df = df.tail(10000)    
    save_object(df, 'arb_log.pkl')
    time.sleep(5)


#datetime.datetime.now().strftime('%Y/%m/%d /%H:%M:%S')
