import requests
from bs4 import BeautifulSoup
from database import Atbat, Pitch, Linescore, Base
from sqlalchemy.orm import sessionmaker
from datetime import datetime as dt, timedelta as td


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
    print(r.url)
    if (r.status_code != 200):
        print("Couldn't find {0}. Sorry!".format(link + 'linescore.xml'))
        return None
    else:
        game = BeautifulSoup(r.text, 'xml').game.attrs
        linescore = Linescore(**game)
        try:
            linescore.time_date = dt.strptime(linescore.time_date,
                                              '%Y/%m/%d %H:%M')
            linescore.time_date += td(hours=12)
        except ValueError:
            linescore.time_date = None
        try:
            linescore.original_date = dt.strptime(linescore.original_date,
                                                  '%Y/%m/%d')
        except ValueError:
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
        print("Sorry. Couldn't find {0}.".format(link + 'inning/inning_all.xml'))
        return []
    else:
        soup = BeautifulSoup(r.text, 'xml')
        atbats = []
        for atbat_data in soup.find_all('atbat'):
            atbat = Atbat(**atbat_data.attrs)
            try:
                atbat.start_tfs_zulu = dt.strptime(atbat.start_tfs_zulu,
                                                   '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                atbat.start_tfs_zulu = None
            atbat.batter = players[atbat.batter]
            atbat.pitcher = players[atbat.pitcher]
            if atbat_data.parent.name == 'top':
                atbat.top = True
            else:
                atbat.top = False
            pitch_data = atbat_data.find_all('pitch')
            pitches = [Pitch(**pitch.attrs) for pitch in pitch_data]
            for pitch in pitches:
                try:
                    pitch.tfs_zulu = dt.strptime(pitch.tfs_zulu,
                                                 '%Y-%m-%dT%H:%M:%SZ')
                except ValueError:
                    pitch.tfs_zulu = None
            atbat.pitches = pitches
            atbats.append(atbat)
        return atbats


def scrape(start, end, engine):
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    date = dt.strptime(start, '%Y/%m/%d')
    end_date = dt.strptime(end, '%Y/%m/%d')
    while date <= end_date:
        games = _get_gids(date)
        for link in games:
            players = _get_players(link=link)
            game = _get_linescore(link=link)
            if players is not None and game is not None:
                game.atbats = _get_inning_all(link=link, players=players)
                session.add(game)
            session.commit()
        date += td(1)
