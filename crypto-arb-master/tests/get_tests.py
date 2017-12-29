import unittest
from xapi import XApi, Exchange


class GetTest(unittest.TestCase):
    def setUp(self):
        self.xapi = XApi(debug=True)

    def tearDown(self):
        pass

    def test_holding(self):
        # Consider changing tests to something more general
        self.assertTrue(len(XApi().get_holdings(Exchange.BTX)) > 0)
        self.assertTrue(len(XApi().get_holdings(Exchange.BNC)) > 0)


if __name__ == '__main__':
    unittest.main()
