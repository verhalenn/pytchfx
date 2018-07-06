from distutils.core import setup

setup(name='Pytchfx',
      description='A slower scraper for a faster database.',
      packages=['pytchfx', 'pytchfx.analysis'],
      zip_safe=False,
      install_requires=['sqlalchemy', 'bs4', 'requests'],
      )
