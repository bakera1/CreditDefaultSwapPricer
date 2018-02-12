cd isda_cds_model_c_v1.8.2/swig/isda/
gcc -fPIC -g -c -DUNIX -DLINUX -DVERSION="1.8.2" example.c main.c -O3 -I"C:\Python27\Include" -L "C:\Python27\libs" -l python27

g++ -fPIC -c cfinanci.cpp isda.cpp -O3 -ftree-vectorizer-verbose=1 -I"C:\Python27\Include" -L "C:\Python27\libs" -l python27

rem g++ -c -fPIC isda_wrap.cxx  -I"C:\Python27\Include" -L "C:\Python27\libs" -l python27

g++  -shared  -L "C:\Python27\libs"  -Wl,-soname,_isda.pyd -o _isda.pyd example.o isda.o isda_wrap.o busday.o cdsbootstrap.o cdsone.o cerror.o cfileio.o cxzerocurve.o cxbsearch.o defaulted.o tcurve.o version.o cmemory.o cx.o interpc.o gtozc.o zcall.o bsearch.o cfinanci.o buscache.o dtlist.o dateconv.o rtbrent.o zcswap.o schedule.o streamcf.o zcswdate.o badday.o feeleg.o cds.o ldate.o date_sup.o zcswutil.o yearfrac.o strutil.o lintrp1.o datelist.o lscanf.o timeline.o cxdatelist.o convert.o stub.o cashflow.o contingentleg.o zr2coup.o lprintf.o fltrate.o zr2fwd.o dateadj.o zerocurve.o main.o -l python27

copy isda.py ..\..\..\cds
copy _isda.pyd ..\..\..\cds
cd ..\..\..\
