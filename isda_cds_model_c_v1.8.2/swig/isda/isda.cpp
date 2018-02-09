#include <vector>
#include <iostream>
#include <sstream>
#include "isda.h"
#include "example.h"
#include "busday.h"
#include "dateconv.h"
#include "date_sup.h"
#include <ctime>
#include <stdio.h>
#include "main.h"
#include "tcurve.h"
#include "bastypes.h"
#include <math.h>
#include "macros.h"

using namespace std;

TDate parse_string_ddmmyyyy(const std::string& s, int& day, int& month, int& year)
{
  sscanf(s.c_str(), "%2d/%2d/%4d", &day, &month, &year);
  return JpmcdsDate(year, month, day);
}

TDate parse_string_ddmmyyyy_to_jpmcdsdate(const std::string& s)
{
  int day, month, year;
  sscanf(s.c_str(), "%2d/%2d/%4d", &day, &month, &year);
  return JpmcdsDate(year, month, day);
}

/*
***************************************************************************
** compute all in one for a what if cds position.
***************************************************************************
*/

vector< vector<double> > cds_all_in_one (
 string trade_date,					/* (I) trade date of cds as DD/MM/YYYY */
 string effective_date,				/* (I) effective date of cds as DD/MM/YYYY */
 string maturity_date,				/* (I) maturity date of cds as DD/MM/YYYY */
 string value_date,					/* (I) date to value the cds DD/MM/YYYY */
 string accrual_start_date,			/* (I) maturity date of cds as DD/MM/YYYY */
 double	recovery_rate,				/* (I) recover rate of the curve in basis points */
 double coupon_rate,				/* (I) CouponRate (e.g. 0.05 = 5% = 500bp) */
 double notional,					/* (I) Notional MM */
 int is_buy_protection,				/* (I) direction of credit risk */
 vector<double> swap_rates, 		/* (I) swap rates */
 vector<string> swap_tenors,		/* (I) swap tenors "1M", "2M" */
 vector<double> spread_rates,		/* (I) spread spreads */
 vector<string> spread_tenors,		/* (I) spread tenors "6M", "1Y" */
 vector<string> spread_roll_tenors, /* (I) spread roll tenors */
 vector<string> imm_dates,			/* (I) imm dates */
 vector<double> scenario_tenors,	/* (I) spread tenors -100, -90, -80, -70 ... */
 int verbose						/* (I) output message text */
)
{

  int start_s = clock();

  // used in risk calculations
  double single_basis_point = 0.0001;

  TDate trade_date_jpm, effective_date_jpm, maturity_date_jpm,
  accrual_start_date_jpm, value_date_jpm;

  // empty curve pointers
  TCurve *zerocurve = NULL;
  TCurve *zerocurve_dv01 = NULL;
  TCurve *spreadcurve = NULL;
  TCurve *spreadcurve_cs01 = NULL;
  TCurve *spreadcurve_dv01 = NULL;

  // discount
  double rates[swap_rates.size()];
  double rates_dv01[swap_rates.size()];
  char *expiries[swap_rates.size()];

  // credit spread
  double spreads[spread_rates.size()];
  double spreads_cs01[spread_rates.size()];
  double *pointer_spreads;
  double *pointer_spreads_cs01;
  long int tenors[imm_dates.size()];
  long int *pointer_tenors;

  char *spread_roll_expiries[spread_roll_tenors.size()];

  // numeric values
  double coupon_rate_in_basis_points = coupon_rate/10000.0;
  double upfrontcharge;
  double dirtypv;
  double dirtypv_cs01;
  double dirtypv_dv01;

  // outer return vector
  vector < vector<double> > allinone;

  // inner return vector
  vector <double> allinone_base;
  vector <double> allinone_pvbp;
  vector < vector<double> > allinone_roll;

  // assumes sell protection default
  double credit_risk_direction_scale_factor = -1;

  // jpm roll dates
  TDate *pointer_roll_dates_jpm;
  double roll_pvdirty;

  /* TODO: check swap_rates.size() == imm_dates.size() with assert */
  /* TODO: check swap_rates.size() == imm_dates.size() with assert */

  /////////////////////////////
  // parse char* to jpm dates
  /////////////////////////////

  trade_date_jpm = parse_string_ddmmyyyy_to_jpmcdsdate(trade_date);
  effective_date_jpm = parse_string_ddmmyyyy_to_jpmcdsdate(effective_date);
  maturity_date_jpm = parse_string_ddmmyyyy_to_jpmcdsdate(maturity_date);
  accrual_start_date_jpm = parse_string_ddmmyyyy_to_jpmcdsdate(accrual_start_date);
  value_date_jpm = parse_string_ddmmyyyy_to_jpmcdsdate(value_date);

  if (verbose == 1){
	  std::cout << "value_date_jpm " << value_date_jpm << std::endl;
	  std::cout << "trade_date_jpm " << trade_date_jpm << std::endl;
	  std::cout << "effective_date_jpm " << effective_date_jpm << std::endl;
	  std::cout << "accrual_start_date_jpm " << accrual_start_date_jpm << std::endl;
	  std::cout << "maturity_date_jpm " << maturity_date_jpm << std::endl;
  }

  /////////////////////////////
  // bootstrap interest rate curve
  /////////////////////////////

  for(int r = 0; r < swap_rates.size(); r++){
    rates[r] = swap_rates[r];
    rates_dv01[r] = swap_rates[r] + single_basis_point;
  }

  for(int r = 0; r < swap_tenors.size(); r++){
    expiries[r] = (char *)swap_tenors[r].c_str();
  }

  // bootstrap discount curve
  zerocurve = build_zero_interest_rate_curve(value_date_jpm
		  , rates
		  , expiries
		  , verbose);

  zerocurve_dv01 = build_zero_interest_rate_curve(value_date_jpm
		  , rates_dv01
		  , expiries
		  , verbose);

  /////////////////////////////
  // bootstrap spread curve
  /////////////////////////////

  // parse imm dates into jpm string format
  for(int r = 0; r < imm_dates.size(); r++){
    tenors[r] = parse_string_ddmmyyyy_to_jpmcdsdate(imm_dates[r]);
    if (verbose){
    	std::cout << r << " imm tenor " << tenors[r] << std::endl;
    }
  }

  // need a pointer to array of long int
  pointer_tenors = tenors;

  for(int r = 0; r < spread_rates.size(); r++){
    spreads[r] = spread_rates[r];
    spreads_cs01[r] = spread_rates[r] + single_basis_point;
    if (verbose){
      std::cout << r << " " << spreads_cs01[r] << std::endl;
    }
  }

  // similarly need a double *
  pointer_spreads = spreads;
  pointer_spreads_cs01 = spreads_cs01;

  if (verbose){
    std::cout << "imm_dates.size() " << imm_dates.size() << std::endl;
  }

  // build spread curve
  spreadcurve = build_credit_spread_par_curve(
  			value_date_jpm
  			, zerocurve
  			, accrual_start_date_jpm
  			, pointer_spreads
  			, pointer_tenors
  			, coupon_rate_in_basis_points
  			, imm_dates.size()
  			, verbose);

  if (spreadcurve == NULL){
  	std::cout << spreadcurve << std::endl;
  	std::cout << "bad spreadcurve" << std::endl;
  }

  if (spreadcurve != NULL){
    if (verbose){
  	  std::cout << spreadcurve << std::endl;
  	  std::cout << "spreadcurve OK!" << std::endl;
  	}
  }

  // cs01_spread_curve

  // build spread curve
  spreadcurve_cs01 = build_credit_spread_par_curve(
  			value_date_jpm
  			, zerocurve
  			, accrual_start_date_jpm
  			, pointer_spreads_cs01
  			, pointer_tenors
  			, coupon_rate_in_basis_points
  			, imm_dates.size()
  			, verbose);

  if (spreadcurve_cs01 == NULL){
  	std::cout << spreadcurve_cs01 << std::endl;
  	std::cout << "bad spreadcurve_cs01" << std::endl;
  }

  if (spreadcurve_cs01 != NULL){
    if (verbose){
  	  std::cout << spreadcurve_cs01 << std::endl;
  	  std::cout << "spreadcurve_cs01 OK!" << std::endl;
  	}
  }

  // dv01 spread_curve

  spreadcurve_dv01 = build_credit_spread_par_curve(
  			value_date_jpm
  			, zerocurve_dv01
  			, trade_date_jpm
  			, pointer_spreads
  			, pointer_tenors
  			, coupon_rate_in_basis_points
  			, imm_dates.size()
  			, verbose);

  if (spreadcurve_dv01 == NULL){
  	std::cout << spreadcurve_dv01 << std::endl;
  	std::cout << "bad spreadcurve_dv01" << std::endl;
  }

  if (spreadcurve_dv01 != NULL){
    if (verbose){
  	  std::cout << spreadcurve_dv01 << std::endl;
  	  std::cout << "spreadcurve_dv01 OK!" << std::endl;
  	}
  }

  // calculate upfront on cds
  //TODO: correctly pass trade details here!
  //upfrontcharge = calculate_upfront_charge(zerocurve, coupon_rate, verbose);

  // calculate price cds
  dirtypv = calculate_cds_price(value_date_jpm
  , maturity_date_jpm
  , zerocurve
  , spreadcurve
  , accrual_start_date_jpm
  , recovery_rate
  , coupon_rate_in_basis_points
  , verbose);

  dirtypv_cs01 = calculate_cds_price(value_date_jpm
  , maturity_date_jpm
  , zerocurve
  , spreadcurve_cs01
  , accrual_start_date_jpm
  , recovery_rate
  , coupon_rate_in_basis_points
  , verbose);

  dirtypv_dv01 = calculate_cds_price(value_date_jpm
  , maturity_date_jpm
  , zerocurve_dv01
  , spreadcurve_dv01
  , accrual_start_date_jpm
  , recovery_rate
  , coupon_rate_in_basis_points
  , verbose);

  if (is_buy_protection){
  	credit_risk_direction_scale_factor = 1;
  }

  // manage sign separately based on trade direction
  dirtypv = fabs(dirtypv);
  dirtypv_cs01 = fabs(dirtypv_cs01);
  dirtypv_dv01 = fabs(dirtypv_dv01);

  if (verbose){
    std::cout << "credit_risk_direction_scale_factor " << credit_risk_direction_scale_factor << std::endl;
    std::cout << "dirtypv * notional " << dirtypv * notional  << std::endl;
    std::cout << "dirtypv " << dirtypv << std::endl;
    std::cout << "pvdirty (scaled) " << dirtypv * notional * credit_risk_direction_scale_factor << std::endl;
  }

  if (verbose){
    std::cout << "cs01 " << dirtypv_cs01 - dirtypv << std::endl;
  }

  // push back result
  allinone_base.push_back(dirtypv * notional * credit_risk_direction_scale_factor);
  allinone_base.push_back((dirtypv_cs01 - dirtypv) * notional);
  allinone_base.push_back((dirtypv_dv01 - dirtypv) * notional);

  //allinone.push_back(upfrontcharge);

  // compute PVBP

  for(int r = 0; r < imm_dates.size(); r++){
     allinone_pvbp.push_back(
		 calculate_cds_price(value_date_jpm
		  , tenors[r]
		  , zerocurve
		  , spreadcurve
		  , value_date_jpm
		  , recovery_rate
		  , 0.01
		  , verbose)
		  -
		  calculate_cds_price(value_date_jpm
		  , tenors[r]
		  , zerocurve
		  , spreadcurve
		  , value_date_jpm
		  , recovery_rate
		  , 0.01 + single_basis_point
		  , verbose)
	  );
  }

  // roll down pv
  // move this into a C library function?

  for(int r = 0; r < spread_roll_tenors.size(); r++){
    spread_roll_expiries[r] = (char *)spread_roll_tenors[r].c_str();
  }

  pointer_roll_dates_jpm =  calculate_cds_roll_dates(value_date_jpm,
  spread_roll_expiries,
  spread_roll_tenors.size(),
  verbose);

  for(int s=0; s < scenario_tenors.size(); s++){  
  	  
	  vector <double> scenario_tenors_pvdirty;
	  
	  // build a scenario spread curve	  
	  for(int r = 0; r < spread_rates.size(); r++){		
	    // spread_cs01 = spead + spread * -0.1
		spreads_cs01[r] = spread_rates[r] + spread_rates[r]  * scenario_tenors[s]/100;		
	  }

	  // similarly need a double *	  
	  pointer_spreads_cs01 = spreads_cs01;
	  
	  // build spread curve
	  spreadcurve = build_credit_spread_par_curve(
				value_date_jpm
				, zerocurve
				, accrual_start_date_jpm
				, pointer_spreads_cs01
				, pointer_tenors
				, coupon_rate_in_basis_points
				, imm_dates.size()
				, verbose);	 
  
	  for(int r = 0; r < spread_roll_tenors.size(); r++){

		roll_pvdirty = calculate_cds_price(pointer_roll_dates_jpm[r]
		  , maturity_date_jpm
		  , zerocurve
		  , spreadcurve
		  , accrual_start_date_jpm
		  , recovery_rate
		  , coupon_rate_in_basis_points
		  , verbose);

		roll_pvdirty = fabs(roll_pvdirty);
		scenario_tenors_pvdirty.push_back((roll_pvdirty - dirtypv) * notional);

	  }
	  
	  // push back entire matrix
	  allinone_roll.push_back(scenario_tenors_pvdirty);
  }

  int stop_s = clock();
  allinone_base.push_back((stop_s-start_s));

  // push back all vectors
  allinone.push_back(allinone_base);
  allinone.push_back(allinone_pvbp);
  
  for(int r = 0; r < allinone_roll.size(); r++){		
	allinone.push_back(allinone_roll[r]);
  }

  // handle free of the curve objects via call to JpmcdsFreeSafe macro
  FREE(spreadcurve);
  FREE(spreadcurve_dv01);
  FREE(spreadcurve_cs01);
  FREE(zerocurve);
  FREE(zerocurve_dv01);
  FREE(pointer_roll_dates_jpm);

  return allinone;
}

vector<double> average (vector< vector<double> > i_matrix) {

  // compute average of each row..
  vector <double> averages; 
  for (int r = 0; r < i_matrix.size(); r++){
    double rsum = 0.0;
    double ncols= i_matrix[r].size();
    for (int c = 0; c< i_matrix[r].size(); c++){
      rsum += i_matrix[r][c];
    }
    averages.push_back(rsum/ncols);    
  }
  std::cout << "factoral " << factoral(5) << std::endl;
  return averages;
};


int n=0;
Callback * callback = NULL;

void Callback::run(int n){
    std::cout << "This print from C++: n = " << n << std::endl;
}

void setCallback(Callback * cb){
    callback = cb;
}

void doSomeWithCallback(){
    if(callback == NULL){
        std::cout << "Must set callback first!" << std::endl;
    }else{
        callback->run(n++);
    }
}
