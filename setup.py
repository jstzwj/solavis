#!/usr/bin/env python

from distutils.core import setup

setup(name='solavis',
      version='0.1',
      description='crawler framework',
      author='JunWang',
      author_email='jstzwj@aliyun.com',
      license="MIT",
      keywords="crawler",
      url='https://github.com/jstzwj/solavis.git',
      packages=['solavis',
            'solavis.core',
            'solavis.contrib'],
      install_requires=[
            'lxml==4.3.3',
            'requests==2.21.0',
            'aiohttp==3.6.2'
      ],
     )