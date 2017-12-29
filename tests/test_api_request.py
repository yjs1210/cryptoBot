#!/usr/bin/env python
# coding=utf-8

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import pytest
import requests_mock
import json

with open('secrets.json') as json_data_file:
    data = json.load(json_data_file)
print(data)

data['shhh']['read_key']



client = Client(data['shhh']['read_key'], data['shhh']['read_secret'])


def test_invalid_json():
    """Test Invalid response Exception"""
    with pytest.raises(BinanceRequestException):
        with requests_mock.mock() as m:
            m.get('https://www.binance.com/exchange/public/product', text='<head></html>')
            client.get_products()


def test_api_exception():
    """Test API response Exception"""

    with pytest.raises(BinanceAPIException):
        with requests_mock.mock() as m:
            json_obj = {"code": 1002, "msg": "Invalid API call"}
            m.get('https://api.binance.com/api/v1/time', json=json_obj, status_code=400)
            client.get_server_time()


def test_withdraw_api_exception():
    """Test Withdraw API response Exception"""

    with pytest.raises(BinanceWithdrawException):

        with requests_mock.mock() as m:
            json_obj = {"success": False, "msg": "Insufficient funds"}
            m.register_uri('POST', requests_mock.ANY, json=json_obj, status_code=200)
            client.withdraw(asset='BTC', address='BTCADDRESS', amount=100)
