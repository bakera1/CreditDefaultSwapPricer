/*
 * ISDA CDS Standard Model
 *
 * Copyright (C) 2009 International Swaps and Derivatives Association, Inc.
 * Developed and supported in collaboration with Markit
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the ISDA CDS Standard Model Public License.
 */

#include "cx.h"

extern "C" double* calculate_cds_par_spread(
 TDate baseDate,				
 TDate maturityDate,			
 TCurve *discountCurve, 		
 TCurve *spreadCurve, 			
 TDate effectiveDate,			
 double recoveryRate,			
 double couponRate,				
 int isPriceClean,				
 int verbose,					
 char **endDateTenors,	        
 int nbEndDates
 );

extern "C" TDate* calculate_cds_roll_dates(
 TDate baseDate,
 char **rollExpiries,
 int n,
 int verbose
);

extern "C" double calculate_cds_price(
 TDate baseDate,
 TDate maturityDate,
 TCurve *discountCurve,
 TCurve *spreadCurve,
 TDate 	tradeDate,
 double recoveryRate,
 double couponRate,
 int isPriceClean,
 int verbose
);

extern "C" TCurve* build_zero_interest_rate_curve_rofr(
 TDate baseDate,
 double *rates,
 char **expiries,
 int n,
 char *types,
 char* swap_floatingDayCountConvention,
 char* swap_fixedDayCountConvention,
 char* swap_fixedPaymentFrequency,
 char* swap_floatingPaymentFrequency,
 char* c_holiday_filename,
 int verbose
 );

extern "C" TCurve* build_zero_interest_rate_curve2(
 TDate baseDate,
 double *rates,
 char **expiries,
 long int *maturities,
 int verbose
);

extern "C" TCurve* build_zero_interest_rate_curve(
 TDate baseDate,
 double *rates,
 char **expiries,
 int verbose
);

extern "C" TCurve* build_credit_spread_par_curve(
 TDate baseDate,
 TCurve* discountCurve,
 TDate 	tradeDate,
 double *rates,
 long int *dates,
 double recoveryRate,
 int n,
 int verbose
);

extern "C" double calculate_upfront_charge(
 TDate baseDate,				/* (I) base start date  */
 TDate maturityDate,			/* (I) cds scheduled termination date  */
 TDate effectiveDate,			/* (I) accrual from start date  */
 TDate settleDate,              /* (I) settlementDate 3 business days forward of baseDate */
 TCurve* curve, 		        /* (I) interest rate curve */
 double coupon_rate, 		    /* (I) fixed coupon payable in bps */
 double par_spread,             /* (I) par spread in bps*/
 double recovery_rate,          /* (I) recover rate as decimal 0.4 */
 double notional,               /* (I) notional */
 char* holiday_filename,        /* (I) holiday file pointer */
 int isPriceClean,              /* (I) is clean price upfront */
 int verbose				    /* (I) used to toggle echo info output */
 );

