swig -python isda.i
g++ -fPIC -c forward_rate_exposure.cpp
gcc -fPIC -c main.c busday.c cds.c cdsbootstrap.c cdsone.c cerror.c cfileio.c \
	cxzerocurve.c cxbsearch.c defaulted.c tcurve.c version.c zerocurve.c \
	cmemory.c cx.c interpc.c gtozc.c zcall.c bsearch.c cfinanci.cpp \
	buscache.c dtlist.c dateconv.c rtbrent.c zcswap.c schedule.c \
	streamcf.c zcswdate.c badday.c feeleg.c cds.c ldate.c date_sup.c \
	zcswutil.c yearfrac.c strutil.c lintrp1.c datelist.c lscanf.c \
	timeline.c cxdatelist.c convert.c stub.c cashflow.c contingentleg.c \
	zr2coup.c lprintf.c fltrate.c zr2fwd.c dateadj.c \
	isda_wrap.c \
        -I/usr/include/python2.7
swig -v -python isda.i
ld -shared main.o busday.o cdsbootstrap.o cdsone.o cerror.o cfileio.o \
 	cxzerocurve.o cxbsearch.o defaulted.o tcurve.o version.o \
	cmemory.o cx.o interpc.o gtozc.o zcall.o bsearch.o cfinanci.o \
	buscache.o dtlist.o dateconv.o rtbrent.o zcswap.o schedule.o \
	streamcf.o zcswdate.o badday.o feeleg.o cds.o ldate.o date_sup.o \
	zcswutil.o yearfrac.o strutil.o lintrp1.o datelist.o lscanf.o timeline.o \
	cxdatelist.o convert.o stub.o cashflow.o contingentleg.o zr2coup.o \
	lprintf.o fltrate.o zr2fwd.o dateadj.o \
	zerocurve.o isda_wrap.o forward_rate_exposure.o -o _isda.so
#python TestISDA.py
