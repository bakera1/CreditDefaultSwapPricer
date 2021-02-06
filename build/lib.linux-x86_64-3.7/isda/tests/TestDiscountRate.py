
import unittest
import datetime

from isda.isda import cds_discount_rate_ir_tenor_dates


class MyTestCase(unittest.TestCase):
    """
        Testcase that has been reconciled with output from MarkIT partners online calculator and
        separate ISDA source; these figures are accurate to 11 decimal places and battle tested
        enough to be useful for more than just indicative risk.

        i) test coverage needs to be extended to handle cases over weekends & holidays
        ii) for now the coverage is a simple buy/sell protection flat spread trade

    """

    def setUp(self):
        # available from markit swap feed
        self.swap_rates = [-0.00369, -0.00340, -0.00329, -0.00271, -0.00219, -0.00187, -0.00149, 0.000040, 0.00159,
                           0.00303, 0.00435, 0.00559, 0.00675, 0.00785, 0.00887]
        self.swap_tenors = ['1M', '2M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y', '10Y']
        self.verbose = 0

    def tearDown(self):
        pass

    def test_buy_protection(self):
        """ method to test buy protection single name CDS """

        self.date_list = list()
        for month in range(1, 12):
            self.date_list.append(datetime.datetime(2018, month, 8).strftime('%d/%m/%Y'))

        f = cds_discount_rate_ir_tenor_dates(self.date_list,
                                             self.swap_rates,
                                             self.swap_tenors,
                                             self.verbose
                                             )

        # expand tuple
        discount_rate = f[0]
        self.assertAlmostEqual(0.9999794971627696, discount_rate, 6)

if __name__ == '__main__':
    unittest.main()
