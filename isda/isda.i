%module isda
%{

 #include "isda.h"

 extern "C" int factoral(int n);
 extern "C" int my_mod(int x, int y);
 extern "C" int compute_isda_upfront(double coupon);

%}

%include "std_vector.i"
%include "std_string.i"
namespace std {
  /* On a side note, the names VecDouble and VecVecdouble can be changed, but the order of first the inner vector matters !*/
  %template(VecDouble) vector<double>;
  %template(VecVecdouble) vector< vector<double> >;

  %template(VecInteger) vector<int>;
  %template(VecVecInteger) vector< vector<int> >;

  %template(VecString) vector<string>;
  %template(VecVecString) vector< vector<string> >;
}

/* turn on director wrapping Callback */
%feature("director") Callback;

%include "isda.h"

extern "C" int factoral(int n);
extern "C" int my_mod(int x, int y);
extern "C" int compute_isda_upfront(double coupon);
