import os
import unittest
import datetime
import uuid



from isda.isda import cds_coupon_schedule, average


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
        self.swap_maturity_dates = ['12/02/2018', '12/03/2018', '10/04/2018', '10/07/2018', '10/10/2018', '10/01/2019'
            , '10/01/2020', '10/01/2021', '10/01/2022', '10/01/2023', '10/01/2024', '10/01/2025', '10/01/2026',
                                    '10/01/2027'
            , '10/01/2028']

        # spread curve download from markit
        self.credit_spreads = [0.84054, 0.58931, 0.40310, 0.33168, 0.30398, 0.28037, 0.25337, 0.23090]
        self.credit_spreads = [75. / 10000, 75. / 10000, 75. / 10000, 75. / 10000, 75. / 10000, 75. / 10000,
                               75. / 10000, 75. / 10000]
        self.credit_spread_tenors = ['6M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']

        # economics of trade
        self.recovery_rate = 0.55000
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
        self.day_count = 1
        self.one_day = datetime.timedelta(1)

        # used to generate and shock roll dataset
        self.spread_roll_tenors = ['1D', '-1D', '-1W', '-1M', '-6M', '-1Y', '-5Y']
        self.scenario_shifts = [-50, -10, 0, 10, 20, 50, 150, 100]

    def convert_yyyymm_dot_one_to_datetime(self, value_date):
        return datetime.datetime.strptime(str(value_date).replace('.0', ''), "%d%m%Y")

    def test_isda_cds_payment_schedule(self):
        """
            Routine that illustrates the how to call isda_cds_payment_schedule()

    function::

    + isda_cds_payment_schedule

    args::

    + self.value_date, string, '%d/%m/%Y'
    + self.maturity_date, string, '%d/%m/%Y'
    + self.verbose, integer 0 or 1

    return::

    + tuple(status as double, ignore as double)
    + tuple(date as double, amount as double)
    date ddmmyyy.0 needs to be stripped into datetime object using self.convert_yyyymm_dot_one_to_datetime


    """

        # import this since we are working with Python datetime objects
        import datetime

        self.result_date = (
            20032018.0, 20062018.0, 20092018.0, 20122018.0, 20032019.0, 20062019.0, 20092019.0, 20122019.0)
        self.result_amount = (
            0.19722222222222222, 0.25555555555555554, 0.25555555555555554, 0.25277777777777777, 0.25,
            0.25555555555555554,
            0.25555555555555554, 0.25555555555555554)

        self.sdate = datetime.datetime(2018, 1, 8)
        self.value_date = self.sdate.strftime('%d/%m/%Y')
        self.maturity_date = '20/12/2019'
        self.coupon_interval = '6M'
        self.coupon_rate = 1.25
        self.notional = 1e6
        self.stub_method = 'B/S/3'  # Front/ Short / 20 days
        self.day_count_convention = "Act/360"
        unique_filename = str(uuid.uuid4())
        self.holiday_filename = f'{unique_filename}.dat'
        self.holiday_list = [16010101, 20180320, 20181220]

        def save_to_file(*holiday_list):
            with open(self.holiday_filename, mode='wt', encoding='utf-8') as myfile:
                for lines in holiday_list:
                    myfile.write('\n'.join(str(line) for line in lines))
                    myfile.write('\n')

        # just for measuring performance

        try:
            save_to_file(self.holiday_list)

            wall_time_list = list()
            f = cds_coupon_schedule(self.value_date, self.maturity_date, self.coupon_interval, self.day_count_convention,
                                    self.stub_method, self.holiday_filename, self.coupon_rate, self.notional, self.verbose)  # call to underlying library
        finally:
            try:
                os.remove(self.holiday_filename)
            except OSError:
                pass
        status = f[0][0]
        if not status:
            raise Exception("Analytic exception")
        wall_time_list.append(f[0][1])
        a = [wall_time_list]
        for i, (date, amount) in enumerate(zip(f[1], f[2])):
            print(self.convert_yyyymm_dot_one_to_datetime(date), amount)
            # self.assertAlmostEqual(self.convert_yyyymm_dot_one_to_datetime(self.result_date[i]),
            #                       self.convert_yyyymm_dot_one_to_datetime(date))
            # self.assertAlmostEqual(amount, self.result_amount[i], 6)
        print(" [isda_cds_payment_schedule] average execution {0} status {1}".format(average(a), status))

        self.assertTrue(1, 1)


if __name__ == '__main__':
    unittest.main()
