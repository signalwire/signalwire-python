import os, codecs, re
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

def read(*file_paths):
  """Read file data."""
  with codecs.open(os.path.join(HERE, *file_paths), "r") as file_in:
    return file_in.read()

def get_version():
  content = read('signalwire/__init__.py')
  match = re.search(r"^__version__ = '(.*)'$", content, re.MULTILINE)
  if match:
    return match.group(1)
  raise RuntimeError('Unable to find package version!')

CLASSIFIERS = [
  'Development Status :: 5 - Production/Stable',
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
  version=get_version(),
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
    'twilio==6.54.0',
    'aiohttp==3.9.5',
  ],
  python_requires='>=3.6',
  zip_safe=False
)
