# from distutils.core import setup, Extension
from setuptools import setup, Extension

module1 = Extension('_isda', extra_compile_args=['-std=c++11'],
                    include_dirs=['/usr/include/python3.6'],
                    library_dirs=['/usr/lib/python3.6'],
                    define_macros=[('LINUX', None)],
                    sources=['isda/example.c',
                             'isda/main.c',
                             'isda/busday.c',
                             'isda/cdsbootstrap.c',
                             'isda/cdsone.c',
                             'isda/cerror.c',
                             'isda/cfileio.c',
                             'isda/cxzerocurve.c',
                             'isda/cxbsearch.c',
                             'isda/defaulted.c',
                             'isda/tcurve.c',
                             'isda/version.c',
                             'isda/zerocurve.c',
                             'isda/cmemory.c',
                             'isda/cx.c',
                             'isda/interpc.c',
                             'isda/gtozc.c',
                             'isda/zcall.c',
                             'isda/bsearch.c',
                             'isda/cfinanci.cpp',
                             'isda/buscache.c',
                             'isda/dtlist.c',
                             'isda/dateconv.c',
                             'isda/rtbrent.c',
                             'isda/zcswap.c',
                             'isda/schedule.c',
                             'isda/streamcf.c',
                             'isda/zcswdate.c',
                             'isda/badday.c',
                             'isda/feeleg.c',
                             'isda/cds.c',
                             'isda/ldate.c',
                             'isda/date_sup.c',
                             'isda/zcswutil.c',
                             'isda/yearfrac.c',
                             'isda/strutil.c',
                             'isda/lintrp1.c',
                             'isda/datelist.c',
                             'isda/lscanf.c',
                             'isda/timeline.c',
                             'isda/cxdatelist.c',
                             'isda/convert.c',
                             'isda/stub.c',
                             'isda/cashflow.c',
                             'isda/contingentleg.c',
                             'isda/zr2coup.c',
                             'isda/lprintf.c',
                             'isda/fltrate.c',
                             'isda/zr2fwd.c',
                             'isda/dateadj.c', 'isda/isda.cpp', 'isda/isda_wrap.cxx'])

readme = open('README.md').read()

setup(name='isda',
      version='1.0.22',
      author='Alexander Baker',
      license='MIT',
      author_email='baker.alexander@gmail.com',
      description='Package that delivers high performance pricing and risk for credit derivatives',
      url='https://github.com/bakera1/CreditDefaultSwapPricer/',
      # ext_package='isda',
      # py_modules=['isda'],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX :: Linux",
      ],
      packages=[
          'isda', 'isda.tests'
      ],
      keywords="credit derivative pricing risk",
      include_package_data=True,
      ext_modules=[module1])
