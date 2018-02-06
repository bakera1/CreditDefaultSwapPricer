gcc -fPIC -c example.c main.c
g++ -fPIC -c isda.cpp -O3 -ftree-vectorizer-verbose=1
swig -c++ -python isda.i

g++ -c -fPIC isda_wrap.cxx -I/usr/include/python2.7 -I/usr/lib/python2.7
g++ -shared -Wl,-soname,_isda.so -o _isda.so example.o isda.o isda_wrap.o \
	busday.o cdsbootstrap.o cdsone.o cerror.o cfileio.o \
	cxzerocurve.o cxbsearch.o defaulted.o tcurve.o version.o \
	cmemory.o cx.o interpc.o gtozc.o zcall.o bsearch.o cfinanci.o \
	buscache.o dtlist.o dateconv.o rtbrent.o zcswap.o schedule.o \
	streamcf.o zcswdate.o badday.o feeleg.o cds.o ldate.o date_sup.o \
	zcswutil.o yearfrac.o strutil.o lintrp1.o datelist.o lscanf.o timeline.o \
	cxdatelist.o convert.o stub.o cashflow.o contingentleg.o zr2coup.o \
	lprintf.o fltrate.o zr2fwd.o dateadj.o zerocurve.o main.o

sudo ldconfig

cp isda.py ../../../cds
cp _isda.so ../../../cds
