import seaborn as sns
import matplotlib.pyplot as plt

class BasePytchfxData:

    def __init__(self, player_data):
        try:
            self.atbats = player_data['atbats']
            self.pitches = player_data['pitches']
        except NameError:
            print("There needs to be an 'atbats' and a 'pitches' dataframe in the player_data dictionary.")

    def pitch_result(self):
        for result in self.pitches.type.unique():
            result_data = self.pitches[self.pitches.type == result]
            sns.distplot(result_data.start_speed)
        plt.show()