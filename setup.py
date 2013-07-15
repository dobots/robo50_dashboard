#1/usr/bin/env python
from setuptools import setup
import sys
sys.path.insert(0, 'src')

setup(name='bobby_dashboard',
      version= '0.1.0',
      packages=['bobby_dashboard'],
      package_dir = {'':'src'},
      install_requires=[],
      author = "Dominik Egger", 
      author_email = "dominik@dobots.nl",
      url = "",
      download_url = "", 
      keywords = [],
      classifiers = [
        "Programming Language :: Python", 
        "License :: OSI Approved :: BSD License" ],
      description = "",
      long_description = "",
      license = "BSD"
      )
