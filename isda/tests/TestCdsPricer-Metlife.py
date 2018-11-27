import unittest
import datetime

from isda.isda import cds_all_in_one_exclude_ir_tenor_dates
from isda.imm import imm_date_vector


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
        self.swap_rates = [0.01896900000000, 0.02035500000000, 0.02347700000000, 0.02481900000000, 0.02481900000000
            , 0.02717200000000, 0.02654500000000, 0.02740500000000, 0.02785000000000
            , 0.02802000000000, 0.02818000000000, 0.02829000000000, 0.02845500000000
            , 0.02858500000000, 0.02868000000000]

        self.swap_tenors = ['1M', '2M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y', '10Y']

        # spread curve download from markit
        self.credit_spreads = [0.00081, 0.0009, 0.00181, 0.00293, 0.00439, 0.00613, 0.00923, 0.01119]
        self.credit_spread_tenors = ['6M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']

        # economics of trade
        self.recovery_rate = 0.40000
        self.coupon = 100.0
        self.trade_date = '13/9/2017'
        self.effective_date = '14/9/2017'
        self.accrual_start_date = '20/6/2014'
        self.maturity_date = '20/12/2022'
        self.notional = 2.0
        self.is_buy_protection = 0  # only ever buy or sell protection!
        self.verbose = 1

        # TODO: try and remove need for this!
        self.tenor_list = [0.5, 1, 2, 3, 4, 5, 7, 10]
        self.day_count = 1
        self.one_day = datetime.timedelta(1)

        # used to generate and shock roll dataset
        self.spread_roll_tenors = ['1D', '-1D', '-1W', '-1M', '-6M', '-1Y', '-5Y']
        self.scenario_shifts = [-50, -10, 0, 10, 20, 50, 150, 100]

    def tearDown(self):
        pass

    def test_buy_protection(self):
        """ method to test buy protection single name CDS """

        self.sdate = datetime.datetime(2018, 4, 13)
        self.value_date = self.sdate.strftime('%d/%m/%Y')

        self.imm_dates = [f[1] for f in imm_date_vector(
            start_date=self.sdate, tenor_list=self.tenor_list)]

        self.verbose = 0
        f = cds_all_in_one_exclude_ir_tenor_dates(self.trade_date,
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
                                   self.credit_spreads,
                                   self.credit_spread_tenors,
                                   self.spread_roll_tenors,
                                   self.imm_dates,
                                   self.scenario_shifts,
                                   self.verbose)

        # expand tuple
        pv_dirty, pv_clean, ai, cs01, dv01, duration_in_milliseconds = f[0]
        pvbp6m, pvbp1y, pvbp2y, pvbp3y, pvbp4y, pvbp5y, pvbp7y, pvbp10y = f[1]

        self.assertAlmostEqual(0.04222146729753646, pv_dirty)
        self.assertAlmostEqual(0.040832578408647575, pv_clean)
        self.assertAlmostEqual(0.001388888888888884, ai)
        self.assertAlmostEqual(-894.9987755496533, cs01 * 1.0e6)
        self.assertAlmostEqual(-9.59351861563179, dv01 * 1.0e6)

        six_month_equivalent_notional = -cs01 / pvbp6m
        one_year_equivalent_notional = -cs01 / pvbp1y
        two_year_equivalent_notional = -cs01 / pvbp2y
        three_year_equivalent_notional = -cs01 / pvbp3y
        four_year_equivalent_notional = -cs01 / pvbp4y
        five_year_equivalent_notional = -cs01 / pvbp5y
        seven_year_equivalent_notional = -cs01 / pvbp7y
        ten_year_equivalent_notional = -cs01 / pvbp10y

        # print six_month_equivalent_notional, one_year_equivalent_notional, two_year_equivalent_notional, \
        #    three_year_equivalent_notional, four_year_equivalent_notional, five_year_equivalent_notional, \
        #    seven_year_equivalent_notional, ten_year_equivalent_notional

        # self.assertAlmostEquals(307.495318062, six_month_equivalent_notional)
        # self.assertAlmostEquals(145.357246478, one_year_equivalent_notional)
        # self.assertAlmostEquals(70.8820514668, two_year_equivalent_notional)
        # self.assertAlmostEquals(46.8826264701, three_year_equivalent_notional)
        # self.assertAlmostEquals(35.1120297467, four_year_equivalent_notional)
        # self.assertAlmostEquals(28.1221873429, five_year_equivalent_notional)
        # self.assertAlmostEquals(20.2184428985, seven_year_equivalent_notional)
        # self.assertAlmostEquals(14.4072625131, ten_year_equivalent_notional)


if __name__ == '__main__':
    unittest.main()
