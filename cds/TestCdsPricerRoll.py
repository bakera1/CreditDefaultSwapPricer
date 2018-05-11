import unittest
import datetime
from datetime import date
from isda import cds_all_in_one
from imm import imm_date_vector


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
        self.swap_maturity_dates = ['12/2/2018', '12/3/2018', '10/4/2018', '10/07/2018', '10/10/2018', '10/1/2019'
            , '10/01/2020', '10/1/2021', '10/1/2022', '10/1/2023', '10/1/2024', '10/1/2025', '10/1/2026', '10/01/2027'
            , '10/01/2028']

        # spread curve download from markit
        self.credit_spreads = [0.00137467867844589] * 8
        self.credit_spread_tenors = ['6M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']

        # economics of trade
        self.recovery_rate = 0.40000
        self.coupon = 100.0
        self.trade_date = '12/12/2014'
        self.effective_date = '13/12/2014'
        self.accrual_start_date = '20/9/2014'
        self.maturity_date = '20/12/2019'
        self.notional = 70.0
        self.is_buy_protection = 1  # only ever buy or sell protection!
        self.verbose = 0

        # TODO: try and remove need for this!
        self.tenor_list = [0.5, 1, 2, 3, 4, 5, 7, 10]

    def tearDown(self):
        pass

    def test_roll(self):
        """

            TODO: include assert for each scenario shift

        :return: 
        """
        self.sdate = datetime.datetime(2018, 1, 8)
        self.value_date = self.sdate.strftime('%d/%m/%Y')
        self.verbose = 0
        self.is_buy_protection = 0

        # used to generate and shock roll dataset
        self.spread_roll_tenors = ['1D', '-1D', '-1W', '-1M', '-6M', '-1Y', '-5Y']
        self.scenario_shifts = [0]

        # build imm_dates TODO: hide this away internally?
        self.imm_dates = [f[1] for f in imm_date_vector(
            start_date=self.sdate, tenor_list=self.tenor_list)]

        f = cds_all_in_one(self.trade_date,
                           self.effective_date,
                           self.maturity_date,
                           self.value_date,
                           self.accrual_start_date,
                           self.recovery_rate,
                           self.coupon,
                           self.notional,
                           self.is_buy_protection,
                           self.swap_rates,
                           self.swap_tenors,
                           self.swap_maturity_dates,
                           self.credit_spreads,
                           self.credit_spread_tenors,
                           self.spread_roll_tenors,
                           self.imm_dates,
                           self.scenario_shifts,
                           self.verbose)

        for scenario, tt in enumerate(f[2:]):
            print self.scenario_shifts[scenario], tt

if __name__ == '__main__':
    unittest.main()
