from app import app
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from app.utilities import Utilities
from app.db_queries import DbQuery

query = DbQuery()
utilities = Utilities()

class MatchConverter(object):
    def __init__(self):
        self.int_string = ['Week', 'Month', 'Year', 'Last-30-Matches', 'Last-50-Matches', 'Last-100-Matches']

    def create_match_data(self, playername):
        squad_ids = query.from_database_squad_match(playername)
        q = query.from_database_matchstats(str(playername))
        return self.consolidate_stats(q, squad_ids)

    def create_match_data_paginate(self, playername, page):
        squad_ids = query.from_database_squad_match(playername)
        q = query.from_database_matchstats_paginate(str(playername), int(page)).items
        return self.consolidate_stats(q, squad_ids)

    def consolidate_stats(self, query_results, squad_ids):
        self.match_list = []

        for m in range(0, len(query_results)):
            match_stats_dict = {}
            match_stats = vars(query_results[m])
            if '_sa_instance_state' in match_stats:
                del match_stats['_sa_instance_state']

            match_stats['matchDate'] = utilities.convert_epoch_time(match_stats['utcStartSeconds'])[0]
            match_stats['matchStart'] = utilities.convert_epoch_time(match_stats['utcStartSeconds'])[1]
            match_stats['matchEnd'] = utilities.convert_epoch_time(match_stats['utcEndSeconds'])[1]

            match_stats['duration'] = utilities.strfdelta(match_stats['duration']//1000,'{minutes}m: {seconds}s')

            match_stats['kdRatio'] = round(match_stats['kdRatio'], 2)
            match_stats['scorePerMinute'] = round(match_stats['scorePerMinute'], 2)
            seconds = match_stats['timePlayed']
            match_stats['timePlayed'] = utilities.strfdelta(seconds, "{minutes}m: {seconds}s")

            if match_stats['teamSurvivalTime'] == 0:
                match_stats['teamSurvivalTime'] = 'no data'
            else:
                survival_sec = match_stats['teamSurvivalTime'] // 1000
                match_stats['teamSurvivalTime'] = utilities.strfdelta(survival_sec, '{minutes}m: {seconds}s')

            match_stats['percentTimeMoving'] = round(match_stats['percentTimeMoving'])
            match_stats['distanceTraveled'] = utilities.convert_inches(match_stats['distanceTraveled'])
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
        q = query.from_database_squad_details(matchID)

        return self.consolidate_stats(q, [])

