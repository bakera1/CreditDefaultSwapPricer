import os
import glob
import sysconfig
from distutils.core import setup, Extension

extra_compile_args = sysconfig.get_config_var('CFLAGS').split()
extra_compile_args += ["-fPIC", "-g", "-c", "-DUNIX", "-DLINUX"]
extra_compile_args += ["-DNDEBUG", "-O3"]

ext_module_cpp = Extension('isda',
		       define_macros= [('VERSION', '1.8.2')],
                       sources=glob.glob(os.path.join(os.getcwd(), 'isda_cds_model_c_v1.8.2/swig/isda/*.cpp')),
		       extra_compile_args=extra_compile_args,
		       extra_link_args=["-lstdc++"],
                       depends=['hello.h'],
                   )
ext_module_c = Extension('isda',
		       define_macros= [('VERSION', '1.8.2')],
                       sources=glob.glob(os.path.join(os.getcwd(), 'isda_cds_model_c_v1.8.2/swig/isda/*.c')),
		       extra_compile_args=extra_compile_args,
		       extra_link_args=["-lstdc++"],
                       depends=['hello.h'],
                   )

ext_module_cxx = Extension('isda',
		       define_macros= [('VERSION', '1.8.2')],
		       include_dirs=['/usr/include/python2.7'],
                       sources=glob.glob(os.path.join(os.getcwd(), 'isda_cds_model_c_v1.8.2/swig/isda/*.cxx')),
		       extra_compile_args=extra_compile_args,
		       extra_link_args=["-lstdc++"],
                       depends=['hello.h'],
                   )

setup (name = 'Credit Default Swap Pricer',
       version = '1.0.0',
       description = "Simple ISDA based Credit Default Swap Pricer and Risk Engine",
       ext_modules = [ext_module_c, ext_module_cpp],
       py_modules = ["hello"],
   )
