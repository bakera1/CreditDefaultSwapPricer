/*
 * ISDA CDS Standard Model
 *
 * Copyright (C) 2009 International Swaps and Derivatives Association, Inc.
 * Developed and supported in collaboration with Markit
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the ISDA CDS Standard Model Public License.
 */

#include "version.h"
#include "macros.h"
#include "cerror.h"
#include "tcurve.h"
#include "cdsone.h"
#include "convert.h"
#include "zerocurve.h"
#include "cds.h"
#include "cxzerocurve.h"
#include "dateconv.h"
#include "date_sup.h"
#include "busday.h"
#include "ldate.h"
#include "stub.h"

EXPORT TCurve* build_credit_spread_par_curve(
 TDate baseDate,				/* (I) base start date  */
 TCurve *discountCurve, 		/* (I) interest rate curve */
 TDate 	tradeDate,				/* (I) trade start date  */
 double *rates,					/* (I) raw credit swap rates */
 long int *dates,				/* (I) imm dates */
 double recoveryRate,			/* (I) recover rate in basis points */
 int n,							/* (I) number of benchmarm imm dates */
 int verbose					/* (I) determine if we want to echo info */
)
{

    static char    *routine = "build_credit_spread_par_curve";
    TCurve         *sc = NULL;
    int            payAccruedOnDefault = 1;
    char           **lines = NULL;
    TDateInterval  ivl;
    int            i=0;
    TDateInterval  ivlCashSettle;
    TDateInterval  couponInterval;
    long int       mmDCC=0;
    TDate          startDate;
    TDate          stepInDate;
    TDate          cashSettleDate;
    TStubMethod    stubMethod;
    int includes[8] = {1,1,1,1,1,1,1,1};
    int            status = 1;
    int 			nbDate = 8;

	JpmcdsErrMsgOn();

    if (JpmcdsErrMsgEnableRecord(20, 128) != SUCCESS) /* ie. 20 lines, each of max length 128 */
        goto done;

	if (JpmcdsStringToDateInterval("1D", routine, &ivl) != SUCCESS)
	{
		goto done;
	}

	if (JpmcdsStringToDateInterval("3D", routine, &ivlCashSettle) != SUCCESS)
	{
		goto done;
	}

	if (JpmcdsDateFwdThenAdjust(tradeDate, &ivl, JPMCDS_BAD_DAY_NONE, "None", &startDate) != SUCCESS)
	{
		goto done;
	}

	if(verbose){
	  printf("today = %d\n", (int)baseDate);
	  printf("startDate = %d\n", (int)tradeDate);
	}

	if (JpmcdsDateFwdThenAdjust(baseDate, &ivl, JPMCDS_BAD_DAY_NONE, "None", &stepInDate) != SUCCESS)
	{
		goto done;
	}
	if(verbose){
		printf("stepInDate = %d\n", (int)stepInDate);
	}

	if (JpmcdsDateFwdThenAdjust(baseDate, &ivlCashSettle, JPMCDS_BAD_DAY_MODIFIED, "None", &cashSettleDate) != SUCCESS)
	{
		goto done;
	}
	if(verbose){
		printf("cashSettleDate = %d\n", (int)cashSettleDate);
	}

    if (JpmcdsStringToDayCountConv("Act/360", &mmDCC) != SUCCESS)
        goto done;

    if (JpmcdsStringToDateInterval("Q", routine, &couponInterval) != SUCCESS)
        goto done;

    if (JpmcdsStringToStubMethod("F/S", &stubMethod)  != SUCCESS)
        goto done;

 /*
    EXPORT TCurve* JpmcdsCleanSpreadCurve
(TDate              today,            (I) Used as credit curve base date
 TCurve            *discountCurve,    (I) Risk-free discount curve
 TDate              startDate,        (I) Start of CDS for accrual and risk
 TDate              stepinDate,       (I) Stepin date
 TDate              cashSettleDate,   (I) Pay date
 long               nbDate,           (I) Number of benchmark dates
 TDate             *endDates,         (I) Maturity dates of CDS to bootstrap
 double            *couponRates,      (I) CouponRates (e.g. 0.05 = 5% = 500bp)
 TBoolean          *includes,         (I) Include this date. Can be NULL if
                                        all are included.
 double             recoveryRate,     (I) Recovery rate
 TBoolean           payAccOnDefault,  (I) Pay accrued on default
 TDateInterval     *couponInterval,   (I) Interval between fee payments
 long               paymentDCC,       (I) DCC for fee payments and accrual
 TStubMethod       *stubType,         (I) Stub type for fee leg
 long               badDayConv,
 char              *calendar
)

*/

	if(verbose){
		printf("calling JpmcdsBuildCleanSpreadCurve...\n");
	}
	
	do {
	
	    sc = JpmcdsCleanSpreadCurve
		    (baseDate,
		     discountCurve,
		     tradeDate,
		     stepInDate,
		     cashSettleDate,
		     nbDate,
		     dates,
		     rates,
		     includes,
		     recoveryRate,
		     payAccruedOnDefault,
		     &couponInterval,
		     mmDCC,
		     &stubMethod,
		     'F',
		     "None"
		    );
		    
		  recoveryRate -= 0.01;
		  if(verbose){  
		    printf("shiftedRecoveryRate = %f\n", recoveryRate);
		  }
            
	}while(sc == NULL);
	
	status = 0;

done:

    if (status != 0){

        printf("\n*** ERROR ***\n");

		printf("\n");
		printf("Error log contains:\n");
		printf("------------------:\n");

		lines = JpmcdsErrGetMsgRecord();
		if (lines == NULL)
			printf("(no log contents)\n");
		else
		{
			for(i = 0; lines[i] != NULL; i++)
			{
				if (strcmp(lines[i],"") != 0)
					printf("%s\n", lines[i]);
			}
		}
    }

    return sc;
}

/*
***************************************************************************
** Build IR zero curve.
***************************************************************************
*/

EXPORT TCurve* build_zero_interest_rate_curve2(
 TDate baseDate,			/* (I) integer base start date JpmCdsDate */
 double *rates,			/* (I) double array with 14 elements */
 char **expiries,		/* (I) array of char* of tenor strings "1M", "2M", "3M", "6M", "9M", "1Y", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y" */
 long int *maturities,
 int verbose
)
{
    static char  *routine = "BuildExampleZeroCurve";
    TCurve       *zc = NULL;
    char         *types = "MMMMMMSSSSSSSSS";
    //char         expiries[14] = {"1M", "2M", "3M", "6M", "9M", "1Y", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y"};
    TDate        *dates = NULL;
    //double        rates[14] = {1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9};
    TDate         baseDateShifted;
    long          swapFloatingDayCountConvention;
    TDateInterval ivlSwapFixedPaymentFrequency;
    TDateInterval ivlSwapFloatingPaymentFrequency;
    TDateInterval ivl2;
    long          swapFixedDayCountConvention;
    double        swapFixedFrequency;
    double        swapFloatingFrequency;
    char          badDayConv = 'M';
    char         *holidays = "None";
    int           i, n;

	if(verbose){
    	printf("build_zero_interest_rate_curve2::BaseDate = %d\n", (int)baseDate);
    }

    if (JpmcdsStringToDayCountConv("Act/360", &swapFloatingDayCountConvention) != SUCCESS)
        goto done;

    if (JpmcdsStringToDayCountConv("30/360", &swapFixedDayCountConvention) != SUCCESS)
        goto done;

	if (JpmcdsStringToDateInterval("1Y", routine, &ivlSwapFixedPaymentFrequency) != SUCCESS)
        goto done;

	if (JpmcdsStringToDateInterval("6M", routine, &ivlSwapFloatingPaymentFrequency) != SUCCESS)
        goto done;

    if (JpmcdsDateIntervalToFreq(&ivlSwapFixedPaymentFrequency, &swapFixedFrequency) != SUCCESS)
        goto done;

    if (JpmcdsDateIntervalToFreq(&ivlSwapFloatingPaymentFrequency, &swapFloatingFrequency) != SUCCESS)
        goto done;

	// move forward 2 days, today (base), tomorrow and spot!
    if (JpmcdsStringToDateInterval("2D", routine, &ivl2) != SUCCESS)
	{
		goto done;
	}
	if (JpmcdsDateFwdThenAdjust(baseDate, &ivl2, JPMCDS_BAD_DAY_MODIFIED, "None", &baseDateShifted) != SUCCESS)
	{
		goto done;
	}

	if(verbose){
    	printf("build_zero_interest_rate_curve2::BaseDateShifted = %d\n", (int)baseDateShifted);
    }

    n = strlen(types);

    if(verbose){
		printf("build_zero_interest_rate_curve2::n = %d\n", n);
	}
    dates = NEW_ARRAY(TDate, n);

	if (verbose) {
		printf("build_zero_interest_rate_curve2::n = %d\n", n);
	}

    for (i = 0; i < n; i++)
    {

		if (verbose) {
			printf("build_zero_interest_rate_curve2::n = %d\n", n);
		}

    	// DEPOSIT RATES
    	if (i<=6){
			if (JpmcdsBusinessDay(maturities[i], JPMCDS_BAD_DAY_NONE, "None", dates+i) != SUCCESS)
				{
					JpmcdsErrMsg ("%s: invalid interval for element[%d].\n", routine, i);
					goto done;
				}
    	}
    	else
    	{
    		// SWAP RATES
			if (JpmcdsBusinessDay(maturities[i], JPMCDS_BAD_DAY_MODIFIED, "None", dates+i) != SUCCESS)
			{
				JpmcdsErrMsg ("%s: invalid interval for element[%d].\n", routine, i);
				goto done;
			}
		}
		if(verbose){
    		printf("build_zero_interest_rate_curve2::dates = %d\n", (long int)dates[i]);
    	}
    }

	/*
EXPORT TCurve* JpmcdsBuildIRZeroCurve(
    TDate      valueDate,        (I) Value date
    char      *instrNames,       (I) Array of 'M' or 'S'
    TDate     *dates,            (I) Array of swaps dates
    double    *rates,            (I) Array of swap rates
    long       nInstr,           (I) Number of benchmark instruments
    long       mmDCC,            (I) DCC of MM instruments
    long       fixedSwapFreq,    (I) Fixed leg freqency
    long       floatSwapFreq,    (I) Floating leg freqency
    long       fixedSwapDCC,     (I) DCC of fixed leg
    long       floatSwapDCC,     (I) DCC of floating leg
    long       badDayConv,       (I) Bad day convention
    char      *holidayFile)      (I) Holiday file
{*/

	if(verbose){
    	printf("calling JpmcdsBuildIRZeroCurve...\n");
    }
    zc = JpmcdsBuildIRZeroCurve(
            baseDateShifted,
            types,
            dates,
            rates,
            n,
            swapFloatingDayCountConvention,
            (long) swapFixedFrequency,
            (long) swapFloatingFrequency,
            swapFixedDayCountConvention,
            swapFloatingDayCountConvention,
            badDayConv,
            holidays);
done:
    FREE(dates);
    return zc;
}

EXPORT TCurve* build_zero_interest_rate_curve(
 TDate baseDate,			/* (I) integer base start date JpmCdsDate */
 double *rates,			/* (I) double array with 14 elements */
 char **expiries,		/* (I) array of char* of tenor strings "1M", "2M", "3M", "6M", "9M", "1Y", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y" */
 int verbose
)
{
    static char  *routine = "build_zero_interest_rate_curve";
    TCurve       *zc = NULL;
    char         *types = "MMMMMMSSSSSSSSS";
    TDate        *dates = NULL;
    TDate         baseDateShifted;
    long          swapFloatingDayCountConvention;
    TDateInterval ivlSwapFixedPaymentFrequency;
    TDateInterval ivlSwapFloatingPaymentFrequency;
    TDateInterval ivl2;
    long          swapFixedDayCountConvention;
    double        swapFixedFrequency;
    double        swapFloatingFrequency;
    char          badDayConv = 'M';
    char         *holidays = "None";
    int           i, n;

	if(verbose){
    	printf("BaseDate = %d\n", (int)baseDate);
    }
    	// move forward 2 days, today (base), tomorrow and spot!
    if (JpmcdsStringToDateInterval("2D", routine, &ivl2) != SUCCESS)
	{
		goto done;
	}
	if (JpmcdsDateFwdThenAdjust(baseDate, &ivl2, JPMCDS_BAD_DAY_MODIFIED, "None", &baseDateShifted) != SUCCESS)
	{
		goto done;
	}

	if(verbose){
    	printf("build_zero_interest_rate_curve2::BaseDateShifted = %d\n", (int)baseDateShifted);
    }

	if (JpmcdsStringToDayCountConv("Act/360", &swapFloatingDayCountConvention) != SUCCESS)
        goto done;

    if (JpmcdsStringToDayCountConv("30/360", &swapFixedDayCountConvention) != SUCCESS)
        goto done;

	if (JpmcdsStringToDateInterval("1Y", routine, &ivlSwapFixedPaymentFrequency) != SUCCESS)
        goto done;

	if (JpmcdsStringToDateInterval("1Y", routine, &ivlSwapFloatingPaymentFrequency) != SUCCESS)
        goto done;

    if (JpmcdsDateIntervalToFreq(&ivlSwapFixedPaymentFrequency, &swapFixedFrequency) != SUCCESS)
        goto done;

    if (JpmcdsDateIntervalToFreq(&ivlSwapFloatingPaymentFrequency, &swapFloatingFrequency) != SUCCESS)
        goto done;

    n = strlen(types);

    dates = NEW_ARRAY(TDate, n);
    for (i = 0; i < n; i++)
    {
        TDateInterval tmp;

        if (JpmcdsStringToDateInterval(expiries[i], routine, &tmp) != SUCCESS)
        {
            JpmcdsErrMsg ("%s: invalid interval for element[%d].\n", routine, i);
            goto done;
        }

        if ( i <= 6 ){
        	if (JpmcdsDateFwdThenAdjust(baseDate, &tmp, JPMCDS_BAD_DAY_NONE, "None", dates+i) != SUCCESS)
			{
				JpmcdsErrMsg ("%s: invalid interval for element[%d].\n", routine, i);
				goto done;
			}
        }
        else{
			if (JpmcdsDateFwdThenAdjust(baseDate, &tmp, JPMCDS_BAD_DAY_MODIFIED, "None", dates+i) != SUCCESS)
			{
				JpmcdsErrMsg ("%s: invalid interval for element[%d].\n", routine, i);
				goto done;
			}
		}
    }

	/*
EXPORT TCurve* JpmcdsBuildIRZeroCurve(
    TDate      valueDate,        (I) Value date
    char      *instrNames,       (I) Array of 'M' or 'S'
    TDate     *dates,            (I) Array of swaps dates
    double    *rates,            (I) Array of swap rates
    long       nInstr,           (I) Number of benchmark instruments
    long       mmDCC,            (I) DCC of MM instruments
    long       fixedSwapFreq,    (I) Fixed leg freqency
    long       floatSwapFreq,    (I) Floating leg freqency
    long       fixedSwapDCC,     (I) DCC of fixed leg
    long       floatSwapDCC,     (I) DCC of floating leg
    long       badDayConv,       (I) Bad day convention
    char      *holidayFile)      (I) Holiday file
{*/

	if(verbose){
    	printf("calling JpmcdsBuildIRZeroCurve...\n");
    }

    zc = JpmcdsBuildIRZeroCurve(
            baseDateShifted,
            types,
            dates,
            rates,
            n,
            swapFloatingDayCountConvention,
            (long) swapFixedFrequency,
            (long) swapFloatingFrequency,
            swapFixedDayCountConvention,
            swapFloatingDayCountConvention,
            badDayConv,
            holidays);
done:
    FREE(dates);
    return zc;
}


EXPORT TCurve* build_zero_interest_rate_curve_rofr(
 TDate baseDate,			/* (I) integer base start date JpmCdsDate */
 double *rates,			    /* (I) double array with 14 elements */
 char **expiries,		    /* (I) array of char* of tenor strings "1M", "2M", "3M", "6M", "9M", "1Y", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y" */
 int n,                     /* (I) array len of rates */
 char *types,               /* (I) array of rate types "MMMMMMSSSSSSSSS" */
 char* swap_floatingDayCountConvention,
 char* swap_fixedDayCountConvention,
 char* swap_fixedPaymentFrequency,
 char* swap_floatingPaymentFrequency,
 char* holiday_filename,
 int verbose
)
{
    static char  *routine = "build_zero_interest_rate_curve_rofr";
    TCurve       *zc = NULL;
    TDate        *dates = NULL;
    TDate         baseDateShifted;
    long          swapFloatingDayCountConvention;
    TDateInterval ivlSwapFixedPaymentFrequency;
    TDateInterval ivlSwapFloatingPaymentFrequency;
    TDateInterval ivl2;
    long          swapFixedDayCountConvention;
    double        swapFixedFrequency;
    double        swapFloatingFrequency;
    char          badDayConv = 'M';
    int           i;

    int            status = 1;
    char           **lines = NULL;

    if (JpmcdsErrMsgFileName(routine, 1) != SUCCESS){
    		goto done;
    }

	if(verbose){
    	printf("BaseDate = %d\n", (int)baseDate);
    }
    	// move forward 2 days, today (base), tomorrow and spot!
    if (JpmcdsStringToDateInterval("2D", routine, &ivl2) != SUCCESS)
	{
		goto done;
	}

	/*int  JpmcdsDateFromBusDaysOffset
(TDate     fromDate,        (I) input date
 long      offset,          (I) number of business days
 char     *holidayFile,     (I) holiday file specification
 TDate    *result)          (O) resulting business date
{*/

	if (JpmcdsDateFromBusDaysOffset(baseDate, 2, "None", &baseDateShifted) != SUCCESS)
	{
		goto done;
	}

	/*if (JpmcdsDateFwdThenAdjust(baseDate, &ivl2, JPMCDS_BAD_DAY_NONE, "None", &baseDateShifted) != SUCCESS)
	{
		goto done;
	}*/

	/*if (JpmcdsDtFwdAny(baseDate, &ivl2, &baseDateShifted) != SUCCESS)
	{
		goto done;
	}*/

	if(verbose){
    	printf("build_zero_interest_rate_curve_rofr::baseDate = %d\n", (int)baseDate);
    	printf("build_zero_interest_rate_curve_rofr::baseDateShifted = %d\n", (int)baseDateShifted);
    }

	if (JpmcdsStringToDayCountConv(swap_floatingDayCountConvention, &swapFloatingDayCountConvention) != SUCCESS)
        goto done;

    if (JpmcdsStringToDayCountConv(swap_fixedDayCountConvention, &swapFixedDayCountConvention) != SUCCESS)
        goto done;

	if (JpmcdsStringToDateInterval(swap_fixedPaymentFrequency, routine, &ivlSwapFixedPaymentFrequency) != SUCCESS)
        goto done;

	if (JpmcdsStringToDateInterval(swap_floatingPaymentFrequency, routine, &ivlSwapFloatingPaymentFrequency) != SUCCESS)
        goto done;

    if (JpmcdsDateIntervalToFreq(&ivlSwapFixedPaymentFrequency, &swapFixedFrequency) != SUCCESS)
        goto done;

    if (JpmcdsDateIntervalToFreq(&ivlSwapFloatingPaymentFrequency, &swapFloatingFrequency) != SUCCESS)
        goto done;

    dates = NEW_ARRAY(TDate, n);
    for (i = 0; i < n; i++)
    {
        TDateInterval tmp;

        if (JpmcdsStringToDateInterval(expiries[i], routine, &tmp) != SUCCESS)
        {
            JpmcdsErrMsg ("%s: invalid interval for element[%d].\n", routine, i);
            goto done;
        }

        if (JpmcdsDateFwdThenAdjust(baseDateShifted, &tmp, JPMCDS_BAD_DAY_NONE, "None", dates+i) != SUCCESS)
        {
            JpmcdsErrMsg ("%s: invalid interval for element[%d].\n", routine, i);
            goto done;
        }

        if(verbose){
    	    printf("build_zero_interest_rate_curve_rofr::i = %d \n", (int)i);
    	    printf("build_zero_interest_rate_curve_rofr::dates = %d \n", dates[i]);
        }
    }

	/*
EXPORT TCurve* JpmcdsBuildIRZeroCurve(
    TDate      valueDate,        (I) Value date
    char      *instrNames,       (I) Array of 'M' or 'S'
    TDate     *dates,            (I) Array of swaps dates
    double    *rates,            (I) Array of swap rates
    long       nInstr,           (I) Number of benchmark instruments
    long       mmDCC,            (I) DCC of MM instruments
    long       fixedSwapFreq,    (I) Fixed leg frequency
    long       floatSwapFreq,    (I) Floating leg frequency
    long       fixedSwapDCC,     (I) DCC of fixed leg
    long       floatSwapDCC,     (I) DCC of floating leg
    long       badDayConv,       (I) Bad day convention
    char      *holidayFile)      (I) Holiday file
{*/

	if(verbose){
    	printf("calling JpmcdsBuildIRZeroCurve...\n");
    }

    zc = JpmcdsBuildIRZeroCurve(
            baseDateShifted,
            types,
            dates,
            rates,
            n,
            swapFloatingDayCountConvention,
            (long) swapFixedFrequency,
            (long) swapFloatingFrequency,
            swapFixedDayCountConvention,
            swapFloatingDayCountConvention,
            badDayConv,
            holiday_filename);


    if(verbose){
    	printf("calling JpmcdsBuildIRZeroCurve OK!\n");
    }

    status = 0;

done:
    FREE(dates);

    if (status != 0){
		printf("\n");
		printf("Error log contains:\n");
		printf("------------------:\n");

		lines = JpmcdsErrGetMsgRecord();
		if (lines == NULL)
			printf("(no log contents)\n");
		else
		{
			for(i = 0; lines[i] != NULL; i++)
			{
				if (strcmp(lines[i],"") != 0)
					printf("%s\n", lines[i]);
			}
		}
    }

    return zc;
}

/*
***************************************************************************
** Calculate upfront charge.
***************************************************************************
*/
EXPORT double calculate_upfront_charge
(
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
)
{
    static char  *routine = "calculate_upfront_charge";
    TDate         today;
    TDate         valueDate;
    TDate         startDate;
    TDate         benchmarkStart;
    TDate         stepInDate;
    /*TDate         settleDate;*/
    TDate         endDate;
    TBoolean      payAccOnDefault = 1;
    TDateInterval ivl;
    TDateInterval ivl2;
    TDateInterval  ivlCashSettle;
    TStubMethod   stub;
    long          dcc;
    /*TBoolean      isPriceClean = FALSE;*/
    double        result = -1.0;

    if (curve == NULL)
    {
        JpmcdsErrMsg("CalcUpfrontCharge: NULL IR zero curve passed\n");
        goto done;
    }


    if (JpmcdsStringToDayCountConv("Act/360", &dcc) != SUCCESS)
        goto done;

    if (JpmcdsStringToDateInterval("Q", routine, &ivl) != SUCCESS)
        goto done;

    if (JpmcdsStringToDateInterval("1D", routine, &ivl2) != SUCCESS)
        goto done;

    if (JpmcdsStringToDateInterval("3D", routine, &ivlCashSettle) != SUCCESS)
	{
		goto done;
	}

    if (JpmcdsStringToStubMethod("f/s", &stub) != SUCCESS)
        goto done;

    if (JpmcdsDateFwdThenAdjust(baseDate, &ivl2, JPMCDS_BAD_DAY_NONE, "None", &stepInDate) != SUCCESS)
	{
		goto done;
	}

	/*if (JpmcdsDateFwdThenAdjust(baseDate, &ivlCashSettle, JPMCDS_BAD_DAY_MODIFIED, "None", &settleDate) != SUCCESS)
	{
		goto done;
	}*/

    if(verbose){
            printf("\n\ntoday = %d\n", (int)baseDate);
            printf("valueDate = %d\n", (int)settleDate);
            printf("benchmarkStartDate = %d\n", (int)effectiveDate);
            printf("stepInDate = %d\n", (int)stepInDate);
            printf("startDate = %d\n", (int)effectiveDate);
            printf("endDate = %d\n", (int)maturityDate);
            printf("coupon_rate = %f\n", coupon_rate);
            printf("isPriceClean = %d\n", isPriceClean);
            printf("recovery_rate = %f\n", recovery_rate);
        }

       /*


	EXPORT int JpmcdsCdsoneUpfrontCharge
	(TDate           today,
	 TDate           valueDate,
	 TDate           benchmarkStartDate,  start date of benchmark CDS for
										  internal clean spread bootstrapping
	 TDate           stepinDate,
	 TDate           startDate,
	 TDate           endDate,
	 double          couponRate,
	 TBoolean        payAccruedOnDefault,
	 TDateInterval  *dateInterval,
	 TStubMethod    *stubType,
	 long            accrueDCC,
	 long            badDayConv,
	 char           *calendar,
	 TCurve         *discCurve,
	 double          oneSpread,
	 double          recoveryRate,
	 TBoolean        payAccruedAtStart,
	 double         *upfrontCharge)
       */

    if (JpmcdsCdsoneUpfrontCharge(baseDate,
                                  settleDate,
                                  effectiveDate,
                                  stepInDate,
                                  effectiveDate,
                                  maturityDate,
                                  coupon_rate ,
                                  payAccOnDefault,
                                  &ivl,
                                  &stub,
                                  dcc,
                                  'F',
                                  holiday_filename,
                                  curve,
                                  par_spread ,
                                  recovery_rate,
                                  isPriceClean,
                                  &result) != SUCCESS) goto done;


    /*TCurve           *flatSpreadCurve = NULL;

    flatSpreadCurve = JpmcdsCleanSpreadCurve (
        baseDate,
        curve,
        effectiveDate,
        stepInDate,
        settleDate,
        1,
        &maturityDate,
        &par_spread,
        NULL,
        recovery_rate,
        payAccOnDefault,
        &ivl,
        dcc,
        &stub,
        'F',
		"None");

    if (flatSpreadCurve == NULL)
        goto done;

    if (JpmcdsCdsPrice(baseDate,
                       settleDate,
                       stepInDate,
                       effectiveDate,
                       maturityDate,
                       coupon_rate,
                       payAccOnDefault,
                       &ivl,
                       &stub,
                       dcc,
                       'F',
			           "None",
                       curve,
                       flatSpreadCurve,
                       recovery_rate,
                       isPriceClean,
                       &result) != SUCCESS) goto done;*/

done:
    return result * notional;
}

EXPORT double calculate_cds_price(
 TDate baseDate,				/* (I) base start date  */
 TDate maturityDate,			/* (I) cds scheduled termination date  */
 TCurve *discountCurve, 		/* (I) interest rate curve */
 TCurve *spreadCurve, 			/* (I) spread rate curve */
 TDate effectiveDate,			/* (I) accrual from start date  */
 double recoveryRate,			/* (I) recover rate in basis points */
 double couponRate,				/* (I) couple rate */
 int isPriceClean,				/* (I) clean = 1, dirty = 0 */
 int verbose					/* (I) used to toggle info output */
)
{
    static char    *routine = "calculate_cds_price";
    int            status = 1;
    int            payAccruedOnDefault = 1;
    char           **lines = NULL;
    TDateInterval  ivl;
    TDateInterval  ivlCashSettle;
    TDateInterval  couponInterval;
    int            i=0;
    long int       paymentDcc=0;
    TDate          stepInDate;
    TDate          settleDate;
    TStubMethod    stubMethod;
    double         price;

    if (JpmcdsErrMsgEnableRecord(20, 128) != SUCCESS) /* ie. 20 lines, each of max length 128 */
        goto done;

	if (JpmcdsStringToDateInterval("1D", routine, &ivl) != SUCCESS)
	{
		goto done;
	}

	if (JpmcdsStringToDateInterval("3D", routine, &ivlCashSettle) != SUCCESS)
	{
		goto done;
	}

	//if (JpmcdsDateFwdThenAdjust(effectiveDate, &ivl, JPMCDS_BAD_DAY_NONE, "None", &startDate) != SUCCESS)
	//{
	//	goto done;
	//}
	//if(verbose){
	//	printf("startDate = %d\n", (int)startDate);
	//}

	if (JpmcdsDateFwdThenAdjust(baseDate, &ivl, JPMCDS_BAD_DAY_NONE, "None", &stepInDate) != SUCCESS)
	{
		goto done;
	}	

	if (JpmcdsDateFwdThenAdjust(baseDate, &ivlCashSettle, JPMCDS_BAD_DAY_MODIFIED, "None", &settleDate) != SUCCESS)
	{
		goto done;
	}

	if(verbose){
	    printf("\n\ntoday = %d\n", (int)baseDate);
	    printf("valueDate = %d\n", (int)settleDate);
		printf("stepInDate = %d\n", (int)stepInDate);
		printf("startDate = %d\n", (int)effectiveDate);
		printf("endDate = %d\n", (int)maturityDate);
		printf("coupon = %f\n", couponRate);
		printf("isPriceClean = %d\n", isPriceClean);
		printf("recoveryRate = %f\n", recoveryRate);
	}
	
    if (JpmcdsStringToDayCountConv("Act/360", &paymentDcc) != SUCCESS)
        goto done;

    if (JpmcdsStringToDateInterval("Q", routine, &couponInterval) != SUCCESS)
        goto done;

    if (JpmcdsStringToStubMethod("F", &stubMethod)  != SUCCESS)
        goto done;

    //printf("calling JpmcdsCdsContingentLegPV...\n");

	/*if (JpmcdsCdsContingentLegPV(baseDate,
                                     settleDate,
                                     stepInDate,
                                     maturityDate,
                                     1.0,
                                     discountCurve,
                                     spreadCurve,
                                     recoveryRate,
                                     1,
                                     &price) != SUCCESS){
                                     goto done;
                                     }*/

	if(verbose){
		printf("calling JpmcdsCdsPrice...\n");
	}

/*
		status = JpmcdsCdsPrice
			(TDate             today,
			 TDate             settleDate,
			 TDate             stepinDate,
			 TDate             startDate,
			 TDate             endDate,
			 double            couponRate,
			 TBoolean          payAccOnDefault,
			 TDateInterval    *dateInterval,
			 TStubMethod      *stubType,
			 long              paymentDcc,
			 long              badDayConv,
			 char             *calendar,
			 TCurve           *discCurve,
			 TCurve           *spreadCurve,
			 double            recoveryRate,
			 TBoolean          isPriceClean,
			 double           *price)
*/
		if (JpmcdsCdsPrice
			(baseDate,
			 settleDate,
			 stepInDate,
			 effectiveDate,
			 maturityDate,
			 couponRate,
			 payAccruedOnDefault,
			 &couponInterval,
			 &stubMethod,
			 paymentDcc,
			 'F',
			 "None",
			 discountCurve,
			 spreadCurve,
			 recoveryRate,
			 isPriceClean,
			 &price) != SUCCESS){

			 goto done;

			 }
			 
	if(verbose){
		printf("calling JpmcdsCdsPrice = %.15f\n", price);
	}

	status = 0;

done:

	if (status != 0){
		printf("\n");
		printf("Error log contains:\n");
		printf("------------------:\n");

		lines = JpmcdsErrGetMsgRecord();
		if (lines == NULL)
			printf("(no log contents)\n");
		else
		{
			for(i = 0; lines[i] != NULL; i++)
			{
				if (strcmp(lines[i],"") != 0)
					printf("%s\n", lines[i]);
			}
		}
    }
	return price;

}

EXPORT TDate* calculate_cds_roll_dates(
 TDate baseDate,		/* (I) integer base start date JpmCdsDate */
 char **rollExpiries,	/* (I) array of char* of tenor strings "1M", "2M", "3M", "6M", "9M", "1Y", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y" */
 int n,
 int verbose
){


  static char  *routine = "calculate_cds_roll_dates";
    TCurve       *zc = NULL;
    //char         *types = "MMMMMMMM";
    TDate        *dates = NULL;
    
    char           **lines = NULL;
    char          badDayConv = 'M';
    char         *holidays = "None";
    int           i;
    int            status = 1;

    //n = strlen(types);

	dates = NEW_ARRAY(TDate, n);
	for (i = 0; i < n; i++)
	{
		TDateInterval tmp;

		if (JpmcdsStringToDateInterval(rollExpiries[i], routine, &tmp) != SUCCESS)
		{
			JpmcdsErrMsg ("%s: invalid interval for element[%d].\n", routine, i);
			goto done;
		}

		if (JpmcdsDateFwdThenAdjust(baseDate, &tmp, JPMCDS_BAD_DAY_PREVIOUS, "None", dates+i) != SUCCESS)
		{
			JpmcdsErrMsg ("%s: invalid interval for element[%d].\n", routine, i);
			goto done;
		}
	}

	status = 0;

done:

	if (status != 0){
		printf("\n");
		printf("Error log contains:\n");
		printf("------------------:\n");

		lines = JpmcdsErrGetMsgRecord();
		if (lines == NULL)
			printf("(no log contents)\n");
		else
		{
			for(i = 0; lines[i] != NULL; i++)
			{
				if (strcmp(lines[i],"") != 0)
					printf("%s\n", lines[i]);
			}
		}
    }
	return dates;

}

EXPORT double* calculate_cds_par_spread(
 TDate baseDate,				/* (I) base start date  */
 TDate maturityDate,			/* (I) cds scheduled termination date  */
 TCurve *discountCurve, 		/* (I) interest rate curve */
 TCurve *spreadCurve, 			/* (I) spread rate curve */
 TDate effectiveDate,			/* (I) accrual from start date  */
 double recoveryRate,			/* (I) recover rate in basis points */
 double couponRate,				/* (I) couple rate */
 int isPriceClean,				/* (I) clean = 1, dirty = 0 */
 int verbose,					/* (I) used to toggle info output */
 char **endDateTenors,	        /* (I) array of char* of tenor strings "1M", "2M", "3M", "6M", "9M", "1Y", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y" */
 int nbEndDates                 /* (I) input count of roll expires */
)
{
    static char    *routine = "calculate_cds_par_spread";
    int            status = 1;
    int            payAccruedOnDefault = 1;
    char           **lines = NULL;
    TDate          *endDates = NULL;
    TDateInterval  ivl;
    TDateInterval  ivlCashSettle;
    TDateInterval  couponInterval;
    int            i=0;
    long int       paymentDcc=0;
    TDate          stepInDate;
    TDate          settleDate;
    TStubMethod    stubMethod;
    double         *parSpread = NULL;

    if (JpmcdsErrMsgEnableRecord(20, 128) != SUCCESS) /* ie. 20 lines, each of max length 128 */
        goto done;

	if (JpmcdsStringToDateInterval("1D", routine, &ivl) != SUCCESS)
	{
		goto done;
	}

	if (JpmcdsStringToDateInterval("3D", routine, &ivlCashSettle) != SUCCESS)
	{
		goto done;
	}

	if (JpmcdsDateFwdThenAdjust(baseDate, &ivl, JPMCDS_BAD_DAY_NONE, "None", &stepInDate) != SUCCESS)
	{
		goto done;
	}	

	if (JpmcdsDateFwdThenAdjust(baseDate, &ivlCashSettle, JPMCDS_BAD_DAY_MODIFIED, "None", &settleDate) != SUCCESS)
	{
		goto done;
	}

	if(verbose){
	    printf("\n\ntoday = %d\n", (int)baseDate);
	    printf("valueDate = %d\n", (int)settleDate);
		printf("stepInDate = %d\n", (int)stepInDate);
		printf("startDate = %d\n", (int)effectiveDate);
		printf("endDate = %d\n", (int)maturityDate);
		printf("coupon = %f\n", couponRate);
		printf("isPriceClean = %d\n", isPriceClean);
		printf("recoveryRate = %f\n", recoveryRate);
		printf("nbEndDates = %d\n", nbEndDates);
	}
	
    if (JpmcdsStringToDayCountConv("Act/360", &paymentDcc) != SUCCESS)
        goto done;

    if (JpmcdsStringToDateInterval("Q", routine, &couponInterval) != SUCCESS)
        goto done;

    if (JpmcdsStringToStubMethod("F", &stubMethod)  != SUCCESS)
        goto done;

	if(verbose){
		printf("calling JpmcdsCdsPrice...\n");
	}
	
	endDates = NEW_ARRAY(TDate, nbEndDates);
	for (i = 0; i < nbEndDates; i++)
	{
		TDateInterval tmp;

		if (JpmcdsStringToDateInterval(endDateTenors[i], routine, &tmp) != SUCCESS)
		{
			JpmcdsErrMsg ("%s: invalid interval for element[%d].\n", routine, i);
			goto done;
		}

		if (JpmcdsDateFwdThenAdjust(baseDate, &tmp, JPMCDS_BAD_DAY_MODIFIED, "None", endDates+i) != SUCCESS)
		{
			JpmcdsErrMsg ("%s: invalid interval for element[%d].\n", routine, i);
			goto done;
		}
	}
	
	parSpread = NEW_ARRAY(double, nbEndDates);

/*
	EXPORT JpmcdsCdsPrice
			(TDate             today,
			 TDate             settleDate,
			 TDate             stepinDate,
			 TDate             startDate,
			 TDate             endDate,
			 double            couponRate,
			 TBoolean          payAccOnDefault,
			 TDateInterval    *dateInterval,
			 TStubMethod      *stubType,
			 long              paymentDcc,
			 long              badDayConv,
			 char             *calendar,
			 TCurve           *discCurve,
			 TCurve           *spreadCurve,
			 double            recoveryRate,
			 TBoolean          isPriceClean,
			 double           *price)
			 
	EXPORT int JpmcdsCdsParSpreads(
        TDate           today,
        TDate           stepinDate,
        TDate           startDate,
        long            nbEndDates,
        TDate          *endDates,
        TBoolean        payAccOnDefault,
        TDateInterval  *couponInterval,
        TStubMethod    *stubType,
        long            paymentDcc,
        long            badDayConv,
        char           *calendar,
        TCurve         *discCurve,
        TCurve         *spreadCurve,
        double          recoveryRate,
        double         *parSpread)
*/
		if (JpmcdsCdsParSpreads
			(baseDate,
			 stepInDate,
			 effectiveDate,
			 nbEndDates,
			 endDates,
			 payAccruedOnDefault,
			 &couponInterval,
			 &stubMethod,
			 paymentDcc,
			 'F',
			 "None",
			 discountCurve,
			 spreadCurve,
			 recoveryRate,
			 parSpread) != SUCCESS){

			 goto done;

			 }
			 
	if(verbose){
	    for (i = 0; i < nbEndDates; i++)
	    {
		    printf("calling JpmcdsCdsParSpreads = %.15f\n", parSpread[i]);
		}
	}

	status = 0;

done:

	if (status != 0){
		printf("\n");
		printf("Error log contains:\n");
		printf("------------------:\n");

		lines = JpmcdsErrGetMsgRecord();
		if (lines == NULL)
			printf("(no log contents)\n");
		else
		{
			for(i = 0; lines[i] != NULL; i++)
			{
				if (strcmp(lines[i],"") != 0)
					printf("%s\n", lines[i]);
			}
		}
    }
	return parSpread;

}

