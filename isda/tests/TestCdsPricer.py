import sys
import unittest
import datetime
from datetime import date

sys.path.append('/usr/local/lib/python2.7/dist-packages/isda')

from _isda import cds_all_in_one
from imm import imm_date_vector

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
        self.swap_rates = [-0.00369, -0.00340, -0.00329, -0.00271, -0.00219, -0.00187, -0.00149, 0.000040, 0.00159,
                           0.00303, 0.00435, 0.00559, 0.00675, 0.00785, 0.00887]
        self.swap_tenors = ['1M', '2M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y', '10Y']
        self.swap_maturity_dates = ['12/2/2018', '12/3/2018', '10/4/2018', '10/07/2018', '10/10/2018', '10/1/2019'
            , '10/01/2020', '10/1/2021', '10/1/2022', '10/1/2023', '10/1/2024', '10/1/2025', '10/1/2026', '10/01/2027'
            , '10/01/2028']


        # spread curve download from markit
        self.credit_spreads = [0.00137467867844589]*8
        self.credit_spread_tenors = ['6M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']

        # economics of trade
        self.recovery_rate = 0.40000
        self.coupon = 100.0
        self.trade_date = '12/12/2014'
        self.effective_date = '13/12/2014'
        self.accrual_start_date = '20/9/2014'
        self.maturity_date = '20/12/2019'
        self.notional = 70.0
        self.is_buy_protection = 1 # only ever buy or sell protection!
        self.verbose = 0

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

        self.sdate = datetime.datetime(2018, 1, 8)
        self.value_date = self.sdate.strftime('%d/%m/%Y')
        self.verbose = 0

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

        # expand tuple
        pv_dirty, pv_clean, ai, cs01, dv01, duration_in_milliseconds = f[0]
        pvbp6m, pvbp1y, pvbp2y, pvbp3y, pvbp4y, pvbp5y, pvbp7y, pvbp10y = f[1]

        # buy protection -ve npv
        # buy protection -ve npv
        # buy protection +ve cs01
        # buy protection +ve dv01

        self.assertAlmostEquals(-1.23099324435, pv_dirty)
        self.assertAlmostEquals(-1.19210435546, pv_clean)
        self.assertAlmostEquals(0.0388888888889, ai)
        self.assertAlmostEquals(14014.5916905, cs01 * 1.0e6)
        self.assertAlmostEquals(131.61798715, dv01 * 1.0e6)

        print("cob_date: {0} pv_dirty: {1} pv_clean: {2} ai: {3} cs01: {4} dv01: {5} wall_time: {6}".format(self.value_date,
                        pv_dirty, pv_clean, ai,cs01*1e6, dv01*1e6, duration_in_milliseconds))

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

        self.assertAlmostEquals(307.495318062, six_month_equivalent_notional)
        self.assertAlmostEquals(145.357246478, one_year_equivalent_notional)
        self.assertAlmostEquals(70.8820514668, two_year_equivalent_notional)
        self.assertAlmostEquals(46.8826264701, three_year_equivalent_notional)
        self.assertAlmostEquals(35.1120297467, four_year_equivalent_notional)
        self.assertAlmostEquals(28.1221873429, five_year_equivalent_notional)
        self.assertAlmostEquals(20.2184428985, seven_year_equivalent_notional)
        self.assertAlmostEquals(14.4072625131, ten_year_equivalent_notional)

    def test_sell_protection(self):

        self.sdate = datetime.datetime(2018, 1, 8)
        self.value_date = self.sdate.strftime('%d/%m/%Y')
        self.verbose = 0
        self.is_buy_protection = 0

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

        # expand tuple
        pv_dirty, pv_clean, ai, cs01, dv01, duration_in_milliseconds = f[0]
        pvbp6m, pvbp1y, pvbp2y, pvbp3y, pvbp4y, pvbp5y, pvbp7y, pvbp10y = f[1]

        # sell protection +ve npv
        # sell protection +ve npv
        # sell protection -ve cs01
        # sell protection -ve dv01

        self.assertAlmostEquals(1.23099324435, pv_dirty)
        self.assertAlmostEquals(1.19210435546, pv_clean)
        self.assertAlmostEquals(0.0388888888889, ai)
        self.assertAlmostEquals(-14014.5916905, cs01*1.0e6)
        self.assertAlmostEquals(-131.61798715, dv01 * 1.0e6)

        print("cob_date: {0} pv_dirty: {1} pv_clean: {2} ai: {3} cs01: {4} dv01: {5} wall_time: {6}".format(
            self.value_date,pv_dirty, pv_clean, ai, cs01 * 1e6, dv01 * 1e6, duration_in_milliseconds))


        six_month_equivalent_notional = -cs01 / pvbp6m
        one_year_equivalent_notional = -cs01 / pvbp1y
        two_year_equivalent_notional = -cs01 / pvbp2y
        three_year_equivalent_notional = -cs01 / pvbp3y
        four_year_equivalent_notional = -cs01 / pvbp4y
        five_year_equivalent_notional = -cs01 / pvbp5y
        seven_year_equivalent_notional = -cs01 / pvbp7y
        ten_year_equivalent_notional = -cs01 / pvbp10y

        self.assertAlmostEquals(307.495318062, six_month_equivalent_notional)
        self.assertAlmostEquals(145.357246478, one_year_equivalent_notional)
        self.assertAlmostEquals(70.8820514668, two_year_equivalent_notional)
        self.assertAlmostEquals(46.8826264701, three_year_equivalent_notional)
        self.assertAlmostEquals(35.1120297467, four_year_equivalent_notional)
        self.assertAlmostEquals(28.1221873429, five_year_equivalent_notional)
        self.assertAlmostEquals(20.2184428985, seven_year_equivalent_notional)
        self.assertAlmostEquals(14.4072625131, ten_year_equivalent_notional)

    def test_sell_protection_par_spread(self):

        self.sdate = datetime.datetime(2018, 1, 8)
        self.value_date = self.sdate.strftime('%d/%m/%Y')
        self.verbose = 0
        self.is_buy_protection = 0

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

        # expand tuple
        pv_dirty, pv_clean, ai, cs01, dv01, duration_in_milliseconds = f[0]
        pvbp6m, pvbp1y, pvbp2y, pvbp3y, pvbp4y, pvbp5y, pvbp7y, pvbp10y = f[1]
        ps_1m, ps_2m, ps_3M, ps_6M, ps_9M, ps_1Y, ps_2Y, ps_3Y, ps_4Y, ps_5Y, ps_6Y, ps_7Y, ps_8Y, ps_9Y, ps_10Y = f[2]
        
        self.assertAlmostEquals(0.00274826727324, ps_1m) 
        self.assertAlmostEquals(0.00274883148583, ps_2m) 
        self.assertAlmostEquals(0.00274929868985, ps_3M) 
        self.assertAlmostEquals(0.00274939866579, ps_6M) 
        self.assertAlmostEquals(0.00274936653181, ps_9M) 
        self.assertAlmostEquals(0.00274937754343, ps_1Y)
        self.assertAlmostEquals(0.00274932944417, ps_2Y) 
        self.assertAlmostEquals(0.00274932454643, ps_3Y) 
        self.assertAlmostEquals(0.00274932165857, ps_4Y) 
        self.assertAlmostEquals(0.0027493199385, ps_5Y)
        self.assertAlmostEquals(0.00274926894167, ps_6Y) 
        self.assertAlmostEquals(0.00274932296072, ps_7Y) 
        self.assertAlmostEquals(0.00274925367015, ps_8Y) 
        self.assertAlmostEquals(0.00274927195173, ps_9Y) 
        self.assertAlmostEquals(0.00274933238284, ps_10Y)
        
        # sell protection +ve npv
        # sell protection +ve npv
        # sell protection -ve cs01
        # sell protection -ve dv01

        self.assertAlmostEquals(1.23099324435, pv_dirty)
        self.assertAlmostEquals(1.19210435546, pv_clean)
        self.assertAlmostEquals(0.0388888888889, ai)
        self.assertAlmostEquals(-14014.5916905, cs01*1.0e6)
        self.assertAlmostEquals(-131.61798715, dv01 * 1.0e6)

        print("cob_date: {0} pv_dirty: {1} pv_clean: {2} ai: {3} cs01: {4} dv01: {5} wall_time: {6}".format(
            self.value_date,pv_dirty, pv_clean, ai, cs01 * 1e6, dv01 * 1e6, duration_in_milliseconds))


        six_month_equivalent_notional = -cs01 / pvbp6m
        one_year_equivalent_notional = -cs01 / pvbp1y
        two_year_equivalent_notional = -cs01 / pvbp2y
        three_year_equivalent_notional = -cs01 / pvbp3y
        four_year_equivalent_notional = -cs01 / pvbp4y
        five_year_equivalent_notional = -cs01 / pvbp5y
        seven_year_equivalent_notional = -cs01 / pvbp7y
        ten_year_equivalent_notional = -cs01 / pvbp10y

        self.assertAlmostEquals(307.495318062, six_month_equivalent_notional)
        self.assertAlmostEquals(145.357246478, one_year_equivalent_notional)
        self.assertAlmostEquals(70.8820514668, two_year_equivalent_notional)
        self.assertAlmostEquals(46.8826264701, three_year_equivalent_notional)
        self.assertAlmostEquals(35.1120297467, four_year_equivalent_notional)
        self.assertAlmostEquals(28.1221873429, five_year_equivalent_notional)
        self.assertAlmostEquals(20.2184428985, seven_year_equivalent_notional)
        self.assertAlmostEquals(14.4072625131, ten_year_equivalent_notional)

    @unittest.skip
    def test_roll(self):
        """
        
            TODO: include assert for each scenario shift
        
        :return: 
        """
        self.sdate = datetime.datetime(2018, 1, 8)
        self.value_date = self.sdate.strftime('%d/%m/%Y')
        self.verbose = 0
        self.is_buy_protection = 0


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
            print(self.scenario_shifts[scenario], tt)

if __name__ == '__main__':
	unittest.main()
