from distutils.core import setup
try:
    import py2exe
except:
	print "[Warning] Cannot import py2exe"

# get py2exe from http://www.lfd.uci.edu/~gohlke/pythonlibs/#py2exe
#     python setup.py py2exe
# or, if you want to install this on linux
#     python setup.py install

setup(
    name='watch',
    packages=["watch"], 
    package_dir={'watch': '.'},
    scripts=['watch.py'],
    console=['watch.py']
)
