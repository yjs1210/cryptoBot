# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 04:46:06 2017

@author: james.lee
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import pytest
import requests_mock
import json

with open('secrets.json') as json_data_file:
    data = json.load(json_data_file)
print(data)

client = Client(data['shhh']['read_key'], data['shhh']['read_secret'])

# get market depth
depth = client.get_order_book(symbol='BTCUSDT')

print(depth)


# place market buy order
order = client.create_order(
    symbol='BNBBTC',
    side=Client.SIDE_BUY,
    type=Client.ORDER_TYPE_MARKET,
    quantity=100)

# get all symbol prices
prices = client.get_all_tickers()

# withdraw 100 ETH
# check docs for assumptions around withdrawals
from binance.exceptions import BinanceApiException, BinanceWithdrawException
try:
    result = client.withdraw(
        asset='ETH',
        address='<eth_address>',
        amount=100)
except BinanceApiException as e:
    print(e)
except BinanceWithdrawException as e:
    print(e)
else:
    print("Success")

# fetch list of withdrawals
withdraws = client.get_withdraw_history()

# fetch list of ETH withdrawals
eth_withdraws = client.get_withdraw_history(asset='ETH')

# get a deposit address got BTC
address = client.get_deposit_address(asset='BTC')

# start trade websocket
def process_message(msg):
    print("message type: {}".format(msg['e']))
    print(msg)
    # do something

from binance.websockets import BinanceSocketManager
bm = BinanceSocketManager(client)
bm.start_aggtrade_socket(symbol='BNBBTC')
bm.start()