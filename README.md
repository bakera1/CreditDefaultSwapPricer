# Credit Default Swap Pricer
Simple Credit Default Swap Pricer project brings together the ISDA CDS pricer and some critical modules that are needed to make best use of the underlying C library functions.

## Why create another library ##

The idea behind this library is ease of use, the underlying ISDA C functions whilst usable are pretty difficult to integrate and often folks revert to other 3rd party or open source 
CDS pricing libraries. Whilst this is fine for most uses; when you need precision pricing quickly and easily that conforms exactly to the ISDA CDS model then this wrapper allows you to very quickly
build and start writing code Python and to price and compute risk on CDS positions.

### CDS All In One ###

A simple function cds_all_in_one can provide a swig wrapped C++ function that invokes the underlying C library functions from the ISDA model. The interface has been constructed to make the usage as simple and easy as possible. 


```python

from isda import cds_all_in_one
from imm import imm_date_vector

# EUR interest rate curve
swap_rates = [-0.00369, -0.00341, -0.00328, -0.00274, -0.00223, -0.00186, -0.00128, 0.00046, 0.00217, 0.003, 0.00504, 
        0.00626, 0.00739, 0.00844, 0.00941, 0.01105, 0.01281, 0.01436, 0.01506]

swap_tenors = ['1M', '2M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y',
               '10Y', '15Y', '20Y', '30Y']

# spread curve
credit_spreads = [0.00141154155739384] * 8
credit_spread_tenors = ['6M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']

# value asofdate
sdate = datetime.datetime(2018, 1, 23)
value_date = sdate.strftime('%d/%m/%Y')

# economics of trade
recovery_rate = 0.4
coupon = 100
trade_date = '14/12/2017'
effective_date = '20/09/2017'
maturity_date = '20/12/2019'
accrual_start_date = '20/09/2017'
notional = 1.0 # 1MM EUR
is_buy_protection = 0

tenor_list = [0.5, 1, 2, 3, 4, 5, 7, 10]

# build imm_dates
imm_dates = [f[1] for f in imm_date_helper(start_date=sdate,
                                           tenor_list=tenor_list)]

value_date = sdate.strftime('%d/%m/%Y')
pv_dirty, cs01, dv01, pvbp6m, pvbp1y, pvbp2y, pvbp3y, pvbp4y, pvbp5y, pvbp7y, pvbp10y, 
            duration_in_milliseconds = cds_all_in_one(trade_date,
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
                   imm_dates,
                   verbose)
```

### IMM CDS Dates ###

The first hurdle quite often is how to compute and feed in IMM dates that play nicely with CDS contracts; the imm_date_helper routine has been constructed and tested for this purpose. You can easily bootstrap the necessary IMM date vector for any business date. As you can see in the example below the IMM date roll logic is embedded accurately into the helper based on the semi annual roll. If you are pricing and need IMM dates before the ISDA 2015 semi annual roll change then this is also supported.


```python
    def test_single_rolldate_day_before_rolldate(self):

        # accepted results
        real_result = [('6M', '20/06/2017'),
                   ('1Y', '20/12/2017'),
                   ('2Y', '20/12/2018'),
                   ('3Y', '20/12/2019'),
                   ('5Y', '20/12/2021'),
                   ('7Y', '20/12/2023')]

        sdate = datetime.datetime(2017, 3, 17)
        tenor_list = [0.5, 1, 2, 3, 5, 7]
        local_result = imm_date_helper(start_date=sdate,
                                 tenor_list=tenor_list,
                                 format='%d/%m/%Y')

        #print sdate, local_result

        for (r,l) in zip(real_result, local_result):
            self.assertTrue(r[0] == l[0] and r[1] == l[1])

    def test_single_rolldate_day_after_rolldate(self):

        # accepted results
        real_result = [('6M', '20/12/2017'),
                   ('1Y', '20/06/2018'),
                   ('2Y', '20/06/2019'),
                   ('3Y', '20/06/2020'),
                   ('5Y', '20/06/2022'),
                   ('7Y', '20/06/2024')]

        sdate = datetime.datetime(2017, 3, 20)
        tenor_list = [0.5, 1, 2, 3, 5, 7]
        local_result = imm_date_helper(start_date=sdate,
                                 tenor_list=tenor_list,
                                 format='%d/%m/%Y')

        #print sdate, local_result

        for (r,l) in zip(real_result, local_result):
            self.assertTrue(r[0] == l[0] and r[1] == l[1])
            
```
