import unittest
import datetime

from isda.isda import cds_all_in_one
from isda.imm import imm_date_vector


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
        self.credit_spreads = [ 0.00081, 0.0009, 0.00181, 0.00293, 0.00439, 0.00613, 0.00923, 0.01119]
        self.credit_spread_tenors = ['6M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']

        # economics of trade
        self.recovery_rate = 0.40000
        self.coupon = 100.0
        self.trade_date = '12/12/2014'
        self.effective_date = '13/12/2014'
        self.accrual_start_date = '20/9/2014'
        self.maturity_date = '20/12/2019'
        self.notional = 2.0
        self.is_buy_protection = 1  # only ever buy or sell protection!
        self.verbose = 0

        # TODO: try and remove need for this!
        self.tenor_list = [0.5, 1, 2, 3, 4, 5, 7, 10]

    def tearDown(self):
        pass

    def test_two_factor_shift(self):
        """ method to test roll and roll shocks generate a surface of pv change """
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
        self.spread_roll_tenors = ['1Y','1D', '-1D', '-1W', '-1M', '-6M', '-1Y']
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

        pv_clean = f[0][1]

        # results to compare against
        self.spread_roll_tenors_results = {-10: [0.04387513244181401, 0.03306420268550876, 0.03302212083102655,
                                                 0.032769619019361866, 0.031801536455466885,
                                                 0.025356314262256027, 0.01767911535374796]
                                         , 0: [0.042111643439626215, 0.03234206758048001, 0.03230149347632522,
                                               0.03205803736866009, 0.031124617333038864,
                                               0.024909464222462, 0.017504780143193628]
                                         , 10:[0.040349886127636986, 0.03162025310504571, 0.03158118526362845,
                                               0.031346766012800564, 0.030447975828985945,
                                               0.024462724355530034, 0.01733046875873452]}
        # confirm that we have managed to generate the accurate number of scenario details
        #
        # confirm we have the same dataset
        for i, test_value_list in enumerate(f[3:]):
            for test_value, result_value in zip(test_value_list, self.spread_roll_tenors_results[self.scenario_shifts[i]]):
                self.assertAlmostEqual(test_value, result_value, 4)

    def test_single_factor_shift(self):
        """ method to test roll and roll shocks """
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
        # both positive and negative; -1D moves the maturity date one day closer to stepIn
        # whilst 1D pushes the scheduled termination date further out increasing the TTM.
        self.spread_roll_tenors = ['1D', '-1D', '-1W', '-1M', '-6M', '-1Y']
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

        pv_clean = f[0][1]

        # self.spread_roll_tenors zero shift
        self.spread_pv_clean_result = 0.03234206758048001
        # self.spread_roll_tenors zero shift
        self.spread_roll_tenors_results = [0.03234206758048001, 0.03230149347632522,
                                           0.03205803736866009, 0.031124617333038864, 0.024909464222462,
                                           0.017504780143193628]

        for test_value, result_value in zip(list(f[3]), self.spread_roll_tenors_results):
            self.assertAlmostEqual(pv_clean-test_value, self.spread_pv_clean_result-result_value, 4)

    def test_1day_roll_buy_protection_cds_shift(self):
        """ method to test roll simple 1 day clean roll pv """
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

        pv_clean = f[0][1]

        # self.spread_roll_tenors zero shift
        self.spread_pv_clean_result = -0.03234206758048001
        self.spread_roll_tenors_results = [-0.03230149347632522, -0.03205803736866009,
                                           -0.031124617333038864, -0.017504780143193628]

        for test_value, result_value in zip(list(f[3]), self.spread_roll_tenors_results):
            self.assertAlmostEqual(pv_clean-test_value, self.spread_pv_clean_result-result_value, 4)


if __name__ == '__main__':
    unittest.main()
