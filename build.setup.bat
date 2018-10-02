"c:\python27\python.exe" setup.py clean
"c:\python27\python.exe" setup.py build_ext  --compiler=mingw32
"c:\python27\python.exe" setup.py build_py -c
"c:\python27\python.exe" setup.py sdist
"c:\python27\python.exe" setup.py install
