import os
import unittest
import uuid

from isda.isda import compute_isda_upfront, average


class MyTestCase(unittest.TestCase):
    """
        Testcase that has been reconciled with output from MarkIT partners online calculator and
        separate ISDA source; these figures are accurate to 11 decimal places and battle tested
        enough to be useful for more than just indicative risk.

        i) test coverage needs to be extended to handle cases over weekends & holidays
        ii) for now the coverage is a simple buy/sell protection flat spread trade
    """

    __name__ = "MyTestCase"

    def setUp(self):
        # available from markit swap feed

        self.is_rofr = 1
        self.swap_rates = [0.002979,
                           0.006419,
                           0.010791,
                           0.015937,
                           0.018675,
                           0.018777,
                           0.018998,
                           0.019199,
                           0.019409,
                           0.019639,
                           0.019958,
                           0.020279,
                           0.020649,
                           0.021399,
                           0.021989,
                           0.02138,
                           0.019411
                           ]
        self.swap_tenors = ['1M', '3M', '6M', '1Y', '2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y', '10Y', '12Y',
                            '15Y', '20Y', '30Y']

        # economics of trade 1% fixed coupon
        self.coupon = 100.0
        self.trade_date = '31/08/2022'
        self.accrual_start_date = '20/06/2022'
        self.maturity_date = '20/12/2026'
        self.notional = 12.0
        self.is_buy_protection = 0  # only ever buy or sell protection!
        self.verbose = 0

    def tearDown(self):
        pass

    def test_compute_isda_upfront(self):
        """
        credit_spread 65.00 recovery_rate 0.40 accrued -24,333.33 clean_settlement_amount -171,870.17 dirty_settlement_amount: -171,870.17
        average execution (1.0,)

        Ran 1 test in 0.010s

        OK

        Process finished with exit code 0

        """

        # simulate an index with 125 names;;
        self.credit_spread_list = [65 / 10000]
        self.recovery_rate_list = [0.4]

        """ EUR ACT/360, 30/360, 1Y, 1Y """
        self.swapFixedDayCountConvention = 'ACT/360'
        self.swapFloatingDayCountConvention = 'ACT/360'
        self.swapFixedPaymentFrequency = '1Y'
        self.swapFloatingPaymentFrequency = '1Y'

        unique_filename = str(uuid.uuid4())
        self.holiday_filename = f'{unique_filename}.dat'
        self.holiday_list = [16010101, 20180320]

        def save_to_file(*holiday_list):
            with open(self.holiday_filename, mode='wt', encoding='utf-8') as myfile:
                for lines in holiday_list:
                    myfile.write('\n'.join(str(line) for line in lines))
                    myfile.write('\n')

        # just for measuring performance

        save_to_file(self.holiday_list)

        wall_time_list = list()
        for credit_spread, recovery_rate in zip(self.credit_spread_list, self.recovery_rate_list):
            f = compute_isda_upfront(self.trade_date,
                                     self.maturity_date,
                                     self.accrual_start_date,
                                     recovery_rate,
                                     self.coupon,
                                     self.notional,
                                     self.is_buy_protection,
                                     self.swap_rates,
                                     self.swap_tenors,
                                     credit_spread,
                                     self.is_rofr,
                                     self.holiday_filename,
                                     self.swapFloatingDayCountConvention,
                                     self.swapFixedDayCountConvention,
                                     self.swapFixedPaymentFrequency,
                                     self.swapFloatingPaymentFrequency,
                                     self.verbose)

            upfront_charge_dirty, upfront_charge_clean, accrued_interest, status, duration_in_milliseconds = f

            wall_time_list.append(float(duration_in_milliseconds))
            print(f"credit_spread {credit_spread * 10000.:,.2f} "
                  f"recovery_rate {recovery_rate:,.2f} "
                  f"accrued_interest {accrued_interest * 1e6:,.2f} "
                  f"clean_settlement_amount {(upfront_charge_clean) * 1e6:,.2f} "
                  f"dirty_settlement_amount: {(upfront_charge_dirty) * 1e6:,.2f} ")

        a = [wall_time_list]
        print("average execution {0}".format(average(a)))

        os.remove(self.holiday_filename)

        """ assert to below """
        """accrued = -24333.3333333333
        clean_settlement_amount = -171870.16640939
        dirty_settlement_amount = -196203.499742724"""

        self.assertAlmostEqual((upfront_charge_dirty) * 1e6, -196203.499742724)
        self.assertAlmostEqual((upfront_charge_clean) * 1e6, -171870.16640939)
        self.assertAlmostEqual(accrued_interest * 1e6, -24333.3333333333)


if __name__ == '__main__':
    unittest.main()
