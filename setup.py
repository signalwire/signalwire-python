from setuptools import setup, find_packages

setup(name='signalwire',
      version='1.2',
      description='Provides SignalWire LAML and REST functionality',
      url='https://github.com/signalwire/signalwire-python',
      author='SignalWire Team',
      author_email='open.source@signalwire.com',
      license='MIT',
      packages=find_packages(exclude=['tests', 'tests.*']),
      install_requires=[
          'twilio==6.16.4',
      ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      zip_safe=False)

