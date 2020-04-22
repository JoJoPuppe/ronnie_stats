from app import app
from datetime import datetime, timezone
from datetime import timedelta
from sqlalchemy import func
from app.models import MatchStats, MatchPlayerStats

class MatchConverter(object):
    def __init__(self, playername):
        self.playername = playername

    def from_database_matchplayerstats(self, playername):
        return MatchPlayerStats.query.filter(MatchPlayerStats.playername == playername).\
                order_by(MatchPlayerStats.timestamp).limit(20).all()

    def from_database_matchstats(self, playername):
        return MatchStats.query.filter(MatchStats.playername == playername).\
                order_by(MatchStats.timestamp).limit(20).all()

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

    def convert_epoch_time(self, seconds):
        local_time = datetime.fromtimestamp(seconds)
        return [local_time.strftime('%a %d.%m.%y'), local_time.strftime('%H:%M')]

    def convert_inches(self, inches):
        meter = inches // 39.3701
        kilometer = round(meter / 1000, 2)
        return f"{kilometer}km"


    def create_match_data(self):
        q2 = self.from_database_matchstats(str(self.playername))
        q = self.from_database_matchplayerstats(str(self.playername))

        self.match_list = []

        for m in range(0, len(q2)):
            match_stats_dict = {}
            match_stats = vars(q2[m])
            if '_sa_instance_state' in match_stats:
                del match_stats['_sa_instance_state']

            match_stats_dict['matchDate'] = self.convert_epoch_time(match_stats['utcStartSeconds'])[0]
            match_stats_dict['matchStart'] = self.convert_epoch_time(match_stats['utcStartSeconds'])[1]
            match_stats_dict['matchEnd'] = self.convert_epoch_time(match_stats['utcEndSeconds'])[1]


            match_stats_dict['duration'] = self.strfdelta(match_stats['duration']//1000,'{minutes}m: {seconds}s')
            match_stats_dict['playerCount'] = match_stats['playerCount']
            match_stats_dict['teamCount'] = match_stats['teamCount']
            match_stats_dict['gameMode'] = match_stats['gameMode']


            player_match_stats = vars(q[m])
            if '_sa_instance_state' in player_match_stats:
                del player_match_stats['_sa_instance_state']

            for k, v in player_match_stats.items():
                match_stats_dict[k] = v

            match_stats_dict['kdRatio'] = round(match_stats_dict['kdRatio'], 2)
            match_stats_dict['scorePerMinute'] = round(match_stats_dict['scorePerMinute'], 2)
            seconds = match_stats_dict['timePlayed']
            match_stats_dict['timePlayed'] = self.strfdelta(seconds, "{minutes}m: {seconds}s")
            survival_sec = match_stats_dict['teamSurvivalTime'] // 1000
            match_stats_dict['teamSurvivalTime'] = self.strfdelta(survival_sec, '{minutes}m: {seconds}s')
            match_stats_dict['percentTimeMoving'] = round(match_stats_dict['percentTimeMoving'])
            match_stats_dict['distanceTraveled'] = self.convert_inches(match_stats_dict['distanceTraveled'])

            self.match_list.append(match_stats_dict)

        return self.match_list




