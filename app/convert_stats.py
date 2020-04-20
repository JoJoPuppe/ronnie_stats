from app import app
from datetime import datetime
from datetime import timedelta
from sqlalchemy import func
from app.models import LifeTimeStats, WeeklyStats

class DataConverter(object):
    def __init__(self):
        self.LT_Table = ['Player', 'Level', 'Wins', 'TOP5', 'TOP10', 'TOP25', 'Kills', 'Downs', 'Deaths', 'KD', 'Score', 'ScoreMin', 'Games', 'Time', 'Contracts']
        self.LT_data_Table = ['playername', 'level', 'wins', 'topFive', 'topTen', 'topTwentyFive', 'kills', 'downs', 'deaths', 'kdRatio', 'score', 'scorePerMinute',
                              'gamesPlayed', 'timePlayed', 'contracts']

        self.WK_Table_Core = ['Player', 'Wins', 'Kills', 'Headshots', 'Deaths', 'KD', 'Score', 'Teamwipes', 'Revives', 'Damage', 'Wounded', 'Games', 'Time']
        self.WK_Table_Core_data = ['playername', 'wins', 'kills', 'headshots', 'deaths', 'kdRatio', 'score', 'teamWipes', 'revives', 'damageDone', 'damageTaken', 'matchesPlayed', 'timePlayed']

        self.WK_Table_Other = ['Player', 'Last Stand Kills', 'Shop', 'Pick Up Tablet', 'Open Boxes', 'Traveled', 'Circle 1', 'Circle 2', 'Circle 3', 'Circle 4', 'Circle 5']
        self.WK_Table_Other_data = ['playername', 'lastStandKills', 'shopping', 'pickupTablet', 'boxesOpen', 'distanceTraveled', 'circle1', 'circle2', 'circle3', 'circle4', 'circle5']

        self.WK_Table_Performance = ['Player','KillsPerGame', 'ScorePerMinute', 'AvgLifeTime']
        self.WK_Table_Performance_data = ['playername', 'killsPerGame', 'scorePerMinute', 'avgLifeTime']

    def from_database_life_time_stats(self):
        return LifeTimeStats.query.group_by(LifeTimeStats.playername).having(func.max(LifeTimeStats.timestamp)).all()

    def from_database_weekly(self, mode="TRIO"):
        return WeeklyStats.query.filter(WeeklyStats.gameMode == mode).\
                group_by(WeeklyStats.playername).having(func.max(WeeklyStats.timestamp)).all()

    def strfdelta(self, sec, fmt):
        d = {}
        d["minutes"], d["seconds"] = divmod(sec, 60)
        d["hours"], d["minutes"] = divmod(d["minutes"], 60)
        return fmt.format(**d)

    def rows_to_columns(self, game_data):
        stats_list = []
        for k, v in game_data[0].items():
            property_list = []
            property_list.append(k)
            for player in game_data:
                property_list.append(player[k])

            stats_list.append(property_list)

        return stats_list

    def create_WK_table(self, mode='TRIO'):
        q = self.from_database_weekly(mode)
        self.player_wk_core_stats = []

        for player in q:
            player_stats_dict = {}
            player_stats = vars(player)
            if '_sa_instance_state' in player_stats:
                del player_stats['_sa_instance_state']
            for out_name, data_name in zip(self.WK_Table_Core, self.WK_Table_Core_data):
                #print(out_name, data_name)
                player_stats_dict[out_name] = player_stats[data_name]

            player_stats_dict['KD'] = round(player_stats_dict['KD'], 2)
            seconds=player_stats_dict['Time']
            player_stats_dict['Time'] = self.strfdelta(seconds, "{hours}h {minutes}m")

            self.player_wk_core_stats.append(player_stats_dict)

        self.player_wk_core_stats = self.rows_to_columns(self.player_wk_core_stats)

        return self.player_wk_core_stats

    def create_LT_table(self):
        q = self.from_database_life_time_stats()
        self.player_stats_list = []

        for player in q:
            player_stats_dict = {}
            player_stats = vars(player)
            if '_sa_instance_state' in player_stats:
                del player_stats['_sa_instance_state']
            for out_name, data_name in zip(self.LT_Table, self.LT_data_Table):
                player_stats_dict[out_name] = player_stats[data_name]

            player_stats_dict['KD'] = round(player_stats_dict['KD'], 2)
            player_stats_dict['ScoreMin'] = round(player_stats_dict['ScoreMin'], 2)
            seconds=player_stats_dict['Time']
            player_stats_dict['Time'] = self.strfdelta(seconds, "{hours}h {minutes}m")

            self.player_stats_list.append(player_stats_dict)

        #self.player_stats_list = self.rows_to_columns(self.player_stats_list)

        return self.player_stats_list




