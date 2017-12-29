import unittest
from xapi import XApi, Exchange


class TransferTest(unittest.TestCase):
    def setUp(self):
        self.xapi = XApi(debug=True)

    def tearDown(self):
        pass

    def test_address_retrieval(self):
        BNC_BTC_BASE_ADDRESS = '1J42EbVnN3UsKjL5EX2GR3HKF2fQxKn5CP'
        BTX_BTC_BASE_ADDRESS = '1LRKuCUzQ2mN2BiHxYzxKQhjiLx4o5pszY'
        BNC_XLM_BASE_ADDRESS = 'GAHK7EEG2WWHVKDNT4CEQFZGKF2LGDSW2IVM4S5DP42RBW3K6BTODB4A'
        BNC_XLM_ALT_ADDRESS = '1048079343'
        BTX_XLM_BASE_ADDRESS = 'GB6YPGW5JFMMP2QB2USQ33EUWTXVL4ZT5ITUNCY3YKVWOJPP57CANOF3'
        BTX_XLM_ALT_ADDRESS = 'f10286d56c3a4bd8843'

        bnc_btc_result = self.xapi.get_deposit_address(Exchange.BNC, 'BTC')
        btx_btc_result = self.xapi.get_deposit_address(Exchange.BTX, 'BTC')
        bnc_xlm_result = self.xapi.get_deposit_address(Exchange.BNC, 'XLM')
        btx_xlm_result = self.xapi.get_deposit_address(Exchange.BTX, 'XLM')

        # Correct currency
        self.assertTrue(bnc_btc_result['currency'] == 'BTC')
        self.assertTrue(btx_btc_result['currency'] == 'BTC')
        self.assertTrue(bnc_xlm_result['currency'] == 'XLM')
        self.assertTrue(btx_xlm_result['currency'] == 'XLM')

        # Base address for currencies
        self.assertTrue(bnc_btc_result['base_address'] == BNC_BTC_BASE_ADDRESS)
        self.assertTrue(btx_btc_result['base_address'] == BTX_BTC_BASE_ADDRESS)
        self.assertTrue(bnc_xlm_result['base_address'] == BNC_XLM_BASE_ADDRESS)
        self.assertTrue(btx_xlm_result['base_address'] == BTX_XLM_BASE_ADDRESS)

        # Alt address for curries that require it
        self.assertTrue(bnc_xlm_result['alt_address'] == BNC_XLM_ALT_ADDRESS)
        self.assertTrue(btx_xlm_result['alt_address'] == BTX_XLM_ALT_ADDRESS)

    @unittest.skip("Enable this when transfer breaks")
    def test_transfer(self):
        # Eventually integrate with get_holding to confirm withdrawal
        print('Before: ')
        print(self.xapi.get_holdings(Exchange.BTX))
        print(self.xapi.get_holdings(Exchange.BNC))

        self.assertTrue(self.xapi.transfer(
                Exchange.BTX, Exchange.BNC, 'XLM', 21))
        self.assertTrue(self.xapi.transfer(
                Exchange.BNC, Exchange.BTX, 'XLM', 21))

        print('AFTER: ')
        print(self.xapi.get_holdings(Exchange.BTX))
        print(self.xapi.get_holdings(Exchange.BNC))


if __name__ == '__main__':
    unittest.main()
