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

    @unittest.skip
    def test_two_factor_shift(self):
        """
        
            roll and roll shocks generate a surface of pv change;
            for each shock the vector of roll tenors is evaluated
           
           The example below is a typical output from shock vector [-10, 0, 10] which translates internally 
           in the scenario engine; via the formula below; you can see that -10 is translated 
           into a -10/100 or -0.1 * spread_rate value and merged into the original spread_rates. This has the overall
           affect to move the spread_rate lower by 10% ahead of shocking the 
           
           spread_rates[r] + spread_rates[r]  * scenario_tenors[s]/100;
            
            -10 (0.024377398537551408, 0.017571131660956488, 0.007359432714929524, -0.0317885280270698, 
                -0.2922965009356705, -0.602319069762766, -1.1921043554642177)
            0 (0.0050220109323667605, -0.0016744535183860904, -0.01172141527276311, -0.0502382139885996, 
                -0.3065609282865831, -0.6116351775358528, -1.1921043554642177)
            10 (-0.014324638086876014, -0.020911398152265066, -0.030793768790011236, -0.06867995379960933, 
                -0.3208205888005652, -0.6209492443307575, -1.1921043554642177)

            The output above has been generated for 7 separate shocks to the time to maturity. It should be possible 
            to compute an entire surface before and after the maturity date of each CDS instrument using this approach
            which can provide detailed information around the roll of each CDS contract.
        
        :return: 
        """

        self.sdate = datetime.datetime(2018, 1, 8)
        self.value_date = self.sdate.strftime('%d/%m/%Y')
        self.verbose = 0
        self.is_buy_protection = 0

        # used to generate and shock roll dataset
        self.spread_roll_tenors = ['1D', '-1D', '-1W', '-1M', '-6M', '-1Y', '-5Y']
        self.scenario_shifts = [-10, 0, 10]

        # build imm_dates TODO: hide this away internally somewhere?
        self.imm_dates = [f[1] for f in imm_date_vector(start_date=self.sdate, tenor_list=self.tenor_list)]

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

        # results to compare against
        self.spread_roll_tenors_results = {-10: [0.024377398537551408, 0.017571131660956488, 0.007359432714929524
            , -0.0317885280270698, -0.2922965009356705, -0.602319069762766, -1.1921043554642177]
                                         , 0: [0.0050220109323667605, -0.0016744535183860904, -0.01172141527276311
                , -0.0502382139885996, -0.3065609282865831, -0.6116351775358528, -1.1921043554642177]
                                         , 10:[-0.014324638086876014, -0.020911398152265066, -0.030793768790011236
                , -0.06867995379960933, -0.3208205888005652, -0.6209492443307575, -1.1921043554642177]}

        # confirm that we have managed to generate the accurate number of scenario details
        #
        self.assertTrue(len(f[2:]), 3)
        # confirm we have the same dataset
        for i, a in enumerate(f[2:]):
            for test_value, result_value in zip(a, self.spread_roll_tenors_results[self.scenario_shifts[i]]):
                self.assertAlmostEquals(test_value, result_value)

    @unittest.skip
    def test_single_factor_shift(self):
        """

            base case roll test; 
            
            '1D' - moves the roll date one day past maturity 
            '-1D' - moves the stepin date one day closer to maturity
            '-1W' - moves stepin one week closer to maturity
            '-1M' - 1 month closer
            '-6M' - 6 months closer
            '-1Y' - 1 whole year closer
            '-5Y' - 5 whole years closer

        :return: 
        """
        self.sdate = datetime.datetime(2018, 1, 8)
        self.value_date = self.sdate.strftime('%d/%m/%Y')
        self.verbose = 0
        self.is_buy_protection = 0

        # used to generate and shock roll dataset
        self.spread_roll_tenors = ['1D', '-1D', '-1W', '-1M', '-6M', '-1Y', '-5Y']
        self.scenario_shifts = [0]

        # build imm_dates TODO: hide this away internally somewhere?
        self.imm_dates = [f[1] for f in imm_date_vector(start_date=self.sdate, tenor_list=self.tenor_list)]

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

        # self.spread_roll_tenors zero shift
        self.spread_roll_tenors_results = [0.0050220109323667605, -0.0016744535183860904, -0.01172141527276311, -0.0502382139885996
            ,-0.3065609282865831, -0.6116351775358528, -1.1921043554642177]

        for test_value, result_value in zip(f[2:][0], self.spread_roll_tenors_results):
            self.assertAlmostEquals(test_value, result_value)


    def test_1day_roll_buy_protection_cds_shift(self):
        """
    
            base case roll test;     
            '-1D' - moves the stepin date one day closer to maturity
    
        :return: 
        """
        self.sdate = datetime.datetime(2018, 1, 8)
        self.value_date = self.sdate.strftime('%d/%m/%Y')
        self.verbose = 0
        self.is_buy_protection = 1

        # used to generate and shock roll dataset
        self.spread_roll_tenors = ['-1D', '-1W', '-1M', '-1Y']
        self.scenario_shifts = [0]

        # build imm_dates TODO: hide this away internally somewhere?
        self.imm_dates = [f[1] for f in imm_date_vector(start_date=self.sdate, tenor_list=self.tenor_list)]

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

        # self.spread_roll_tenors zero shift
        self.spread_roll_tenors_results = [-0.00167445351801]

        for test_value, result_value in zip(f[2:][0], self.spread_roll_tenors_results):
            self.assertAlmostEquals(f[0][1]-test_value, result_value)


if __name__ == '__main__':
    unittest.main()
