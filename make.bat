cd isda_cds_model_c_v1.8.2/swig/isda/
gcc -fPIC -g -c -DUNIX -DLINUX -DVERSION="1.8.2" example.c main.c busday.c cds.c cdsbootstrap.c cdsone.c cerror.c cfileio.c cxzerocurve.c cxbsearch.c defaulted.c tcurve.c version.c zerocurve.c cmemory.c cx.c interpc.c gtozc.c zcall.c bsearch.c buscache.c dtlist.c dateconv.c rtbrent.c zcswap.c schedule.c streamcf.c zcswdate.c badday.c feeleg.c cds.c ldate.c date_sup.c zcswutil.c yearfrac.c strutil.c lintrp1.c datelist.c lscanf.c timeline.c cxdatelist.c convert.c stub.c cashflow.c contingentleg.c zr2coup.c lprintf.c fltrate.c zr2fwd.c dateadj.c -O3 -I"C:\Python27\Include" -L "C:\Python27\libs" -l python27

g++ -fPIC -c cfinanci.cpp isda.cpp -O3 -ftree-vectorizer-verbose=1 -I"C:\Python27\Include" -L "C:\Python27\libs" -l python27

rem install swig to enable this step.
rem C:\Program Files (x86)\swigwin-3.0.12\swig -c++ -python isda.i

g++ -c -fPIC isda_wrap.cxx  -I"C:\Python27\Include" -L "C:\Python27\libs" -l python27

g++  -shared  -L "C:\Python27\libs"  -Wl,-soname,_isda.pyd -o _isda.pyd example.o isda.o isda_wrap.o busday.o cdsbootstrap.o cdsone.o cerror.o cfileio.o cxzerocurve.o cxbsearch.o defaulted.o tcurve.o version.o cmemory.o cx.o interpc.o gtozc.o zcall.o bsearch.o cfinanci.o buscache.o dtlist.o dateconv.o rtbrent.o zcswap.o schedule.o streamcf.o zcswdate.o badday.o feeleg.o cds.o ldate.o date_sup.o zcswutil.o yearfrac.o strutil.o lintrp1.o datelist.o lscanf.o timeline.o cxdatelist.o convert.o stub.o cashflow.o contingentleg.o zr2coup.o lprintf.o fltrate.o zr2fwd.o dateadj.o zerocurve.o main.o -l python27

copy isda.py ..\..\..\cds
copy _isda.pyd ..\..\..\cds
cd ..\..\..\
