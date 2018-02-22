import pandas as pd

class Player:

    def __init__(self, player_data):
        try:
            self.atbats = player_data['atbats']
            self.pitches = player_data['pitches']
        except NameError:
            print("There needs to be an 'atbats' and a 'pitches' dataframe in the player_data dictionary.")
