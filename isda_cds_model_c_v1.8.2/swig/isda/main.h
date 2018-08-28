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
 TCurve* curve,
 double couponRate,
 int verbose
 );

int compute_isda_upfront(double coupon);

