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
    long           mmDCC;
    TDate          startDate;
    TDate          stepInDate;
    TDate          cashSettleDate;
    TStubMethod    stubMethod;
    //int includes[8] = {1,1,1,1,1,1,1,1};
    int            status = 1;

    if(verbose){
      printf("BaseDate = %d\n", (int)baseDate);
    }

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

	if (JpmcdsDateFwdThenAdjust(tradeDate, &ivl, JPMCDS_BAD_DAY_MODIFIED, "None", &startDate) != SUCCESS)
	{
		goto done;
	}
	if(verbose){
	  printf("startDate = %d\n", (int)startDate);
	}

	if (JpmcdsDateFwdThenAdjust(baseDate, &ivl, JPMCDS_BAD_DAY_MODIFIED, "None", &stepInDate) != SUCCESS)
	{
		goto done;
	}
	if(verbose){
		printf("StepInDate = %d\n", (int)stepInDate);
	}

	if (JpmcdsDateFwdThenAdjust(baseDate, &ivlCashSettle, JPMCDS_BAD_DAY_MODIFIED, "NONE", &cashSettleDate) != SUCCESS)
	{
		goto done;
	}
	if(verbose){
		printf("SettleDate = %d\n", (int)cashSettleDate);
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

	sc = JpmcdsCleanSpreadCurve
		(baseDate,
		 discountCurve,
		 tradeDate,
		 stepInDate,
		 cashSettleDate,
		 n,
		 dates,
		 rates,
		 NULL,
		 recoveryRate,
		 payAccruedOnDefault,
		 &couponInterval,
		 mmDCC,
		 &stubMethod,
		 'F',
		 "None"
		);

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
EXPORT TCurve* build_zero_interest_rate_curve(
 TDate baseDate,			/* (I) integer base start date JpmCdsDate */
 double *rates,			/* (I) double array with 14 elements */
 char **expiries,		/* (I) array of char* of tenor strings "1M", "2M", "3M", "6M", "9M", "1Y", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y" */
 int verbose
)
{
    static char  *routine = "BuildExampleZeroCurve";
    TCurve       *zc = NULL;
    char         *types = "MMMMMSSSSSSSSS";
    //char         expiries[14] = {"1M", "2M", "3M", "6M", "9M", "1Y", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y"};
    TDate        *dates = NULL;
    //double        rates[14] = {1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9};
    //TDate         baseDate;
    long          mmDCC;
    TDateInterval ivl;
    long          dcc;
    double        freq;
    char          badDayConv = 'M';
    char         *holidays = "None";
    int           i, n;

	if(verbose){
    	printf("BaseDate = %d\n", (int)baseDate);
    }

    if (JpmcdsStringToDayCountConv("Act/360", &mmDCC) != SUCCESS)
        goto done;

    if (JpmcdsStringToDayCountConv("30/360", &dcc) != SUCCESS)
        goto done;

    if (JpmcdsStringToDateInterval("6M", routine, &ivl) != SUCCESS)
        goto done;

    if (JpmcdsDateIntervalToFreq(&ivl, &freq) != SUCCESS)
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

        if (JpmcdsDateFwdThenAdjust(baseDate, &tmp, JPMCDS_BAD_DAY_NONE, "None", dates+i) != SUCCESS)
        {
            JpmcdsErrMsg ("%s: invalid interval for element[%d].\n", routine, i);
            goto done;
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
            baseDate,
            types,
            dates,
            rates,
            n,
            mmDCC,
            (long) freq,
            (long) freq,
            dcc,
            dcc,
            badDayConv,
            holidays);
done:
    FREE(dates);
    return zc;
}

/*
***************************************************************************
** Calculate upfront charge.
***************************************************************************
*/
EXPORT double calculate_upfront_charge
(TCurve* curve, 		/* (I) interest rate curve */
double couponRate, 		/* (I) fixed coupon payable */
int verbose				/* (I) used to toggle echo info output */
)
{
    static char  *routine = "CalcUpfrontCharge";
    TDate         today;
    TDate         valueDate;
    TDate         startDate;
    TDate         benchmarkStart;
    TDate         stepinDate;
    TDate         endDate;
    TBoolean      payAccOnDefault = TRUE;
    TDateInterval ivl;
    TStubMethod   stub;
    long          dcc;
    double        parSpread = 3600;
    double        recoveryRate = 0.4;
    TBoolean      isPriceClean = FALSE;
    double        notional = 1e7;
    double        result = -1.0;

    if (curve == NULL)
    {
        JpmcdsErrMsg("CalcUpfrontCharge: NULL IR zero curve passed\n");
        goto done;
    }

    today          = JpmcdsDate(2008, 2, 1);
    valueDate      = JpmcdsDate(2008, 2, 1);
    benchmarkStart = JpmcdsDate(2008, 2, 2);
    startDate      = JpmcdsDate(2008, 2, 8);
    endDate        = JpmcdsDate(2008, 2, 12);
    stepinDate     = JpmcdsDate(2008, 2, 9);

    if (JpmcdsStringToDayCountConv("Act/360", &dcc) != SUCCESS)
        goto done;

    if (JpmcdsStringToDateInterval("1S", routine, &ivl) != SUCCESS)
        goto done;

    if (JpmcdsStringToStubMethod("f/s", &stub) != SUCCESS)
        goto done;

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

    if (JpmcdsCdsoneUpfrontCharge(today,
                                  valueDate,
                                  benchmarkStart,
                                  stepinDate,
                                  startDate,
                                  endDate,
                                  couponRate / 10000.0,
                                  payAccOnDefault,
                                  &ivl,
                                  &stub,
                                  dcc,
                                  'F',
                                  "None",
                                  curve,
                                  parSpread / 10000.0,
                                  recoveryRate,
                                  isPriceClean,
                                  &result) != SUCCESS) goto done;
done:
    return result * notional;
}

int compute_isda_upfront(
double coupon, 		/* (I) upfront fixed coupon */
int verbose			/* (I) flag to indicate if we should echo output to stdout */
)
{
    int     status = 1;
    char    version[256];
    char  **lines = NULL;
    int     i;
    TCurve *zerocurve = NULL;
    int baseDate;

    if (JpmcdsVersionString(version) != SUCCESS)
        goto done;

    /* print library version */
    printf("starting...\n");
    printf("%s\n", version);

    /* enable logging */
    printf("enabling logging...\n");
    if (JpmcdsErrMsgEnableRecord(20, 128) != SUCCESS) /* ie. 20 lines, each of max length 128 */
        goto done;

    /* construct IR zero curve */
    printf("building zero curve...\n");

    char         *expiries[14] = {"1M", "2M", "3M", "6M", "9M", "1Y", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y"};
    double        rates[14] = {1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9};

	baseDate = JpmcdsDate(2008, 1, 3);
    zerocurve = build_zero_interest_rate_curve(baseDate, rates, expiries, verbose);
    if (zerocurve == NULL)
        goto done;

    /* get discount factor */
    printf("\n");
    printf("Discount factor on 3rd Jan 08 = %f\n", JpmcdsZeroPrice(zerocurve, JpmcdsDate(2008,1,3)));
    printf("Discount factor on 3rd Jan 09 = %f\n", JpmcdsZeroPrice(zerocurve, JpmcdsDate(2009,1,3)));
    printf("Discount factor on 3rd Jan 17 = %f\n", JpmcdsZeroPrice(zerocurve, JpmcdsDate(2017,1,3)));

    /* get upfront charge */
    printf("\n");
    printf("Upfront charge @ cpn = %fbps   =  %f\n", coupon, calculate_upfront_charge(zerocurve, coupon, verbose));

    /* return 'no error' */
    status = 0;

done:
    if (status != 0)
        printf("\n*** ERROR ***\n");

    /* print error log contents */
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

    FREE(zerocurve);
    return status;
}

EXPORT double calculate_cds_price(
 TDate baseDate,				/* (I) base start date  */
 TDate maturityDate,			/* (I) cds scheduled termination date  */
 TCurve *discountCurve, 		/* (I) interest rate curve */
 TCurve *spreadCurve, 			/* (I) spread rate curve */
 TDate 	tradeDate,				/* (I) trade start date  */
 double recoveryRate,			/* (I) recover rate in basis points */
 double couponRate,				/* (I) couple rate */
 int isDirty,					/* (I) clean = 1, dirty = 0 */
 int verbose					/* (I) used to toggle info output */
)
{
    static char    *routine = "calculate_cds_price";
    int            status = 1;
    int            payAccruedOnDefault = 0;
    char           **lines = NULL;
    TDateInterval  ivl;
    TDateInterval  ivlCashSettle;
    TDateInterval  couponInterval;
    int            i=0;
    long           paymentDcc;
    TDate          startDate;
    TDate          stepInDate;
    TDate          settleDate;
    TStubMethod    stubMethod;
    double         price;

	if(verbose){
    	printf("BaseDate = %d\n", (int)baseDate);
    }

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

	if (JpmcdsDateFwdThenAdjust(tradeDate, &ivl, JPMCDS_BAD_DAY_MODIFIED, "None", &startDate) != SUCCESS)
	{
		goto done;
	}
	if(verbose){
		printf("startDate = %d\n", (int)startDate);
	}

	if (JpmcdsDateFwdThenAdjust(baseDate, &ivl, JPMCDS_BAD_DAY_MODIFIED, "None", &stepInDate) != SUCCESS)
	{
		goto done;
	}
	if(verbose){
		printf("StepInDate = %d\n", (int)stepInDate);
	}

	if (JpmcdsDateFwdThenAdjust(baseDate, &ivlCashSettle, JPMCDS_BAD_DAY_MODIFIED, "NONE", &settleDate) != SUCCESS)
	{
		goto done;
	}
	if(verbose){
		printf("SettleDate = %d\n", (int)settleDate);
	}

	if (verbose){
		printf("MaturityDate = %d\n", (int)maturityDate);
	}

    if (JpmcdsStringToDayCountConv("Act/360", &paymentDcc) != SUCCESS)
        goto done;

    if (JpmcdsStringToDateInterval("Q", routine, &couponInterval) != SUCCESS)
        goto done;

    if (JpmcdsStringToStubMethod("F/S", &stubMethod)  != SUCCESS)
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
			 tradeDate,
			 maturityDate,
			 couponRate,
			 payAccruedOnDefault,
			 &ivl,
			 &stubMethod,
			 paymentDcc,
			 'F',
			 "None",
			 discountCurve,
			 spreadCurve,
			 recoveryRate,
			 isDirty,
			 &price) != SUCCESS){

			 goto done;

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
    long          mmDCC;
    char           **lines = NULL;
    TDateInterval ivl;
    long          dcc;
    double        freq;
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

		if (JpmcdsDateFwdThenAdjust(baseDate, &tmp, JPMCDS_BAD_DAY_MODIFIED, "None", dates+i) != SUCCESS)
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
