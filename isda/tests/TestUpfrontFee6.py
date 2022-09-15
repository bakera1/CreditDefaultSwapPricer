import os
import unittest
import datetime
import uuid

from isda.isda import compute_isda_upfront, average
from isda.imm import date_by_adding_business_days


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
        self.swap_rates = [0.028122,
                           0.030161,
                           0.032012,
                           0.035599,
                           0.037935,
                           0.0365,
                           0.034499,
                           0.03319,
                           0.032379,
                           0.031959,
                           0.03167,
                           0.031501,
                           0.031431,
                           0.031471,
                           0.031581,
                           0.031671,
                           0.031091,
                           0.030011,
                           0.029012]

        self.swap_tenors = ['1M', '2M', '3M', '6M', '1Y', '2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y', '10Y', '12Y',
                            '15Y', '20Y', '25Y', '30Y']

        # economics of trade 1% fixed coupon
        self.coupon = 100.0
        self.dt_trade_date = datetime.datetime(2022, 9, 13)
        self.trade_date = self.dt_trade_date.strftime('%d/%m/%Y')
        self.settle_date = date_by_adding_business_days(self.dt_trade_date, 3).strftime('%d/%m/%Y')
        self.accrual_start_date = '21/06/2022'
        self.maturity_date = '20/06/2027'
        self.notional = 150.0
        self.is_buy_protection = 1  # only ever buy or sell protection!
        self.verbose = 0

    def tearDown(self):
        pass

    def test_compute_isda_upfront(self):

        self.credit_spread_list = [82.86 / 10000., 83.86 / 10000., 85.90 / 10000., 86.90 / 10000.]
        self.recovery_rate_list = [0.4, 0.4, 0.4, 0.4]

        """ EUR ACT/360, 30/360, 1Y, 1Y """
        self.swapFixedDayCountConvention = 'ACT/360'
        self.swapFloatingDayCountConvention = 'ACT/360'
        self.swapFixedPaymentFrequency = '1Y'
        self.swapFloatingPaymentFrequency = '1Y'

        unique_filename = str(uuid.uuid4())
        self.holiday_filename = f'{unique_filename}.dat'
        self.holiday_list = [16010101, 20180320, 20220620]

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
                                     self.settle_date,
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
                  f"accrued {accrued_interest * 1e6:,.2f} "
                  f"clean_settlement_amount {(upfront_charge_clean) * 1e6:,.2f} "
                  f"dirty_settlement_amount: {(upfront_charge_dirty) * 1e6:,.2f} ")

        a = [wall_time_list]
        print("average execution {0}".format(average(a)))

        os.remove(self.holiday_filename)



if __name__ == '__main__':
    unittest.main()
