import sys
import unittest
import datetime
from datetime import date

from isda import cds_index_all_in_one, cds_all_in_one, average
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
        self.swap_rates = [-0.00369, -0.00340, -0.00329, -0.00271, -0.00219, -0.00187, -0.00149, 0.000040, 0.00159,0.00303, 0.00435, 0.00559, 0.00675, 0.00785, 0.00887]
        self.swap_tenors = ['1M', '2M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y', '10Y']
        self.swap_maturity_dates = ['12/02/2018', '12/03/2018', '10/04/2018', '10/07/2018', '10/10/2018', '10/01/2019'
            , '10/01/2020', '10/01/2021', '10/01/2022', '10/01/2023', '10/01/2024', '10/01/2025', '10/01/2026', '10/01/2027'
            , '10/01/2028']


        # spread curve download from markit
        self.credit_spreads = [0.84054, 0.58931, 0.40310, 0.33168, 0.30398, 0.28037, 0.25337, 0.23090]
        self.credit_spread_tenors = ['6M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']

        # economics of trade
        self.recovery_rate = 0.55000
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

    def test_sell_protection_index(self):
        """ method to specifically price an index cds """
    
        self.sdate = datetime.datetime(2018, 1, 8)
        self.value_date = self.sdate.strftime('%d/%m/%Y')
        self.verbose = 0
        self.is_buy_protection = 0
        
        # simulate an index with 125 names;; 
        self.credit_spread_list = [self.credit_spreads]*125
        self.recovery_rate_list = [self.recovery_rate]*125

        # build imm_dates TODO: hide this away internally?
        self.imm_dates = [f[1] for f in imm_date_vector(
            start_date=self.sdate, tenor_list=self.tenor_list)]

        wall_time_list = list()
        for i in range(0,20):
            f = cds_index_all_in_one(self.trade_date,
                                   self.effective_date,
                                   self.maturity_date,
                                   self.value_date,
                                   self.accrual_start_date,
                                   self.recovery_rate_list,
                                   self.coupon,
                                   self.notional,
                                   self.is_buy_protection,
                                   self.swap_rates,
                                   self.swap_tenors,
                                   self.swap_maturity_dates,
                                   self.credit_spread_list,
                                   self.credit_spread_tenors,
                                   self.spread_roll_tenors,
                                   self.imm_dates,
                                   self.scenario_shifts,
                                   self.verbose) 
          
            pv_dirty, pv_clean, ai, duration_in_milliseconds = f[1]
            wall_time_list.append(float(duration_in_milliseconds))        
            print("cob_date: {0} pv_dirty: {1:.6f} pv_clean: {2:.6f} ai: {3:.6f} wall_time: {4} (ms)".format(self.value_date,
                        pv_dirty, pv_clean, ai, duration_in_milliseconds))
        a = [wall_time_list]
        print("average execution {0}".format(average(a)))         
if __name__ == '__main__':
	unittest.main()
