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
#)
############################################################

import datetime
from isda import cds_all_in_one
from imm import imm_date_vector

# EUR interest rate curve
swap_rates = [-0.00369, -0.00341, -0.00328, -0.00274, -0.00223, -0.00186, -0.00128, 0.00046, 0.00217, 0.003, 0.00504,
              0.00626, 0.00739, 0.00844, 0.00941, 0.01105, 0.01281, 0.01436, 0.01506]

swap_tenors = ['1M', '2M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y',
               '10Y', '15Y', '20Y', '30Y']

# spread curve
credit_spreads = [0.00141154155739384] * 8
credit_spreads = [0.00141154155739384, 0.00241154155739384, 0.00341154155739384,
                  0.00441154155739384, 0.00541154155739384, 0.00541154155739384,
                  0.00541154155739384, 0.00541154155739384]
credit_spread_tenors = ['6M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']

# value asofdate
sdate = datetime.datetime(2018, 1, 23)
value_date = sdate.strftime('%d/%m/%Y')

# economics of trade
recovery_rate = 0.4
coupon_list = [100]
trade_date = '14/12/2014'
effective_date = '20/09/2014'
maturity_date = '20/12/2019'
accrual_start_date = '20/09/2014'
notional = 70.0 # 70MM EUR
is_buy_protection = 0
verbose = 0

tenor_list = [0.5, 1, 2, 3, 4, 5, 7, 10]
day_count = 22
one_day = datetime.timedelta(1)

spread_roll_tenors = ['1D', '1W', '1M', '2M', '3M', '4M', '6M', '1Y', '2Y', '3Y', '5Y']

for day in range(day_count):

    # build imm_dates
    imm_dates = [f[1] for f in imm_date_vector(start_date=sdate,
                                               tenor_list=tenor_list)]
    if verbose:
        print imm_dates

    # skip any weekend dates
    if sdate.weekday() in [5, 6]:
        sdate = sdate + one_day
        continue

    value_date = sdate.strftime('%d/%m/%Y')
    for coupon in coupon_list:

        base, pvbp, roll = cds_all_in_one(trade_date,
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
                           verbose)
        # expand tuple
        pv_dirty, cs01, dv01, duration_in_milliseconds = base
        pvbp6m, pvbp1y, pvbp2y, pvbp3y, pvbp4y, pvbp5y, pvbp7y, pvbp10y = pvbp
        roll1d, roll1w, roll1m, roll2m, roll3m, roll4m, roll6m, roll1y, roll2y, roll3y, roll5y = roll

        five_year_equivalent_notional = -cs01/pvbp5y
        print "{0:.10}\tpv_dirty ({1:.6})\tcs01 ({2:.6})\tdv01 ({3:.6})\tpvbp5y {4:.6}\t5yeqnot ({5:.6})\t1day roll ({6:.6})\ttime ({7:.6})".format(value_date,
                                                                                          pv_dirty,
                                                                                          cs01*1e6,
                                                                                          dv01,
                                                                                          pvbp5y,
                                                                                          five_year_equivalent_notional,
                                                                                          roll1d*1e6,
                                                                                          duration_in_milliseconds)
    sdate = sdate + one_day
