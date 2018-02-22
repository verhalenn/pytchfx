from pytchfx import Pytchfx
from sqlalchemy import create_engine

engine = create_engine('sqlite://')
pitchfx = Pytchfx(engine=engine)
data = pitchfx.scrape('2016/06/06', '2016/06/06')
test = pitchfx.get_batter('Kris Bryant')
