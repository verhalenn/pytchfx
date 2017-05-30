import requests
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET
from database import Atbat, Pitch, Linescore, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from datetime import datetime as dt, timedelta as td
from multiprocessing import Pool


def _get_gids(date):
    links = []
    base_link = "http://gd2.mlb.com/components/game/mlb/"
    day = base_link + date.strftime("year_%Y/month_%m/day_%d/")
    r = requests.get(day)
    if (r.status_code != 200):
        print("Couldn't find that link: " + day)
    else:
        soup = BeautifulSoup(r.text, 'lxml')
        for link in soup.find_all('a'):
            link_address = link.get('href')
            if link_address.startswith('gid_'):
                print(link_address)
                links.append(day + link_address)
    return links


def _get_linescore(link):
    r = requests.get(link + 'linescore.xml')
    gid = link.split('/')[-1]
    print(r.url)
    if (r.status_code != 200):
        print("Couldn't find {0}. Sorry!".format(link + 'linescore.xml'))
        return None
    else:
        game = ET.fromstring(r.content).attrib
        linescore = Linescore(**game)
        linescore.gid = gid
        try:
            linescore.time_date = dt.strptime(linescore.time_date,
                                              '%Y/%m/%d %H:%M')
            linescore.time_date += td(hours=12)
        except:
            linescore.time_date = None
        try:
            linescore.original_date = dt.strptime(linescore.original_date,
                                                  '%Y/%m/%d')
        except:
            linescore.original_date = None
        return linescore


def _get_players(link):
    r = requests.get(link + 'players.xml')
    print(r.url)
    if (r.status_code != 200):
        print("Couldn't find {0}. Sorry!".format(link + 'players.xml'))
        return None
    else:
        soup = BeautifulSoup(r.text, 'xml')
        players = {}
        for player in soup.find_all('player'):
            attr = player.attrs
            players[attr['id']] = attr['first'] + ' ' + attr['last']
        return players


def _get_inning_all(link, players):
    r = requests.get(link + 'inning/inning_all.xml')
    print(r.url)
    if (r.status_code != 200):
        print("Sorry. Couldn't find {0}."
              .format(link + 'inning/inning_all.xml'))
        return []
    else:
        tree = ET.fromstring(r.content)
        atbats = []
        for inning in tree.findall('.//inning'):
            inning_num = inning.get('num')
            for inning_side in inning.getchildren():
                if inning_side.tag == 'top':
                    top = True
                else:
                    top = False
                for atbat_data in inning_side.findall('.//atbat'):
                    atbat = Atbat(**atbat_data.attrib)
                    atbat.inning = inning_num
                    try:
                        atbat.start_tfs_zulu = dt.strptime(atbat.start_tfs_zulu,
                                                           '%Y-%m-%dT%H:%M:%SZ')
                    except:
                        atbat.start_tfs_zulu = None
                    atbat.batter = players[atbat.batter]
                    atbat.pitcher = players[atbat.pitcher]
                    atbat.top = top
                    pitch_data = atbat_data.findall('pitch')
                    pitches = [Pitch(**pitch.attrib) for pitch in pitch_data]
                    for pitch in pitches:
                        try:
                            pitch.tfs_zulu = dt.strptime(pitch.tfs_zulu,
                                                         '%Y-%m-%dT%H:%M:%SZ')
                        except:
                            pitch.tfs_zulu = None
                    atbat.pitches = pitches
                    atbats.append(atbat)
        return atbats


def _get_data(link):
    players = _get_players(link=link)
    game = _get_linescore(link=link)
    if players is not None and game is not None:
        game.atbats = _get_inning_all(link=link, players=players)
    return game


# This is the main function that scrapes every game from the start to the end
# date.
def scrape(start, end, engine, pool_size=1):
    # Setting up the sqlalchemy objects.
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    # Setting up the pool for multiprocessing
    p = Pool(pool_size)
    # Converting the dates from a string to a datetime object
    date = dt.strptime(start, '%Y/%m/%d')
    end_date = dt.strptime(end, '%Y/%m/%d')
    # Loops through each date
    while date <= end_date:
        # Find the games on that particular date
        links = _get_gids(date)
        # Get the data from each game on date
        games = p.map(_get_data, links)
        # Iteratively add each game to the database
        for game in games:
            if game is not None:
                session.add(game)
        # Commit to the session and add one day to the date variable
        session.commit()
        date += td(1)


def update(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    start_time_date = session.query(func.max(Linescore.time_date)).scalar()
    current_max = start_time_date.strftime('%Y/%m/%d')
    start_time_date += td(days=1)
    end_time_date = dt.now() - td(days=1)
    start = start_time_date.strftime('%Y/%m/%d')
    end = end_time_date.strftime('%Y/%m/%d')
    if current_max < end:
        scrape(start=start, end=end, engine=engine)
    else:
        print('Already up to date.')
