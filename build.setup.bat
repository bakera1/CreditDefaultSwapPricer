python setup.py clean
rem python setup.py build_ext
rem python setup.py build_py -c
"C:\Users\bakera\AppData\Local\Programs\Python\Python37\python.exe" setup.py bdist bdist_wheel
rem "C:\Users\bakera\AppData\Local\Programs\Python\Python36\python.exe" setup.py bdist bdist_wheel
rem "C:\Users\bakera\AppData\Local\Programs\Python\Python35\python.exe" setup.py bdist bdist_wheel

rem cd dist
pip uninstall -y dist\isda-1.0.7-cp37-cp37m-win_amd64.whl
pip install dist\isda-1.0.7-cp37-cp37m-win_amd64.whl
python -m unittest discover -v -s c:\users\bakera\AppData\Local\Programs\Python\Python37\Lib\site-packages\isda\tests


rem flip to execute the installed test suite!
rem cd "..\isda\lib\src\tests"
rem cd "C:\Users\bakera\AppData\Local\Programs\Python\Python37\Lib\site-packages\isda\lib\src\tests"
rem python TestCdsoPricer.py
