# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 05:42:48 2017

@author: james.lee
"""

"""
collect data and create a log of arb opportunities
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
from bittrex.bittrex import Bittrex
import pytest
import requests_mock
import json
import time



with open('secrets.json') as json_data_file:
    scrt = json.load(json_data_file)
print(scrt)


bin_client = Client(scrt['shhh']['bin_read_key'], scrt['shhh']['bin_read_secret'])
binList = bin_client.get_exchange_info()
binList['symbols']


bit_client = Bittrex(scrt['shhh']['bit_read_key'],scrt['shhh']['bit_read_secret'],)
bitList = bit_client.get_markets()
bitList






while True:
    print 'Hello'
    time.sleep(2) # 2 second delay