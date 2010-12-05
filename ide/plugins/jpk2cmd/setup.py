# -*- coding: utf-8 -*-
# Setup script to build the Jaluino Pk2cmd plugin. To build the plugin
# just run 'python setup.py bdist_egg' and an egg will be built and put into 
# the dist directory of this folder.

"""PK2-JaluinoIDE"""

from setuptools import setup
 
__author__ = "Carlo Dormeletti"
__doc__ = """Plugin to control PicKit2 in the JaluinoIDE"""
import jpk2cmd 
__version__ = jpk2cmd.__version__
 
setup(
      name    = "PK2-JaluinoIDE",    # Plugin Name
      version = __version__,         # Plugin Version
      description = __doc__,         # Short plugin description
      author = __author__,     
      author_email = "carlo.dormeletti@email.it", 
      license = "wxWindows",       # Plugins licensing info
      packages = ['jpk2cmd'],     # Package directory name(s)
      entry_points = '''
      [Editra.plugins]
      JPK2 = jpk2cmd:Jpk2cmd
      '''
     )
