from pytchfx.download import scrape
from sqlalchemy import create_engine

engine = create_engine('sqlite://')
scrape('2016/06/06', '2016/06/06', engine)