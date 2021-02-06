#ifndef _code
#define _code

#ifdef MATHLIBRARY_EXPORTS  
#define MATHLIBRARY_API __declspec(dllexport)   
#else  
#define MATHLIBRARY_API __declspec(dllimport)   
#endif  

#include <vector>

std::vector<double> average (std::vector< std::vector<double> > i_matrix);

std::vector< double > cds_discount_rate_ir_tenor_dates(
	std::string value_date,						/* (I) date to value the cds DD/MM/YYYY */
	std::vector<std::string> value_dates,		/* (I) date to value the cds DD/MM/YYYY */
	std::vector<double> swap_rates, 			/* (I) swap rates */
	std::vector<std::string> swap_tenors,		/* (I) swap tenors "1M", "2M" */
	int verbose
);

std::vector< std::vector<double> > cds_coupon_schedule(
    std::string accrual_start_date, /* (I) maturity date of cds as DD/MM/YYYY */
    std::string maturity_date, /* (I) maturity date of cds as DD/MM/YYYY */
    std::string coupon_interval, /* (I) coupon interval Q, 1M, 2M */
    std::string day_count_convention, /* (I) day_count_convention Act/360 */
    std::string stub_method, /* (I) stub_method F/S/20 */
    std::string holiday_filename, /* (I) YYMMDD holiday.dat filename */
    double coupon_rate, /* (I) maturity date of cds as DD/MM/YYYY */
    double notional, /* (I) maturity date of cds as DD/MM/YYYY */
    int verbose
);

std::vector< std::vector<double> > cds_index_all_in_one (
 std::string trade_date,						    /* (I) trade date of cds as DD/MM/YYYY */
 std::string effective_date,					    /* (I) effective date of cds as DD/MM/YYYY */
 std::string maturity_date,						    /* (I) maturity date of cds as DD/MM/YYYY */
 std::string value_date,						    /* (I) date to value the cds DD/MM/YYYY */
 std::string accrual_start_date,				    /* (I) maturity date of cds as DD/MM/YYYY */
 std::vector<double> recovery_rate,					    /* (I) recover rate of the curve in basis points */
 double coupon_rate,							    /* (I) CouponRate (e.g. 0.05 = 5% = 500bp) */
 double notional,								    /* (I) Notional MM */
 int is_buy_protection,							    /* (I) direction of credit risk */
 std::vector<double> swap_rates, 				    /* (I) swap rates */
 std::vector<std::string> swap_tenors,			    /* (I) swap tenors "1M", "2M" */
 std::vector<std::string> swap_maturities,		    /* (I) swap maturity dates */
 std::vector< std::vector<double> > spread_rates,	/* (I) spread spreads */
 std::vector<std::string> spread_tenors,		    /* (I) spread tenors "6M", "1Y" */
 std::vector<std::string> spread_roll_tenors, 	    /* (I) spread roll tenors */
 std::vector<std::string> imm_dates,			    /* (I) imm dates */
 std::vector<double> scenario_tenors,			    /* (I) spread tenors -100, -90, -80, -70 ... */
 int verbose
);

std::vector< std::vector<double> > cds_all_in_one (
 std::string trade_date,						/* (I) trade date of cds as DD/MM/YYYY */
 std::string effective_date,					/* (I) effective date of cds as DD/MM/YYYY */
 std::string maturity_date,						/* (I) maturity date of cds as DD/MM/YYYY */
 std::string value_date,						/* (I) date to value the cds DD/MM/YYYY */
 std::string accrual_start_date,				/* (I) maturity date of cds as DD/MM/YYYY */
 double	recovery_rate,							/* (I) recover rate of the curve in basis points */
 double coupon_rate,							/* (I) CouponRate (e.g. 0.05 = 5% = 500bp) */
 double notional,								/* (I) Notional MM */
 int is_buy_protection,							/* (I) direction of credit risk */
 std::vector<double> swap_rates, 				/* (I) swap rates */
 std::vector<std::string> swap_tenors,			/* (I) swap tenors "1M", "2M" */
 std::vector<std::string> swap_maturities,		/* (I) swap maturity dates */
 std::vector<double> spread_rates,				/* (I) spread spreads */
 std::vector<std::string> spread_tenors,		/* (I) spread tenors "6M", "1Y" */
 std::vector<std::string> spread_roll_tenors, 	/* (I) spread roll tenors */
 std::vector<std::string> imm_dates,			/* (I) imm dates */
 std::vector<double> scenario_tenors,			/* (I) spread tenors -100, -90, -80, -70 ... */
 int verbose
);


std::vector< std::vector<double> > cds_all_in_one_exclude_ir_tenor_dates (
 std::string trade_date,						/* (I) trade date of cds as DD/MM/YYYY */
 std::string effective_date,					/* (I) effective date of cds as DD/MM/YYYY */
 std::string maturity_date,						/* (I) maturity date of cds as DD/MM/YYYY */
 std::string value_date,						/* (I) date to value the cds DD/MM/YYYY */
 std::string accrual_start_date,				/* (I) maturity date of cds as DD/MM/YYYY */
 double	recovery_rate,							/* (I) recover rate of the curve in basis points */
 double coupon_rate,							/*(I) CouponRate (e.g. 0.05 = 5% = 500bp) */
 double notional,								/* (I) Notional MM */
 int is_buy_protection,							/* (I) direction of credit risk */
 std::vector<double> swap_rates, 				/* (I) swap rates */
 std::vector<std::string> swap_tenors,			/* (I) swap tenors "1M", "2M" */
 std::vector<double> spread_rates,				/* (I) spread spreads */
 std::vector<std::string> spread_tenors,		/* (I) spread tenors "6M", "1Y" */
 std::vector<std::string> spread_roll_tenors, 	/* (I) spread roll tenors */
 std::vector<std::string> imm_dates,			/* (I) imm dates */
 std::vector<double> scenario_tenors,			/* (I) spread tenors -100, -90, -80, -70 ... */ 
 int verbose
);

#endif

class Callback{
    public:
    virtual void run(int n);
    virtual ~Callback() {};
};
extern Callback *callback;
extern void doSomeWithCallback();
extern void setCallback(Callback * cb);
