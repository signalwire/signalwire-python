from setuptools import setup

setup(name='signalwire',
      version='1.0.0-rc1',
      description='Provides SignalWire LAML and REST functionality',
      url='https://github.com/signalwire/signalwire-python',
      author='SignalWire Team',
      author_email='open.source@signalwire.com',
      license='MIT',
      packages=['signalwire'],
      install_requires=[
          'twilio',
      ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      zip_safe=False)

