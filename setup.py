from distutils.core import setup
import setuptools

setup(
  name = 'music',
  py_modules = ['musicBase', 'matchMyMusic', 'matchMusicName', 'primeDirectory', 'myMusicDBMap'],
  version = '0.0.1',
  description = 'A Python Wrapper for Music Data',
  long_description = open('README.md').read(),
  author = 'Thomas Gadfort',
  author_email = 'tgadfort@gmail.com',
  license = "MIT",
  url = 'https://github.com/tgadf/discogs',
  keywords = ['Discogs', 'music'],
  classifiers = [
    'Development Status :: 3',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
  ],
  install_requires=['jupyter_contrib_nbextensions'],
  dependency_links=['matchAlbums==0.0.1', 'musicdb==0.0.1'
                    'git+ssh://git@github.com/tgadf/musicdb.git#egg=musicdb-0.0.1',]
)
 
