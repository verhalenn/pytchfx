import seaborn as sns
import matplotlib.pyplot as plt

class BasePytchfxData:

    def __init__(self, player_data):
        try:
            self.atbats = player_data['atbats']
            self.pitches = player_data['pitches']
        except NameError:
            print("There needs to be an 'atbats' and a 'pitches' dataframe in the player_data dictionary.")

    def pitch_result_speed(self):
        for result in self.pitches.type.unique():
            result_data = self.pitches[self.pitches.type == result]
            sns.distplot(result_data.start_speed, label=result)
        plt.legend()
        plt.show()

    def pitch_result_spin(self):
        for result in self.pitches.type.unique():
            result_data = self.pitches[self.pitches.type == result]
            sns.distplot(result_data.spin_rate, label=result)
        plt.legend()
        plt.show()

    def pitch_type_stats(self):
        pitch_type = self.pitches.groupby('pitch_type')['start_speed', 'spin_rate', 'z0', 'x0', 'break_length',
            'break_angle'].mean()
        pitch_type['Percent'] = self.pitches.pitch_type.value_counts(normalize=True) * 100
        pitch_type['Count'] = self.pitches.pitch_type.value_counts(normalize=False)
        return(pitch_type)

    def pitch_type_speed(self):
        for pitch_type in self.pitches.pitch_type.unique():
            result_data = self.pitches[self.pitches.pitch_type == pitch_type]
            sns.distplot(result_data.start_speed, label=pitch_type)
        plt.legend()
        plt.show()

    def pitch_type_spin(self):
        for pitch_type in self.pitches.pitch_type.unique():
            result_data = self.pitches[self.pitches.pitch_type == pitch_type]
            sns.distplot(result_data.spin_rate, label=pitch_type)
        plt.legend()
        plt.show()

    def pitch_des_stats(self):
        des = self.pitches.groupby('des')['start_speed', 'spin_rate', 'z0', 'x0', 'break_angle', 'break_length'].mean()
        des['count'] = self.pitches.des.value_counts()
        return des
