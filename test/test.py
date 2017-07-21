from pytchfx.download import scrape
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('sqlite://')
scrape('2016/06/06', '2016/06/06', engine)
print(pd.read_sql_table('linescores', engine))
