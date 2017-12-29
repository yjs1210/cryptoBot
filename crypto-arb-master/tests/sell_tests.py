import unittest
from xapi import XApi, Exchange, BaseQuotePair


# DO NOT ENABLE THIS TEST UNLESS YOU KNOW WHAT YOU'RE DOING
class SellTest(unittest.TestCase):
    def setUp(self):
        self.xapi = XApi()

    def _confirm(self, result):
        print(result)

    @unittest.skip("Enable this when Sell breaks")
    def testSellBinance(self):
        self.xapi.sell(Exchange.BNC, BaseQuotePair('WAVES', 'BTC'), 1, 1, True)

    @unittest.skip("Enable this when Sell breaks")
    def testSellBittrex(self):
        self.xapi.sell(Exchange.BTX, BaseQuotePair('XMR', 'BTC'), 0.05, 0.03, True).addCallbacks(self._confirm, self._confirm)

unittest.main()
