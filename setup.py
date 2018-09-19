from setuptools import setup

setup(name='SignalWire Python SDK',
      version='0.1',
      description='Provides Twilio-like functionality to SignalWire LAML',
      url='https://github.com/signalwire/signalwire-python',
      author='Luca Pradovera',
      author_email='luca@signalwire.com',
      license='MIT',
      packages=['signalwire'],
      install_requires=[
          'twilio',
      ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      zip_safe=False)

