from enum import Enum

import logging

from binance.client import Client as Binance
from binance.exceptions import (BinanceAPIException, BinanceWithdrawException)
from fork.bittrex.bittrex import Bittrex, API_V2_0
from requests.exceptions import ConnectionError

_logger = logging.getLogger('xapi')


class Exchange(Enum):
    BNC = 1
    BTX = 2

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class BaseQuotePair:
    def __init__(self, base, quote):
        self.base = base
        self.quote = quote
        self.bnc_symbol = f'{base}{quote}'
        self.btx_symbol = f'{quote}-{base}'

    def __str__(self):
        return f'<{self.base}, {self.quote}>'

    def __repr__(self):
        return f'<{self.base}, {self.quote}>'

    def __eq__(self, other):
        if not isinstance(other, BaseQuotePair):
            return False
        return self.base == other.base and self.quote == other.quote

    def __hash__(self):
        return hash((self.base, self.quote))


class OrderResponse:
    def __init__(self, exchange: Exchange, symbol: BaseQuotePair, is_limit,
                 is_buy, quantity, price, success, _id=-1, filled='UNKNOWN'):
        self._exchange = exchange
        self._symbol = symbol
        self._is_limit = is_limit
        self._is_buy = is_buy
        self._quantity = quantity
        self._price = price
        self._success = success
        self._id = _id
        self._filled = filled

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        placed = 'placed' if self._success else 'FAILED'
        limit = 'Limit' if self._is_limit else 'Market'
        buy = 'buy' if self._is_buy else 'sell'
        return (f'[Id: {self._id}]: {limit} {buy} order for {self._quantity} '
                f'{self._symbol} at price {self._price} '
                f'{placed} on {self._exchange}.')


class XApiException(Exception):
    pass


class BNCException(XApiException):
    pass


class BTXException(XApiException):
    pass


EXEC_ALGO_IOC = Binance.TIME_IN_FORCE_IOC
EXEC_ALGO_GTC = Binance.TIME_IN_FORCE_GTC


class XApi:
    def __init__(self, debug=True):
        self._debug = debug
        self._cancel_limit_repeat = 100
        if debug:
            from template_conf import CONFIG_TEST as CONFIG
        else:
            from conf import CONFIG as CONFIG

        self._config = CONFIG

        self.refresh_clients()
        self.traded_universe = self.get_universe()
        self.currency_universe = {x.base for x in self.traded_universe}

    def refresh_clients(self):
        self._print('Refreshing client...')
        bnc_api_key = self._config['api']['bnc']['key']
        bnc_secret = self._config['api']['bnc']['secret']
        btx_api_key = self._config['api']['btx']['key']
        btx_secret = self._config['api']['btx']['secret']
        try:
            self._bnc_client = Binance(bnc_api_key, bnc_secret)
            self._btx_client = Bittrex(btx_api_key, btx_secret)
            self._btx_client_v2 = Bittrex(
                    btx_api_key, btx_secret, api_version=API_V2_0)
        except ConnectionError:
            raise XApiException("Couldn't connect to client - likely due to "
                                "poor internet connection")

        self._print('Clients initialized')

    def _print(self, message):
        if self._debug:
            print(message)

    def get_universe(self, quote_curr=('BTC', 'ETH')):
        # Cache/update traded universe
        self.traded_universe = {
            k for k, v in
            self.exchange_info(exchange=None, quote_currs=quote_curr).items()
            if v[Exchange.BNC]['trading'] and v[Exchange.BTX]['trading']
        }

        return self.traded_universe

    def get_fees(self, exchange: Exchange = None):
        def _get_bnc_fees(info):
            from conf import BNC_FEES
            return {k.base: BNC_FEES[k.base] * v[Exchange.BNC]['ask_price']
                    for k, v in info.items() if k.quote == 'BTC'}

        def _get_btx_fees(info):
            return {k.base: v[Exchange.BTX]['withdrawal_fee_quote']
                    for k, v in info.items() if k.quote == 'BTC'}

        exchange_info = self.exchange_info()

        if exchange is None:
            bnc_fees = _get_bnc_fees(exchange_info)
            btx_fees = _get_btx_fees(exchange_info)
            return {k: {Exchange.BNC: v, Exchange.BTX: btx_fees[k]}
                    for k, v in bnc_fees.items()}

        elif exchange == Exchange.BNC:
            return {k: {Exchange.BNC: v} for k, v in
                    _get_bnc_fees(exchange_info).items()}
        elif exchange == Exchange.BTX:
            return {k: {Exchange.BTX: v} for k, v in
                    _get_btx_fees(exchange_info).items()}

    def get_deposit_address(self, exchange: Exchange, currency):
        def _bnc_get_deposit_address(currency: str):
            response = self._bnc_client.get_deposit_address(asset=currency)
            if response['success']:
                return {
                    'currency': response['asset'],
                    'exchange': 'BNC',
                    'base_address': response['address'],
                    'alt_address': response['addressTag']
                }
            else:
                raise BNCException(f'Get deposit address failed for BNC')

        def _btx_get_deposit_address(currency: str):
            response = self._btx_client_v2.get_deposit_address(currency)
            if response['success']:
                if currency in self._config['requires_tag']:
                    alt_address = response['result']['Address']
                    base_address = response['result']['BaseAddress']
                else:
                    alt_address = response['result']['BaseAddress']
                    base_address = response['result']['Address']

                return {
                    'currency': response['result']['Currency'],
                    'exchange': 'BTX',
                    'base_address': base_address,
                    'alt_address': alt_address
                }
            else:
                raise BTXException(f'Get deposit address failed for BTX')

        return (_bnc_get_deposit_address(currency) if exchange == Exchange.BNC
                else _btx_get_deposit_address(currency))

    def transfer(self, origin: Exchange, dest: Exchange,
                 currency, amount) -> bool:
        # TODO: Persist the transaction
        if not ((isinstance(origin, Exchange)) and
                    (isinstance(dest, Exchange)) and
                    (currency in self.currency_universe) and
                    (origin != dest)):
            raise ValueError(f'Invalid exchange or symbol: '
                             f'origin: {origin}, '
                             f'dest: {dest}, '
                             f'symbol: {currency})')

        address_info = self.get_deposit_address(dest, currency)
        dest_deposit_addr = address_info['base_address']
        dest_deposit_tag = address_info['alt_address']

        if origin == Exchange.BNC and dest == Exchange.BTX:
            try:
                response = self._bnc_client.withdraw(
                        asset=currency,
                        address=dest_deposit_addr,
                        addressTag=dest_deposit_tag,
                        amount=amount,
                        name='Sending to Bittrex',
                        description=f'Withdrawing {amount} {currency}')
                if response['success']:
                    print(f'Successfully transferred {amount} {currency} '
                          f'from Binance to Bittrex.')
                    return True
            except BinanceAPIException as e:
                print(e)
            except BinanceWithdrawException as e:
                print(e)
        elif origin == Exchange.BTX and dest == Exchange.BNC:
            try:
                response = self._btx_client.withdraw(
                        currency,
                        amount,
                        dest_deposit_addr,
                        dest_deposit_tag)
                if response['success']:
                    print(f'Successfully transferred {amount} {currency} '
                          f'from Bittrex to Binance.')
                    return True
            except Exception:
                raise BTXException('Could not withdraw from Bittrex...')
        return False

    def exchange_info(self, exchange: Exchange = None,
                      quote_currs=('BTC', 'ETH')) -> dict:
        """
        Retrieves exchange data. If exchange is None, we'll retrieve
        info from both exchanges.

        Returns a dictionary with the following structure:

        {Exchange: {
            quote_coin: str (BTC/ETH for now): {
                base_coin: str {
                    trading: boolean
                    bid_price: float
                    ask_price: float
                    withdrawal_fee: float
                    volume: float
                }
            }
        }

        :param exchange:
        :param quote_currs:
        :return:
        """

        def _get_bnc_info():
            # Assumes unique key in list of dicts
            def _seek_key(l: list, key):
                for d in l:
                    if key in d:
                        return d[key]

            bnc_order_book_raw = self._bnc_client.get_orderbook_tickers()
            bnc_market_raw = self._bnc_client.get_products()['data']
            bnc_info_raw = self._bnc_client.get_exchange_info()['symbols']

            agg_info = {}
            for quote_curr in quote_currs:
                bnc_order_book = {
                    d['symbol'].replace(quote_curr, ''): {
                        'bid_price': float(d['bidPrice']),
                        'bid_qty': float(d['bidQty']),
                        'ask_price': float(d['askPrice']),
                        'ask_qty': float(d['askQty'])
                    } for d in bnc_order_book_raw
                    if d['symbol'].endswith(quote_curr)
                }
                bnc_market = {
                    d['baseAsset']: {
                        'trading': True if d['status'] == 'TRADING' else False,
                        'traded_notional_usd': d['tradedMoney'],
                        'withdrawal_fee': float(d['withdrawFee']),
                        'min_trade': eval(d['minQty'].lower()),
                        'volume': float(d['volume'])
                    } for d in bnc_market_raw if d['quoteAsset'] == quote_curr
                }
                bnc_info = {
                    d['baseAsset']: {
                        # For lot size
                        'min_qty': float(
                                _seek_key(d['filters'], 'minQty')),
                        'step_size': float(_seek_key(d['filters'], 'stepSize')),
                        # For price
                        'min_price': float(_seek_key(d['filters'], 'minPrice')),
                        'tick_size': float(_seek_key(d['filters'], 'tickSize')),
                        # Minimum price * quantity
                        'min_notional': float(
                                _seek_key(d['filters'], 'minNotional'))
                    } for d in bnc_info_raw
                    if d['quoteAsset'] == quote_curr
                }

                agg_info.update({
                    BaseQuotePair(k, quote_curr): {
                        Exchange.BNC: {**v, **bnc_order_book[k], **bnc_info[k]}
                    } for k, v in bnc_market.items()
                    if v['trading'] and k in bnc_order_book and k in bnc_info
                })

            return agg_info

        def _get_btx_info():
            btx_market_raw = self._btx_client.get_market_summaries()['result']
            btx_market_currencies = self._btx_client.get_currencies()['result']
            btx_market_info_raw = self._btx_client.get_markets()['result']

            agg_info = {}
            for quote_curr in quote_currs:
                btx_market = {
                    # Key is currency name
                    d['MarketName'].split('-')[1]: {
                        'bid_price': d['Bid'],
                        'ask_price': d['Ask'],
                        'volume': d['Volume']
                    } for d in btx_market_raw if
                    d['MarketName'].startswith(quote_curr)
                }
                btx_currs = {
                    # Key is currency name
                    d['Currency']: {
                        'withdrawal_fee': d['TxFee']
                    } for d in btx_market_currencies
                }
                btx_mkt_info = {
                    d['MarketCurrency']: {
                        'min_qty': d['MinTradeSize'],
                        'trading': d['IsActive']
                    } for d in btx_market_info_raw
                    if d['BaseCurrency'] == quote_curr
                }

                agg_info.update({
                    BaseQuotePair(k, quote_curr): {
                        Exchange.BTX: {
                            **v, **btx_currs[k], **btx_mkt_info[k],
                            'withdrawal_fee_quote':
                                btx_currs[k]['withdrawal_fee'] * v['ask_price'],
                        }
                    } for k, v in btx_market.items()
                    if k in btx_mkt_info and btx_mkt_info[k]['trading']
                })

            return agg_info

        if not (exchange is None or isinstance(exchange, Exchange)):
            raise ValueError(f'Exchange {exchange} is not type '
                             f'Exchange or None')

        if exchange is None:
            from conf import BNC_RESTRICTED
            restricted = BNC_RESTRICTED
            bnc_info = _get_bnc_info()
            btx_info = _get_btx_info()
            universe = bnc_info.keys() & btx_info.keys()
            return {symbol: {**bnc_info[symbol], **btx_info[symbol]}
                    for symbol in universe if symbol.base not in restricted}

        elif exchange == Exchange.BNC:
            return _get_bnc_info()
        elif exchange == Exchange.BTX:
            return _get_btx_info()
        else:
            raise ValueError(f'Unknown exchange: {exchange}')

    def order_book(self, symbol: BaseQuotePair):
        def _bnc_book(symbol):
            book = self._bnc_client.get_orderbook_ticker(
                    symbol=symbol.bnc_symbol)
            return {
                'bid_price': float(book['bidPrice']),
                'bid_qty': float(book['bidQty']),
                'ask_price': float(book['askPrice']),
                'ask_qty': float(book['askQty'])
            }

        def _btx_book(symbol):
            # TODO: Write an wrapper over network calls to encapsulate retry
            response = self._btx_client.get_orderbook(symbol.btx_symbol)
            if not response['success']:
                raise BTXException(f"Couldn't retrieve order book for {symbol}")

            book = response['result']
            # TODO: Consider getting deeper layers of this book
            return {
                'bid_price': book['buy'][0]['Rate'],
                'bid_qty': book['buy'][0]['Quantity'],
                'ask_price': book['sell'][0]['Rate'],
                'ask_qty': book['sell'][0]['Quantity']
            }

        return {Exchange.BNC: _bnc_book(symbol),
                Exchange.BTX: _btx_book(symbol)}

    # See README for method signature
    def buy(self,
            exchange: Exchange,
            symbol: BaseQuotePair,
            amount: float,
            price: float,
            is_limit,
            exec_algo=EXEC_ALGO_GTC):
        def _buy_bittrex(symbol, amount: float, price: str,
                         is_limit: bool):
            """
            Buys a Coin off Bittrex.

             :returns: The API response from Bittrex.
                We will wait some preset amount of time before canceling the
                execution
                (failing the Deferred). If the order is awaiting execution, and
                eventually succeeds, the deferred will contain results of the
                execution

            """
            # TODO(yuxiao): reimplement this when bittrex supports this.
            if not is_limit:
                raise XApiException(
                        'Market orders on Bittrex are not yet supported')

            response = self._btx_client.buy_limit(
                    symbol.btx_symbol, amount, price)
            if not response['success']:
                raise BTXException(f'Buy failed - received '
                                   f'{response["message"]} from Bittrex')

            return OrderResponse(
                    Exchange.BTX, symbol, is_limit, True, amount, price,
                    response['success'], response['result']['uuid'])

        def _buy_binance(symbol: BaseQuotePair, amount: float,
                         price: str, is_limit: bool, exec_algo):
            """
            Buys a Coin off Binance using a limit order.

            :returns: Deferred representing the API response.
                If the order is executed immediately, the Deferred will be
                successful upon return.
                If the order is awaiting execution, we will wait some preset
                amount of time before canceling the execution (failing the
                Deferred).
                If the order is awaiting execution, and eventually succeeds, the
                deferred will contain results of the execution
            """
            if not is_limit:
                response = self._bnc_client.order_market_buy(
                        symbol=symbol.bnc_symbol,
                        side=Binance.SIDE_BUY,
                        quantity=amount,
                        newOrderRespType=Binance.ORDER_RESP_TYPE_FULL)
            else:
                response = self._bnc_client.order_limit(
                        symbol=symbol.bnc_symbol,
                        side=Binance.SIDE_BUY,
                        quantity=amount,
                        price=price,
                        timeInForce=exec_algo,
                        newOrderRespType=Binance.ORDER_RESP_TYPE_FULL)
            return OrderResponse(
                    Exchange.BNC, symbol, is_limit, True, amount,
                    price, True, response['orderId'], response['status'])

        if exchange == Exchange.BNC:
            return _buy_binance(
                    symbol, amount, f'{price:.8f}', is_limit, exec_algo)
        else:
            return _buy_bittrex(symbol, amount, f'{price:.8f}', is_limit)

    # See README for method signature
    def sell(self,
             exchange: Exchange,
             symbol: BaseQuotePair,
             amount: float,
             price: float,
             is_limit,
             exec_algo=EXEC_ALGO_GTC):

        def _sell_binance(symbol, amount, price, is_limit, exec_algo):
            if not is_limit:
                response = self._bnc_client.order_market_sell(
                        symbol=symbol.bnc_symbol,
                        quantity=amount,
                        newOrderRespType=Binance.ORDER_RESP_TYPE_FULL)
            else:
                response = self._bnc_client.order_limit_sell(
                        symbol=symbol.bnc_symbol,
                        quantity=amount,
                        price=price,
                        timeInForce=exec_algo,
                        newOrderRespType=Binance.ORDER_RESP_TYPE_FULL)
            return OrderResponse(
                    Exchange.BNC, symbol, is_limit, False, amount,
                    price, True, response['orderId'], response['status'])

        def _sell_bittrex(symbol, amount, price, is_limit):
            if not is_limit:
                raise XApiException(
                        'Market orders on Bittrex are not yet supported')
            response = self._btx_client.sell_limit(
                    symbol.btx_symbol, amount, price)
            if not response['success']:
                raise BTXException(f'Failed to place limit sell on Bittrex. '
                                   f'Response: {response}.')

            return OrderResponse(
                    Exchange.BTX, symbol, is_limit, False, amount, price,
                    response['success'], response['result']['uuid'])

        if exchange == Exchange.BNC:
            return _sell_binance(
                    symbol, amount, f'{price:.8f}', is_limit, exec_algo)
        else:
            return _sell_bittrex(symbol, amount, f'{price:.8f}', is_limit)

    def get_holdings(self, exchange: Exchange = None):
        """
        Retrieves the account balance for an exchange.

        :returns: dict keyed by currency name - contains holdings for exchange
        format:
        {
            'Currency': {
                'Available': ...,
                'Pending' : ...
            }, ...
        }
        """

        def _get_bnc_holdings():
            response = self._bnc_client.get_account()
            if 'balances' not in response.keys():
                raise BNCException('Cannot retireve data from Binance')
            if not response['canWithdraw']:
                raise BNCException('Cannot withdraw from '
                                   'Binance for some reason')
            result = {
                element['asset']: {
                    'available': float(element['free']),
                    'pending': float(element['locked'])
                } for element in response['balances']
                if float(element['free']) > 0 or float(element['locked']) > 0
            }
            return result

        def _get_btx_holdings():
            response = self._btx_client.get_balances()
            if not response['success']:
                raise BTXException('Cannot retrieve data from Bittrex')

            result = {
                element['Currency']: {
                    'available': element['Available'],
                    'pending': element['Pending']
                } for element in response['result']
                if element['Available'] > 0 or element['Pending'] > 0
            }
            return result

        if exchange is None:
            return {Exchange.BNC: _get_bnc_holdings(),
                    Exchange.BTX: _get_btx_holdings()}
        elif exchange == Exchange.BNC:
            return _get_bnc_holdings()
        elif exchange == Exchange.BTX:
            return _get_btx_holdings()


if __name__ == '__main__':
    print(XApi().get_universe())
