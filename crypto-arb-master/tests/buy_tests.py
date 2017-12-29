import unittest
from xapi import XApi, BaseQuotePair, Exchange


# DO NOT ENABLE THIS TEST NORMALLY
class BuyTest(unittest.TestCase):
    def setUp(self):
        self.xapi = XApi()

    def _confirm(self, result):
        print(result)

    @unittest.skip("Enable this when Buy breaks")
    def testBuyBittrex(self):
        self.xapi.buy(Exchange.BTX, BaseQuotePair('XMR', 'BTC'), 0.05, 0.0247,
                      False).addCallbacks(self._confirm, self._confirm)

    @unittest.skip("Enable this when Buy breaks")
    def testBuyBinance(self):
        self.xapi.buy(Exchange.BNC, BaseQuotePair('ETH', 'BTC'), 0.001, 0.00047,
                      False).addErrback(lambda error: self.fail(error))


if __name__ == '__main__':
    unittest.main()
