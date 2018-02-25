import requests
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET
from pytchfx.database import Atbat, Pitch, Linescore, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from datetime import datetime as dt, timedelta as td
from .analysis.basepytchfxdata import BasePytchfxData
import pandas as pd

class Pytchfx:

    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    # Get each game id out of a specific date.
    def _get_gids(self, date):
        links = []
        # Setup the link
        base_link = "http://gd2.mlb.com/components/game/mlb/"
        day = base_link + date.strftime("year_%Y/month_%m/day_%d")
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
                if link_address.startswith(date.strftime("day_%d/gid_")):
                    print(link_address)
                    links.append(day + link_address[6:])
        # Return the links
        return links


    # Get the linescore data
    def _get_linescore(self, link):
        r = requests.get(link + 'linescore.xml')
        gid = link.split('/')[-2]
        date = dt.strptime(link[39:64], 'year_%Y/month_%m/day_%d').date()
        print(r.url)
        # Check to see if you could find the link
        if r.status_code != 200:
            print("Couldn't find {0}. Sorry!".format(link + 'linescore.xml'))
            return None
        else:
            # Extract data using elementtree
            game = ET.fromstring(r.content).attrib
            linescore = Linescore(**game)
            linescore.gid = gid
            linescore.date = date
            # convert top inning to boolean
            linescore.top_inning = linescore.top_inning == 'Y'
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
    def _get_players(self, link):
        # Get players.xml for game with requests
        r = requests.get(link + 'players.xml')
        print(r.url)
        # Check to make sure the xml could be found
        if r.status_code != 200:
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
    def _get_inning_all(self, link, players):
        # Get data from url using requests
        r = requests.get(link + 'inning/inning_all.xml')
        print(r.url)
        # Check to make sure url worked
        if r.status_code != 200:
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


    def _get_data(self, link):
        # Get the linescores and player names
        players = self._get_players(link=link)
        game = self._get_linescore(link=link)
        # If you have the players names and linescores get the rest of the data.
        if players is not None and game is not None:
            game.atbats = self._get_inning_all(link=link, players=players)
        return game


    # This is the main function that scrapes every game from the start to the end
    # date.
    def scrape(self, start, end, pool_size=1):
        # Setting up the sqlalchemy objects.
        Base.metadata.create_all(self.engine)
        # Converting the dates from a string to a datetime object
        date = dt.strptime(start, '%Y/%m/%d')
        end_date = dt.strptime(end, '%Y/%m/%d')
        # Loops through each date
        while date <= end_date:
            # Find the games on that particular date
            links = self._get_gids(date)
            # Get the data from each game on date
            for link in links:
                game = self._get_data(link=link)
                # Iteratively add each game to the database
                if game is not None:
                    self.session.add(game)
                # Commit to the session and add one day to the date variable
                self.session.commit()
                date += td(1)


    # Update the database from last day downloaded to today.
    def update(self, engine):
        start_time_date = self.session.query(func.max(Linescore.date)).scalar()
        current_max = start_time_date.strftime('%Y/%m/%d')
        start_time_date += td(days=1)
        end_time_date = dt.now() - td(days=1)
        start = start_time_date.strftime('%Y/%m/%d')
        end = end_time_date.strftime('%Y/%m/%d')
        if current_max < end:
            self.scrape(start=start, end=end)
        else:
            print('Already up to date.')

    def get_batter(self, batter_name):
        atbat_data = pd.read_sql(self.session.query(Atbat).join(Pitch).filter(
            Atbat.batter==batter_name).statement,
                                  self.session.bind)
        pitch_data = pd.read_sql(self.session.query(Pitch).join(Atbat).filter(
            Atbat.batter==batter_name).statement,
                                 self.session.bind)
        batter_data = {'atbats': atbat_data, 'pitches': pitch_data}
        return BasePytchfxData(batter_data)
