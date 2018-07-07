import pytchfx
import os
from sqlalchemy import create_engine

if 'test.db' in os.listdir():
    os.remove('test.db')
engine = create_engine('sqlite:///test.db')
pitchfx = pytchfx.Pytchfx(engine=engine)
data = pitchfx.scrape('2016/06/06', '2016/06/06')
