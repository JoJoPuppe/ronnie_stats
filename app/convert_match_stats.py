from app import app, db
from datetime import datetime, timezone, timedelta
from datetime import timedelta
from sqlalchemy import func, desc
from app.models import MatchStats
from collections import defaultdict
import time

class MatchConverter(object):
    def __init__(self):
        self.week_interval = 604800
        self.day_interval = 86400

    def from_database_matchstats(self, playername):
        return MatchStats.query.filter(MatchStats.playername == playername).\
                order_by(desc(MatchStats.utcStartSeconds)).limit(20).all()

    def from_database_squad_match(self, playername):
        sub = MatchStats.query.with_entities(MatchStats.id, MatchStats.matchID, func.count(MatchStats.matchID).label("count_id") ).group_by(MatchStats.matchID).having((func.count(MatchStats.matchID) > 1)).subquery()
        q = db.session.query(MatchStats.matchID, sub.c.count_id, MatchStats.playername).join(sub, MatchStats.matchID == sub.c.matchID).filter(MatchStats.playername == playername).all()
        return [s[0] for s in q]

    def from_database_squad_details(self, matchID):
        return MatchStats.query.filter(MatchStats.matchID == matchID).all()

    def from_database_time_stats(self, playername, start_time, end_time):
        return MatchStats.query.filter(MatchStats.playername == playername, MatchStats.utcStartSeconds > start_time, MatchStats.utcStartSeconds < end_time).order_by(MatchStats.utcStartSeconds).all()

    def strfdelta(self, sec, fmt):
        d = {}
        d["minutes"], d["seconds"] = divmod(sec, 60)
        d["hours"], d["minutes"] = divmod(d["minutes"], 60)
        return fmt.format(**d)


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



    def get_week_break(self, timestamp):
        #MON 6AM
        DAY_BREAK = 6

        current_date = datetime.fromtimestamp(timestamp)
        daily_breakpoint = timedelta(seconds=DAY_BREAK * 3600)
        daily_diff = current_date - daily_breakpoint
        current_weekday = daily_diff.weekday()
        seconds = (daily_diff.hour * 60 * 60) + (daily_diff.minute * 60) + daily_diff.second
        daily_diff = timedelta(seconds=seconds)
        days_since_mon = timedelta(days=current_weekday)
        break_time = current_date - days_since_mon - daily_diff

        return int(break_time.timestamp())


    def weekly_timings(self, week_diff):
        weekly_stats_dict = {}

        time_now = int(time.time()) - (week_diff * self.week_interval)
        current_week_start_ts = self.get_week_break(time_now)
        last_week_start = time_now - self.week_interval
        last_week_start_ts = self.get_week_break(last_week_start)
        end_time_timestamp = time_now + self.week_interval
        current_week_end_ts = self.get_week_break(end_time_timestamp)

        return [last_week_start_ts, current_week_start_ts, current_week_end_ts]


    def rows_to_columns(self, game_data):
        stats_dict = {}
        for k, v in game_data[0].items():
            property_list = []
            for player in game_data:
                property_list.append(player[k])

            stats_dict[k] = property_list

        return stats_dict


    def consolidate_interval_stats(self, playername, week_diff):
        weekly_stats_dict = {}

        weekly_timings = self.weekly_timings(week_diff)
        q = self.from_database_time_stats(playername, weekly_timings[0], weekly_timings[2])

        week_list = self.get_interval_list(q, weekly_timings[0], self.week_interval, 2)

        weeks = []
        for week in week_list:
            weeks.append(self.average_sum_data(self.sum_stats(week)))

        day_list = self.get_interval_list(week_list[1], weekly_timings[1], self.day_interval, 7)


        days = []
        for day in day_list:
            days.append(self.average_sum_data(self.sum_stats(day)))

        weeks = self.rows_to_columns(weeks)

        days = self.rows_to_columns(days)

        weekly_stats_dict['week_start'] = self.convert_epoch_time(weekly_timings[1])
        weekly_stats_dict['week_end'] = self.convert_epoch_time(weekly_timings[2])
        weekly_stats_dict['week'] = weeks
        weekly_stats_dict['days'] = days
        weekly_stats_dict['playername'] = playername

        return weekly_stats_dict


    def average_sum_data(self, sum_stats):
        hours = sum_stats['timePlayed'] / 60 / 60 if sum_stats['timePlayed'] != 0 else 1
        gamecount = sum_stats['game_count']
        sum_stats['kdRatio'] = round(sum_stats['kills'] / sum_stats['deaths'], 2) if sum_stats['deaths'] != 0 else 0
        sum_stats['score_hour'] = round(sum_stats['score'] / hours)
        sum_stats['kills_hour'] = round(sum_stats['kills'] / hours)
        sum_stats['deaths_hour'] = round(sum_stats['deaths'] / hours)
        sum_stats['damageDone_hour'] = round(sum_stats['damageDone'] / hours)
        sum_stats['damageTaken_hour'] = round(sum_stats['damageTaken'] / hours)
        sum_stats['percentTimeMoving_game'] = round(sum_stats['percentTimeMoving'] / gamecount) if gamecount != 0 else 1

        sum_stats['distanceTraveled_hour'] = self.convert_inches(round(sum_stats['distanceTraveled'] / hours))
        sum_stats['distanceTraveled'] = self.convert_inches(sum_stats['distanceTraveled'])

        sum_stats['revives_hour'] = round(sum_stats['revives'] / hours)
        sum_stats['shopping_hour'] = round(sum_stats['shopping'] / hours)
        sum_stats['teamWipes_hour'] = round(sum_stats['teamWipes'] / hours)
        sum_stats['boxesOpen_hour'] = round(sum_stats['boxesOpen'] / hours)
        sum_stats['longestStreak_hour'] = round(sum_stats['longestStreak'] / hours)
        sum_stats['lastStandKills_hour'] = round(sum_stats['lastStandKills'] / hours)
        sum_stats['headshots_hour'] = round(sum_stats['headshots'] / hours)
        sum_stats['pickupTablet_hour'] = round(sum_stats['pickupTablet'] / hours)
        sum_stats['xp_hour'] = round(sum_stats['totalXp'] / hours)
        sum_stats['timePlayed'] = self.strfdelta(sum_stats['timePlayed'], "{hours}h: {minutes}m")

        sum_stats['downs'] =  int(sum_stats['circle1']) +\
            int(sum_stats['circle2']) +\
            int(sum_stats['circle3']) +\
            int(sum_stats['circle4']) +\
            int(sum_stats['circle5']) +\
            int(sum_stats['circle6']) +\
            int(sum_stats['circle7'])

        sum_stats['downs_hour'] = round(sum_stats['downs'] / hours)

        return sum_stats


    def get_zero_stats(self, match_list):
        first_match = match_list[0]
        if not isinstance(first_match, dict):
            first_match = vars(first_match)
            if '_sa_instance_state' in first_match:
                del first_match['_sa_instance_state']

        for k, v in first_match.items():
            if isinstance(first_match[k], str) or k == "timestamp" or k == "id":
                continue
            first_match[k] = 0

        return first_match


    def get_interval_list(self, match_list, start_timestamp, interval, max_cnt):
        interval_list = []
        cnt = 0
        while cnt < max_cnt:
            keep_interval = []
            check_next = []
            has_value = False
            zero_base_stats = self.get_zero_stats(match_list)

            for match in match_list:
                if not isinstance(match, dict):
                    match = vars(match)
                    if '_sa_instance_state' in match:
                        del match['_sa_instance_state']

                start = start_timestamp + (cnt * interval)
                end = start_timestamp + interval + ( cnt * interval )
                if start <= match['utcStartSeconds'] < end:
                    keep_interval.append(match)
                    has_value = True
                else:
                    check_next.append(match)

            cnt += 1
            if has_value == True:
                interval_list.append(keep_interval)
            else:
                interval_list.append([zero_base_stats])

            match_list = check_next

        return interval_list


    def sum_stats(self, match_query):
        if not match_query:
            return 0

        name_stats = match_query[0]
        sum_dict = defaultdict(lambda: 0)
        for k, v in name_stats.items():
            if isinstance(name_stats[k], str) or k == 'timestamp' or k == 'id':
                continue

            for m in range(0, len(match_query)):
                match_stats = match_query[m]

                sum_dict[k] += match_stats[k]

        sum_dict['game_count'] = len(match_query)

        return sum_dict









