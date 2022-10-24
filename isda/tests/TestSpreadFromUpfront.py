import os
import unittest
import uuid

from isda.isda import compute_isda_upfront, average, calculate_spread_from_upfront_charge


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
        self.swap_rates = [0.032869,
                           0.035129,
                           0.037749,
                           0.04169,
                           0.04442,
                           0.043513,
                           0.041393,
                           0.039835,
                           0.038784,
                           0.037992,
                           0.037292,
                           0.036762,
                           0.036352,
                           0.036092,
                           0.035742,
                           0.035332,
                           0.034192,
                           0.032562,
                           0.031092
                           ]
        self.swap_tenors = ['1M', '2M', '3M', '6M', '1Y', '2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y', '10Y', '12Y',
                            '15Y', '20Y', '25Y', '30Y']

        # economics of trade 1% fixed coupon
        self.coupon = 500.0
        self.trade_date = '10/10/2022'
        self.settle_date = '13/10/2022'
        self.accrual_start_date = '20/09/2022'
        self.maturity_date = '20/12/2027'
        self.notional = 1.0
        self.is_buy_protection = 0  # only ever buy or sell protection!
        self.verbose = 0

    def tearDown(self):
        pass

    def test_compute_isda_upfront_back_to_spread(self):
        # simulate an index with 125 names;;

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
        recovery_rate = 0.3
        credit_spread = 775 / 10000.0

        #
        # compute the upfront clean & dirty from spread
        #

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

        print(f"credit_spread {credit_spread * 10000.:,.2f} "
              f"recovery_rate {recovery_rate:,.2f} "
              f"accrued {accrued_interest * 1e6:,.2f} "
              f"clean_settlement_amount {(upfront_charge_clean) * 1e6:,.2f} "
              f"dirty_settlement_amount: {(upfront_charge_dirty) * 1e6:,.2f} ")

        #
        # re-compute the original traded spread from clean upfront
        #

        is_charge_clean = 1
        f_clean = calculate_spread_from_upfront_charge(self.trade_date,
                                                       self.maturity_date,
                                                       self.accrual_start_date,
                                                       self.settle_date,
                                                       recovery_rate,
                                                       self.coupon,
                                                       self.notional,
                                                       self.is_buy_protection,
                                                       self.swap_rates,
                                                       self.swap_tenors,
                                                       upfront_charge_clean,
                                                       self.is_rofr,
                                                       is_charge_clean,
                                                       self.holiday_filename,
                                                       self.swapFloatingDayCountConvention,
                                                       self.swapFixedDayCountConvention,
                                                       self.swapFixedPaymentFrequency,
                                                       self.swapFloatingPaymentFrequency,
                                                       self.verbose)

        upfront_spread_from_clean_upfront, status, duration_in_milliseconds = f_clean

        wall_time_list.append(float(duration_in_milliseconds))
        print(f"upfront_charge_dirty {upfront_charge_dirty :,.2f} "
              f"recovery_rate {recovery_rate:,.2f} "
              f"upfront_spread {(upfront_spread_from_clean_upfront * 10000) :,.6f} ")

        #
        # re-compute the original traded spread from dirty upfront
        #

        is_charge_clean = 0
        f_dirty = calculate_spread_from_upfront_charge(self.trade_date,
                                                       self.maturity_date,
                                                       self.accrual_start_date,
                                                       self.settle_date,
                                                       recovery_rate,
                                                       self.coupon,
                                                       self.notional,
                                                       self.is_buy_protection,
                                                       self.swap_rates,
                                                       self.swap_tenors,
                                                       upfront_charge_dirty,
                                                       self.is_rofr,
                                                       is_charge_clean,
                                                       self.holiday_filename,
                                                       self.swapFloatingDayCountConvention,
                                                       self.swapFixedDayCountConvention,
                                                       self.swapFixedPaymentFrequency,
                                                       self.swapFloatingPaymentFrequency,
                                                       self.verbose)

        upfront_spread_from_dirty_upfront, status, duration_in_milliseconds = f_dirty

        wall_time_list.append(float(duration_in_milliseconds))
        print(f"upfront_charge_dirty {upfront_charge_dirty :,.2f} "
              f"recovery_rate {recovery_rate:,.2f} "
              f"upfront_spread {(upfront_spread_from_dirty_upfront * 10000) :,.6f} ")

        a = [wall_time_list]
        print("average execution {0}".format(average(a)))

        os.remove(self.holiday_filename)
        self.assertAlmostEqual(upfront_spread_from_clean_upfront * 10000., 775)
        self.assertAlmostEqual(upfront_spread_from_dirty_upfront * 10000., 775)


if __name__ == '__main__':
    unittest.main()
