import requests
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET
from database import Atbat, Pitch, Linescore, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from datetime import datetime as dt, timedelta as td
from multiprocessing import Pool


# Get each game id out of a specific date.
def _get_gids(date):
    links = []
    # Setup the link
    base_link = "http://gd2.mlb.com/components/game/mlb/"
    day = base_link + date.strftime("year_%Y/month_%m/day_%d/")
    # Get the link using requests
    r = requests.get(day)
    # Check if the link works
    if (r.status_code != 200):
        print("Couldn't find that link: " + day)
    else:
        # Use BeautifulSoup to find links that start with 'gid_' and add it to the links.
        soup = BeautifulSoup(r.text, 'lxml')
        for link in soup.find_all('a'):
            link_address = link.get('href')
            if link_address.startswith('gid_'):
                print(link_address)
                links.append(day + link_address)
    # Return the links
    return links


# Get the linescore data
def _get_linescore(link):
    r = requests.get(link + 'linescore.xml')
    gid = link.split('/')[-1]
    print(r.url)
    # Check to see if you could find the link
    if (r.status_code != 200):
        print("Couldn't find {0}. Sorry!".format(link + 'linescore.xml'))
        return None
    else:
        # Extract data using elementtree
        game = ET.fromstring(r.content).attrib
        linescore = Linescore(**game)
        linescore.gid = gid
        # convert the time date and original date
        try:
            linescore.time_date = dt.strptime(linescore.time_date,
                                              '%Y/%m/%d %H:%M')
            # If it is a PM game add 12 hours
            if linescore.ampm == 'PM':
                linescore.time_date += td(hours=12)
        except:
            linescore.time_date = None
        try:
            linescore.original_date = dt.strptime(linescore.original_date,
                                                  '%Y/%m/%d')
        except:
            linescore.original_date = None
        return linescore


# Get player names
def _get_players(link):
    # Get players.xml for game with requests
    r = requests.get(link + 'players.xml')
    print(r.url)
    # Check to make sure the xml could be found
    if (r.status_code != 200):
        print("Couldn't find {0}. Sorry!".format(link + 'players.xml'))
        return None
    else:
        # Use BeautifulSoup to find the players
        soup = BeautifulSoup(r.text, 'xml')
        players = {}
        for player in soup.find_all('player'):
            # Create a dictionary that links players id's with their full names.
            attr = player.attrs
            players[attr['id']] = attr['first'] + ' ' + attr['last']
        return players


# Get atbat and pitchfx data
def _get_inning_all(link, players):
    # Get data from url using requests
    r = requests.get(link + 'inning/inning_all.xml')
    print(r.url)
    # Check to make sure url worked
    if (r.status_code != 200):
        print("Sorry. Couldn't find {0}."
              .format(link + 'inning/inning_all.xml'))
        return []
    else:
        # Parse data using elementtree
        tree = ET.fromstring(r.content)
        atbats = []
        # Loop through each inning
        for inning in tree.findall('.//inning'):
            # Hold the inning number
            inning_num = inning.get('num')
            # Loop through each inning side.
            for inning_side in inning.getchildren():
                # Hold the inning side.
                top = inning_side.tag == 'top'
                # Loop through each atbat in the inning side
                for atbat_data in inning_side.findall('.//atbat'):
                    atbat = Atbat(**atbat_data.attrib)
                    # Attribute the inning number to the atbat.
                    atbat.inning = inning_num
                    # Parse the atbat start into a datetime
                    try:
                        atbat.start_tfs_zulu = dt.strptime(atbat.start_tfs_zulu,
                                                           '%Y-%m-%dT%H:%M:%SZ')
                    except:
                        atbat.start_tfs_zulu = None
                    # Link the batter to the batters name using the pitchers dictionary.
                    atbat.batter = players[atbat.batter]
                    atbat.pitcher = players[atbat.pitcher]
                    # Attribute the inning side to the atbat
                    atbat.top = top
                    # Find all the pitches in the atbat and loop through them.
                    pitch_data = atbat_data.findall('pitch')
                    pitches = [Pitch(**pitch.attrib) for pitch in pitch_data]
                    for pitch in pitches:
                        # Parse the tfs_zulu into a datetime for each pitch.
                        try:
                            pitch.tfs_zulu = dt.strptime(pitch.tfs_zulu,
                                                         '%Y-%m-%dT%H:%M:%SZ')
                        except:
                            pitch.tfs_zulu = None
                    # Connect the pitches to the atbat
                    atbat.pitches = pitches
                    # Append the atbat list with the finish atbat to be returned
                    atbats.append(atbat)
        return atbats


def _get_data(link):
    # Get the linescores and player names
    players = _get_players(link=link)
    game = _get_linescore(link=link)
    # If you have the players names and linescores get the rest of the data.
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


# Update the database from last day downloaded to today.
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
