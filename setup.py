from setuptools import setup

setup(name='Pytchfx',
      description='A slower scraper for a faster database.',
      packages=['pytchfx'],
      zip_safe=False,
      install_requires=['sqlalchemy', 'bs4', 'requests'],
      )
