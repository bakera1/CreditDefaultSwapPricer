#!/usr/bin/env python

############################################################
# example call to all in one call wrapper call in JPM model
# returns
# std::vector<double> cds_all_in_one (
# std::string trade_date,					/* (I) trade date of cds as DD/MM/YYYY */
# std::string effective_date,				/* (I) effective date of cds as DD/MM/YYYY */
# std::string maturity_date,				/* (I) maturity date of cds as DD/MM/YYYY */
# std::string value_date,					/* (I) date to value the cds DD/MM/YYYY */
# std::string accrual_start_date,			/* (I) maturity date of cds as DD/MM/YYYY */
# double recovery_rate,				        /* (I) recover rate of the curve in basis points */
# double coupon_rate,				        /* (I) CouponRate (e.g. 0.05 = 5% = 500bp) */
# std::vector<double> swap_rates, 		    /* (I) swap rates */
# std::vector<std::string> swap_tenors,		/* (I) swap tenors "1M", "2M" */
# std::vector<double> spread_rates,		    /* (I) spread spreads */
# std::vector<std::string> spread_tenors,	/* (I) spread tenors "6M", "1Y" */
# std::vector<std::string> imm_dates		/* (I) imm dates */
# )
############################################################

import datetime

from isda.isda import cds_all_in_one_exclude_ir_tenor_dates
from isda.imm import imm_date_vector

# EUR interest rate curve
swap_rates = [-0.00369, -0.00341, -0.00329, -0.00278, -0.00222, -0.00191, -0.00134, 0.0007, 0.00276, 0.00461, 0.00621,
              0.00762, 0.00884, 0.00994, 0.01091, 0.01248, 0.0141, 0.01541, 0.0158]

swap_tenors = ['1M', '2M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y',
               '10Y', '15Y', '20Y', '30Y']

# spread curve
credit_spreads = [0.0021768492292503962] * 8
credit_spread_tenors = ['6M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']

# value asofdate
sdate = datetime.datetime(2018, 2, 8)
value_date = sdate.strftime('%d/%m/%Y')

# economics of trade
recovery_rate = 0.4
coupon_list = [100]
trade_date = '12/12/2014'
effective_date = '13/12/2014'
accrual_start_date = '20/09/2014'
maturity_date = '20/12/2019'
notional = 1.0
is_buy_protection = 0  # only ever buy or sell protection!
verbose = 0

tenor_list = [0.5, 1, 2, 3, 4, 5, 7, 10]
day_count = 1
one_day = datetime.timedelta(1)

spread_roll_tenors = ['1D', '-1D', '-1W', '-1M', '-6M', '-1Y', '-5Y']
scenario_shifts = [-50, -10, 0, 10, 20, 50, 150, 100]

for day in range(day_count):

    # build imm_dates
    imm_dates = [f[1] for f in imm_date_vector(start_date=sdate,
                                               tenor_list=tenor_list)]
    if verbose:
        print(imm_dates)

    # skip any weekend dates
    if sdate.weekday() in [5, 6]:
        sdate = sdate + one_day
        continue

    value_date = sdate.strftime('%d/%m/%Y')
    for coupon in coupon_list:
        f = cds_all_in_one_exclude_ir_tenor_dates(trade_date,
                                                  effective_date,
                                                  maturity_date,
                                                  value_date,
                                                  accrual_start_date,
                                                  recovery_rate,
                                                  coupon,
                                                  notional,
                                                  is_buy_protection,
                                                  swap_rates,
                                                  swap_tenors,
                                                  credit_spreads,
                                                  credit_spread_tenors,
                                                  spread_roll_tenors,
                                                  imm_dates,
                                                  scenario_shifts,
                                                  verbose)

        # expand tuple
        pv_dirty, pv_clean, ai, cs01, dv01, duration_in_milliseconds = f[0]
        pvbp6m, pvbp1y, pvbp2y, pvbp3y, pvbp4y, pvbp5y, pvbp7y, pvbp10y = f[1]

        five_year_equivalent_notional = -cs01 / pvbp5y
        #print(
        #    "{0:.10}\tpv_dirty ({1:.6})\tcs01 ({2:.6})\tdv01 ({3:.6})\tpvbp5y {4:.6}\t5yeqnot ({5:.6})\ttime ({6:.6})\tai ({7:.6})".format(
        #        value_date,
        #        pv_dirty,
        #        cs01 * 1e6,
        #        dv01,
        #        pvbp5y,
        #        five_year_equivalent_notional,
        #        duration_in_milliseconds, ai))

    sdate = sdate + one_day
