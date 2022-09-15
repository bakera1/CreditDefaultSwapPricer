import os
import unittest
import datetime
import uuid

from isda.isda import compute_isda_upfront, average, cds_all_in_one_exclude_ir_tenor_dates
from isda.imm import imm_date_vector


class MyTestCase(unittest.TestCase):
    """
        Testcase that has been reconciled with output from MarkIT partners online calculator and
        separate ISDA source; these figures are accurate to 11 decimal places and battle tested
        enough to be useful for more than just indicative risk.

        i) test coverage needs to be extended to handle cases over weekends & holidays
        ii) for now the coverage is a simple buy/sell protection flat spread trade

        /****** Script for SelectTopNRows command from SSMS  ******/
SELECT TOP (1000) [locked]
      ,[market_operation]
      ,[trade_id]
      ,[version]
      ,[market_operation_id]
      ,[trade_name]
      ,[trade_type]
      ,[fund]
      ,[risk_class]
      ,[strategy_id]
      ,[group_id]
      ,[instrument_id]
      ,[curve_id]
      ,[Prtf_id]
      ,[Model]
      ,[maturity]
      ,[coupon]
      ,[instrument_ccy]
      ,[schedule]
      ,[attach_original]
      ,[detach_original]
      ,[attach_actual]
      ,[detach_actual]
      ,[factor]
      ,[option_type]
      ,[strike]
      ,[exercise_date]
      ,[notional]
      ,[traded_notional]
      ,[direction]
      ,[trader_name]
      ,[counter_party]
      ,[quotation_type]
      ,[quote] * 10000 as [quote]
      ,[trade_date]
      ,[start_date]
      ,[first_coupon_date]
      ,[accrued]
      ,[clean_settlement_amount]
      ,[dirty_settlement_amount]
      ,[settlement_ccy]
      ,[dirty_settlement_amount_USD]
      ,[settlement_date]
      ,[transaction_type]
      ,[DTCC_ID]
      ,[groupHeader_id]
      ,[db_groupHeader_id]
      ,[initial_margin]
      ,[novation_type]
      ,[novation_amount]
      ,[remaining_ctpy]
      ,[stepIn_ctpy]
      ,[stepOut_ctpy]
      ,[trade_comment]
      ,[calypso_id]
      ,[commission]
      ,[curr_factor]
      ,[unfactored_notional]
      ,[set_id]
      ,[status]
      ,[last_date]
      ,[actual_counterparty]
      ,[email_sent]
      ,[original_notional]
      ,[repo_cash_price]
      ,[haircut]
      ,[repo_rate_type]
      ,[repo_fixed_rate]
      ,[repo_spread]
      ,[all_in_rate]
      ,[spread]
      ,[start_cash]
      ,[end_cash]
      ,[day_count_convention]
      ,[end_date]
      ,[created_datetime]
      ,[updated_datetime]
  FROM [SCB_Blotter].[orm].[scb_trade_universe_view2] where [trade_date] = '31 Aug 2022' and quotation_type = 'Flat Spread (bps)'

  -- mezz tranche; zero recovery assumption; sub indicies 20%
  -- ??? instrument to recovery ??? SQL ???

  select 12000000/1e6

  -- instrument CDS
  select * from [SCB_Blotter].[dbo].[recovery_rate] where instrument_type = '{}' and instrument = '{}'
  -- tranche
	-- sub
  -- 0.4

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
        self.settle_date = '05/09/2022'
        self.effective_date = '01/09/2022'
        self.accrual_start_date = '20/06/2022'
        self.maturity_date = '20/12/2026'
        self.notional = 12.0
        self.is_buy_protection = 0  # only ever buy or sell protection!
        self.verbose = 1

    def tearDown(self):
        pass

    def test_compute_isda_upfront(self):
        """
        Process finished with exit code 0
        credit_spread 45.0 recovery_rate 0.4 upfront_charge: 27573.02664720266 pv_clean (clean price) 102.57219208021354 dirty_price (Cash Settlement Amount) 27471.92080213547 ai 1750.0000000000016
        credit_spread 55.0 recovery_rate 0.4 upfront_charge: 22808.98548867634 pv_clean (clean price) 102.09576148061264 dirty_price (Cash Settlement Amount) 22707.614806126363 ai 1750.0000000000016
        credit_spread 65.0 recovery_rate 0.4 upfront_charge: 18084.047153034346 pv_clean (clean price) 101.62324051685925 dirty_price (Cash Settlement Amount) 17982.40516859251 ai 1750.0000000000016
        credit_spread 75.0 recovery_rate 0.4 upfront_charge: 13397.884539847697 pv_clean (clean price) 101.15459650030917 dirty_price (Cash Settlement Amount) 13295.965003091651 ai 1750.0000000000016
        credit_spread 85.0 recovery_rate 0.4 upfront_charge: 8750.17330450548 pv_clean (clean price) 100.68979701753237 dirty_price (Cash Settlement Amount) 8647.970175323704 ai 1750.0000000000016
        average execution (23.8,)
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

        """ assert to below """
        """accrued = -24333.3333333333
        clean_settlement_amount = -171870.16640939
        dirty_settlement_amount = -196203.499742724"""

        self.assertAlmostEqual((upfront_charge_dirty) * 1e6, -196203.499742724)
        self.assertAlmostEqual((upfront_charge_clean) * 1e6, -171870.16640939)
        self.assertAlmostEqual(accrued_interest * 1e6, -24333.3333333333)


if __name__ == '__main__':
    unittest.main()
