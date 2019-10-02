import os, codecs
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

def read(*file_paths):
  """Read file data."""
  with codecs.open(os.path.join(HERE, *file_paths), "r") as file_in:
    return file_in.read()

CLASSIFIERS = [
  'Development Status :: 4 - Beta',
  'Intended Audience :: Developers',
  'Intended Audience :: Information Technology',
  'Intended Audience :: Telecommunications Industry',
  'License :: OSI Approved :: MIT License',
  'Natural Language :: English',
  'Topic :: Communications',
  'Topic :: Software Development'
]

setup(
  name='signalwire',
  version='2.0.0b2',
  description='Client library for connecting to SignalWire.',
  long_description=read('README.md'),
  long_description_content_type="text/markdown",
  classifiers=CLASSIFIERS,
  url='https://github.com/signalwire/signalwire-python',
  author='SignalWire Team',
  author_email='open.source@signalwire.com',
  license='MIT',
  packages=find_packages(exclude=['tests', 'tests.*']),
  install_requires=[
    'twilio==6.16.4',
    'aiohttp',
    'asyncio'
  ],
  python_requires='>=3.6',
  zip_safe=False
)
