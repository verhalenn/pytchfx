from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, Integer, String, DateTime, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class Linescore(Base):
    __tablename__ = 'linescores'

    game_id = Column(Integer, primary_key=True)
    away_name_abbrev = Column(String)
    away_team_runs = Column(Integer)
    away_team_hits = Column(Integer)
    away_team_erros = Column(Integer)
    home_name_abbrev = Column(String)
    home_team_runs = Column(Integer)
    home_team_hits = Column(Integer)
    home_team_errors = Column(Integer)
    double_header_sw = Column(String)
    game_type = Column(String)
    inning = Column(Integer)
    status = Column(String)
    top_inning = Column(Boolean)
    time_date = Column(DateTime)
    original_date = Column(DateTime)

    def __init__(self, **entries):
        self.__dict__.update(entries)


class Atbat(Base):
    __tablename__ = 'atbats'

    atbat_id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('linescores.game_id'), index=True)

    game = relationship('Linescore', back_populates='atbats')

    top = Column(Boolean)
    start_tfs_zulu = Column(DateTime)
    pitcher = Column(String)
    batter = Column(String)
    stand = Column(String)
    away_team_runs = Column(Integer)
    home_team_runs = Column(Integer)
    b = Column(Integer)
    s = Column(Integer)
    o = Column(Integer)
    event = Column(String)

    def __init__(self, **entries):
        self.__dict__.update(entries)


class Pitch(Base):
    __tablename__ = 'pitches'

    pitch_id = Column(Integer, primary_key=True)
    atbat_id = Column(Integer, ForeignKey('atbats.atbat_id'), index=True)

    atbat = relationship('Atbat', back_populates="pitches")

    id = Column(Integer)
    ax = Column(Float)
    ay = Column(Float)
    az = Column(Float)
    break_angle = Column(Float)
    break_length = Column(Float)
    break_y = Column(Float)
    des = Column(String)
    start_speed = Column(Float)
    end_speed = Column(Float)
    nasty = Column(Integer)
    pfx_x = Column(Float)
    pfx_z = Column(Float)
    pitch_type = Column(String)
    px = Column(Float)
    pz = Column(Float)
    spin_dir = Column(Float)
    spin_rate = Column(Float)
    sz_bot = Column(Float)
    sz_top = Column(Float)
    tfs_zulu = Column(DateTime)
    type = Column(String)
    type_confidence = Column(Float)
    vx0 = Column(Float)
    vy0 = Column(Float)
    vz0 = Column(Float)
    x = Column(Float)
    x0 = Column(Float)
    y = Column(Float)
    y0 = Column(Float)
    z0 = Column(Float)
    zone = Column(Integer)

    def __init__(self, **entries):
        self.__dict__.update(entries)


Atbat.pitches = relationship('Pitch',
                             order_by=Pitch.pitch_id,
                             back_populates='atbat')
Linescore.atbats = relationship('Atbat',
                                order_by=Atbat.atbat_id,
                                back_populates='game')
