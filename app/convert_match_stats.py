from app import app, db
from datetime import datetime, timezone
from datetime import timedelta
from sqlalchemy import func, desc
from app.models import MatchStats

class MatchConverter(object):
    def __init__(self):
        pass

    def from_database_matchstats(self, playername):
        return MatchStats.query.filter(MatchStats.playername == playername).\
                order_by(desc(MatchStats.utcStartSeconds)).limit(20).all()

    def from_database_squad_match(self, playername):
        sub = MatchStats.query.with_entities(MatchStats.id, MatchStats.matchID, func.count(MatchStats.matchID).label("count_id") ).group_by(MatchStats.matchID).having((func.count(MatchStats.matchID) > 1)).subquery()
        q = db.session.query(MatchStats.matchID, sub.c.count_id, MatchStats.playername).join(sub, MatchStats.matchID == sub.c.matchID).filter(MatchStats.playername == playername).all()
        return [s[0] for s in q]

    def from_database_squad_details(self, matchID):
        return MatchStats.query.filter(MatchStats.matchID == matchID).all()

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


    def create_match_data(self, playername):
        squad_ids = self.from_database_squad_match(playername)
        q = self.from_database_matchstats(str(playername))
        return self.consolidate_stats(q, squad_ids)

    def consolidate_stats(self, query_results, squad_ids):
        self.match_list = []

        for m in range(0, len(query_results)):
            match_stats_dict = {}
            match_stats = vars(query_results[m])
            if '_sa_instance_state' in match_stats:
                del match_stats['_sa_instance_state']

            match_stats['matchDate'] = self.convert_epoch_time(match_stats['utcStartSeconds'])[0]
            match_stats['matchStart'] = self.convert_epoch_time(match_stats['utcStartSeconds'])[1]
            match_stats['matchEnd'] = self.convert_epoch_time(match_stats['utcEndSeconds'])[1]

            match_stats['duration'] = self.strfdelta(match_stats['duration']//1000,'{minutes}m: {seconds}s')

            match_stats['kdRatio'] = round(match_stats['kdRatio'], 2)
            match_stats['scorePerMinute'] = round(match_stats['scorePerMinute'], 2)
            seconds = match_stats['timePlayed']
            match_stats['timePlayed'] = self.strfdelta(seconds, "{minutes}m: {seconds}s")

            if match_stats['teamSurvivalTime'] == 0:
                match_stats['teamSurvivalTime'] = 'no data'
            else:
                survival_sec = match_stats['teamSurvivalTime'] // 1000
                match_stats['teamSurvivalTime'] = self.strfdelta(survival_sec, '{minutes}m: {seconds}s')

            match_stats['percentTimeMoving'] = round(match_stats['percentTimeMoving'])
            match_stats['distanceTraveled'] = self.convert_inches(match_stats['distanceTraveled'])
            if len(squad_ids):
                if match_stats['matchID'] in squad_ids:
                    match_stats['squad_match'] = True
                else:
                    match_stats['squad_match'] = False

            match_stats['downs'] =  int(match_stats['circle1']) +\
                int(match_stats['circle2']) +\
                int(match_stats['circle3']) +\
                int(match_stats['circle4']) +\
                int(match_stats['circle5']) +\
                int(match_stats['circle6']) +\
                int(match_stats['circle7'])
            self.match_list.append(match_stats)

        return self.match_list

    def create_squad_match_details(self, matchID):
        q = self.from_database_squad_details(matchID)

        return self.consolidate_stats(q, [])






