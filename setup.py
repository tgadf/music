from distutils.core import setup
import setuptools

setup(
  name = 'music',
  py_modules = ['music'],
  version = '0.0.1',
  description = 'A Python Wrapper For My Music',
  long_description = open('README.md').read(),
  author = 'Thomas Gadfort',
  author_email = 'tgadfort@gmail.com',
  license = "MIT",
  url = 'https://github.com/tgadf/mp3id',
  keywords = ['metadata', 'mp3'],
  classifiers = [
    'Development Status :: 3',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
  ],
  install_requires=['utils==0.0.1', 'mp3id==0.0.1'],
  dependency_links=['git+ssh://git@github.com/tgadf/mp3id.git#egg=mp3id-0.0.1', 'git+ssh://git@github.com/tgadf/utils.git#egg=utils-0.0.1']
)
 

