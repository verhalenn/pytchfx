Three Tables:

* linescores
* atbats
* pitches

Connected by:

linescores.game_id = atbats.game_id
atbats.atbat_id = pitches.atbat_id

Linescores Structure
--------------------

gid(char): Unique game id provided by mlb.com. Useful for games without a time_date.

game_id(int): Table key used to connect to the atbats table.

away_name_abbrev(varchar(3)): The three letter away team abbreviation. Team Abbreviations can be found at the bottom.

away_team_runs(int): The number of runs scored by the away team in that game.

away_team_hits(int): The number of hits the away team made in that game.

away_team_errors(int): The number of errors the away team commited in that game.

home_name_abbrev(varchar(3)): The three letter home team abbreviation: Team Abbreviations can be found at the bottom.

home_team_runs(int): The number of runs scored by the home team in that game.

home_team_hits(int): The number of hits the home team made in that game.

home_team_errors(int): The number of errors the home team commited in that game.

double_header_sw(varchar(1)): One letter abbreviation for whether or not it was a double header. 'Y' and 'S' meaning yes
and 'N' meaning No.

game_type(varchar(1)): One letter abbreviation for the game type.

* R: Regular Season
* E: I'm not sure what the E stands for but it seems to be all the college games.
* S: Spring Training
* A: Allstar game
* D: Division Championship Series
* L: League Championship Series
* W: World Series
* F: Wild Card Games

inning(int): What inning the game ended on.

status(varchar(15): Whether or no the game finished.

top_inning(tinyint): What side of the inning the game finished on.

time_date(datetime): What was the time and date the game was started on.

original_date(datetime): If the game was postponed what was it's original dat.

Atbats Structure
----------------

atbat_id(int): Table key used to connect to pitches table.

game_id(int): Table key used to connect to linescores table.

inning(tinyint): The inning the atbat took place in.

top(tinyint): whether it was the top or the bottom of the inning.

start_tfs_zulu(datetime): The time in which the inning started at.

pitcher(varchar(30)): The name of the pitcher in the atbat.

batter(varchar(30)): The name of the batter in the atbat.

stand(varchar(1)): Single letter representing the stance of the batter.

away_team_runs(int): The number of runs through out the game the away team has scored by the end of the atbat.
Null if no runs were scored in the atbat.

home_team_runs(int): The number of runs through out the game the home team has scored by the end of the atabt.
null if no runs were scored in the atabt.

b(int): The count of balls at the end of the atbat. 0 unless a walk in spring training games.

s(int): The count of strikes at the end of the atbat. 0 unless a strikeout in spring training games.

o(int): The number of outs at the end of the atbat.

event(varchar(20)): A short description of the of the atbat result.

Pitches Structure
-----------------

Some information provided by Mike Fast at https://fastballs.wordpress.com/2007/08/02/glossary-of-the-gameday-pitch-fields/

pitch_id(int): Unique pitch_id provided by the engine.

atbat_id(int): Table key used to connect to the atbats table.

id(int): Unique pitch id provided by the PITCHf/x

x, y (float): Old dimensions, not really used anymore. Not sure why I included it in the database. y is now z in the new
system.

x0(float): The left/right distance in feet where the initial point is measured.

y0(float): The distance in feet from home plate where the the initial point is measured. It has been changed at
different times but has been set to 50 since 2007.

z0(float): The vertical distance in feet of where the initial point was measured.

ax, ay, az(float): The acceleration as measured at the intial point.

break_angle(float): : the angle, in degrees, from vertical to the
straight line path from the release point to where the pitch crossed
the front of home plate, as seen from the catcher’s/umpire’s perspective.

break_length(float):  the measurement of the greatest distance, in inches,
between the trajectory of the pitch at any point between the release point
and the front of home plate, and the straight line path from the release
point and the front of home plate.

break_y(float):  the distance in feet from home plate to the point in
the pitch trajectory where the pitch achieved its greatest deviation
from the straight line path between the release point and the front of
home plate.

des(varchar(25)): A brief description of the result of the pitch.

start_speed(float): The speed of the pitch measured in all three dimensions at the initial point. This is generally what
is seen on the radar gun.

end_speed(float): The speed of the pitch as it crosses home plate.

nasty(int): Not entirely sure.

pfx_x, pfx_z(float): The amount of break in the pitch between the 40 from home plate and home plate, in inches, as
compared to a pitch thrown at the same speed with no spin-induced movement.

pitch_type(varchar(2)): The most probable pitch type.

px, pz (float): The coordinates in feet as it crosses home plate. Y not being needed because it's already set.

spin_dir(float): Not entirely positive. But I would have to guess the angle of the spin.

spin_rate(float): The number of rotations a second the ball was thrown at.

sz_bot(float): Tho distance from the ground in feet to the bottom of the players strike zone as set by the PITCHf/x operator.

sz_top(float): The distance from the ground in feet to the top of the players strike zone as set by the PITCHf/x operator.

tfs_zulu(datetime): The start time of the pitch at the zulu time zone or GMT

type(varchar(1)): One letter abbreviation for the result of the pitch. B: Ball; S: Strike; X: In Play.

type_confidence(float): How confident they are of the pitch_type.

vx0, vy0, vz0 (float): The initial velocity

zone(int):....................................................

