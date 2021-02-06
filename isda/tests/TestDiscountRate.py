
import unittest
import datetime
from dateutil.relativedelta import *

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

        self.result = [0.9999589957968681,
        0.9980746188690016,
        0.9962244301618564,
        0.9943470908518799,
        0.9924936377158069,
        0.9906233289133188,
        0.9887869530937763,
        0.9869236293686865,
        0.9850941118963936,
        0.9832377471614023,
        0.981415062422361]

    def tearDown(self):
        pass

    def test_discount_factor(self):
        """ method to test buy protection single name CDS """

        # base date
        value_date = datetime.datetime(2021, 2, 5)
        date_list = list()
        date_list.append(value_date.strftime('%d/%m/%Y'))
        for month in range(10):
            value_date = value_date + relativedelta(months=6)
            date_list.append(value_date.strftime('%d/%m/%Y'))

        f = cds_discount_rate_ir_tenor_dates(value_date.strftime('%d/%m/%Y'),
                                             date_list,
                                             self.swap_rates,
                                             self.swap_tenors,
                                             self.verbose
                                             )
        # expand tuple
        index = 0
        for mydate, discount_rate in zip(date_list, f):
            if self.verbose:
                print(index, mydate, discount_rate)
            self.assertAlmostEqual(self.result[index], discount_rate, 6)
            index += 1

if __name__ == '__main__':
    unittest.main()
