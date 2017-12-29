# Crypto-Arb Bot

A crypto-currency arbitrage based bot. By Ed and Yux

## X-Api

Proprietary API for interacting with Multiple e*X*change *API*s.

```python
def get_holding(self, exchange):
```

_Parameters_
* **exchange** : which exchange to transact in. Represented by Exchange enum in XApi

_Return_:
A list of dictionaries that represents your holding in the exchange:

[{"Currency" : string,
  "Available": float,
  "Pending": float}, ...]

```python
def buy(self, exchange, symbol, amount, price, is_limit):
```

_Parameters_
* **exchange** : which exchange to transact in. Represented by Exchange enum in XApi
* **symbol** : which coin to transact with. Represented by Coin enum in XApi
* **amount** : amount of coins to buy
* **price**: price of coin to purchase at
* **is\_limit** : whether to set a limit order

_note_: It is unclear what happens with the exchanges, when you place a market order with a price range that exceeds/is below market value.

_Return_:
A Deferred. This Deferred varies based on which exchange you're buying on
* Deferred return value when buying on Binance:
  * success: {
      "orderId" : string
      "clientOrderId" : string
      "status": string
      }
  * failure: an Exception with the message \'Did not execute\'
* Deferred return value when buying on Bittrex:
  * success: {
      "uuid" : string
    }
  * failure: an Exception with the message \'Did not execute\'


```python
def sell(self, exchange, symbol, amount, price, is_limit):
```

_Parameters_
* **exchange** : which exchange to transact in. Represented by Exchange enum in XApi
* **symbol** : which coin to transact with. Represented by Coin enum in XApi
* **amount** : amount of coins to buy
* **price**: price of coin to purchase at
* **is\_limit** : whether to set a limit order

_Return_:
A Deferred. This Deferred varies based on which exchange you're buying on.
* Deferred return value when buying on Binance:
  * success: {
      "orderId" : string,
      "clientOrderId" : string,
      "status" : string
     }
* Deferred return value when buying on Bittrex:
  * success: {
      "uuid" : string
  }

## Future Stuff


## Caveats
* Binance: no withdrawals are permitted for 24 hours after disable of SMS Auth or Google Auth.
* Binance: Need to have sent each crypto to dest address via website before API 

