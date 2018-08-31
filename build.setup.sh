rm -rf hatch
python setup.py clean
python setup.py build_ext
python setup.py build_py -c
python setup.py sdist
sudo python setup.py install
