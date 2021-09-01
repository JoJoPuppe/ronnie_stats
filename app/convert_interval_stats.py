from app import app
from collections import defaultdict
from app.utilities import Utilities
from app.db_queries import DbQuery
from app.timings import Timings
import math

query = DbQuery()
utilities = Utilities()

class IntervalConverter(object):
    def __init__(self):
        self.int_string = ['Week', 'Month', 'Year', 'Last-30-Matches', 'Last-50-Matches', 'Last-100-Matches', 'Day', 'Last-7-Days']
        self.zero_stat = self.get_zero_stats()


    def add_percent_diff(self, sum_list):
        invert_percent_stats = ['teamPlacement_noSum', 'deaths', 'damageTaken']
        if len(sum_list) < 2:
            return sum_list

        percent_diff = {}
        for k, v in sum_list[0].items():
            if sum_list[0][k] == 0 or sum_list[1][k] == 0:
                percent_diff[k] = 0
            else:
                percent_diff[k] = round(100 - (100 / sum_list[0][k] * sum_list[1][k]))
            if k in invert_percent_stats:
                percent_diff[k] *= -1

        return percent_diff


    def get_ticklist(self, interval_list,  interval_timings, interval):
        int_timing = Timings()
        if interval == int_timing.int_string[0] or interval == int_timing.int_string[7]:
            return self.get_interval_list(interval_list[0], interval_timings[1], int_timing.day_interval, int_timing.week_day_count)
        if interval == int_timing.int_string[6]:
            return self.get_interval_list(interval_list[0], interval_timings[1], int_timing.day_interval, 1)
        if interval == int_timing.int_string[1]:
            days_of_month = int_timing.get_days_of_month(interval_timings[1])
            return self.get_interval_list(interval_list[0], interval_timings[1], int_timing.day_interval, days_of_month)
        if interval == int_timing.int_string[2]:
            return self.get_interval_list(interval_list[0], interval_timings[1], int_timing.week_interval, 52)


    def get_time_stats(self, playername, interval, interval_diff, team=False):
        int_timings = Timings()

        if team:
            print(team)

        interval_seconds = int_timings.get_seconds_of_interval(interval, interval_diff)

        time_interval_stats_dict = {}

        interval_timings = int_timings.interval_timings(interval, interval_diff)

        print(interval_timings)
        q = query.from_database_time_stats(playername, interval_timings[0], interval_timings[2])


        interval_list = self.get_interval_list(q, interval_timings[0], interval_seconds, 2)
        interval_list = interval_list[::-1]


        interval_sum_list = []
        for i in interval_list:
            interval_sum = self.sum_stats(i)
            interval_average = self.average_sum_data(interval_sum)
            interval_sum_list.append(interval_average)

        tick_list = self.get_ticklist(interval_list, interval_timings, interval)

        percent_diff_dict = self.add_percent_diff(interval_sum_list)

        if interval == int_timings.int_string[6]:
            ticks = []
            for tick in tick_list[0]:
                ticks.append(self.average_sum_data(self.sum_stats([tick])))
        else:
            ticks = []
            for tick in tick_list:
                ticks.append(self.average_sum_data(self.sum_stats(tick)))

        interval_sum_list.append(percent_diff_dict)

        #ticks = self.aggregate_stats(ticks)

        time_interval_stats_dict['inter_start'] = utilities.convert_epoch_time(interval_timings[1])
        time_interval_stats_dict['inter_end'] = utilities.convert_epoch_time(interval_timings[2])
        time_interval_stats_dict['inter'] = interval_sum_list
        time_interval_stats_dict['ticks'] = ticks
        time_interval_stats_dict['ticks_length'] = len(ticks)
        time_interval_stats_dict['playername'] = playername

        return time_interval_stats_dict

    def get_team_matches(self, team):
        #team = ['dlt_orko', 'neuner_eisen', 'jojopuppe']
        team_data = query.from_database_team_matches(team)
        match_list = self.clean_interval_list(team_data)
        sep_names = []
        for name in team:
            name_list = []
            for match in match_list:
               if match['playername'] == name:
                   name_list.append(match)

            player_matches = self.setup_match_count_stats(name, name_list)
            sep_names.append(player_matches)

        return sep_names


    def get_match_count_stats(self, playername, interval):
        count = {self.int_string[3]: 30, self.int_string[4]: 50, self.int_string[5]: 100}

        interval_count = count[interval]

        q = query.from_database_count_stats(playername, interval_count)

        match_list = self.clean_interval_list(q)

        return self.setup_match_count_stats(playername, match_list)


    def setup_match_count_stats(self, playername, match_list):
        interval_sum_list = self.average_sum_data(self.sum_stats(match_list))

        #interval_sum_list = self.rows_to_columns([interval_sum_list])

        ticks = []
        for tick in match_list:
            ticks.append(self.average_sum_data(tick))

        #ticks = self.rows_to_columns(ticks)
        count_interval_stats_dict = {}
        count_interval_stats_dict['inter_start'] = utilities.convert_epoch_time(match_list[0]['utcStartSeconds'])
        count_interval_stats_dict['inter_end'] = utilities.convert_epoch_time(match_list[-1]['utcStartSeconds'])
        count_interval_stats_dict['inter'] = [interval_sum_list]
        count_interval_stats_dict['ticks'] = ticks
        count_interval_stats_dict['ticks_length'] = len(ticks)
        count_interval_stats_dict['playername'] = playername

        return count_interval_stats_dict


    def consolidate_interval_stats(self, playername, interval, interval_diff):
        if interval in [self.int_string[0], self.int_string[1], self.int_string[2], self.int_string[6], self.int_string[7]]:
            return self.get_time_stats(playername, interval, interval_diff)
        else:
            return self.get_match_count_stats(playername, interval)


    def aggregate_stats(self, stats):
        for k, v in stats[0].items():
            current_value = 0
            for match in stats:
                if isinstance(match[k], str) or k == "timestamp" or k == "id" or 'noSum' in k or 'hour' in k:
                    continue
                else:
                    match[k] += current_value
                    current_value = match[k]

        return stats


    def average_sum_data(self, sum_stats):
        try:
            gc = sum_stats['game_count']
        except:
            sum_stats['game_count'] = 1

        if math.isnan(sum_stats['timePlayed']) or math.isnan(sum_stats['game_count']):
            return sum_stats

        per_hour_stats = ['score', 'kills', 'deaths', 'damageDone', 'damageTaken', 'distanceTraveled', 'revives', 'shopping', 'boxesOpen',
                          'pickupTablet', 'totalXp', 'downs', 'headshots']

        average_stats = ['teamPlacement', 'percentTimeMoving']

        hours = sum_stats['timePlayed'] / 60 / 60 if sum_stats['timePlayed'] != 0 else 1
        gamecount = sum_stats['game_count'] if sum_stats['game_count'] != 0 else 1

        sum_stats['downs'] =  sum_stats['circle1'] +\
            sum_stats['circle2'] +\
            sum_stats['circle3'] +\
            sum_stats['circle4'] +\
            sum_stats['circle5'] +\
            sum_stats['circle6'] +\
            sum_stats['circle7']

        for stat in per_hour_stats:
            if math.isnan(sum_stats[stat]):
                continue
            stat_hour = stat + "_hour"
            sum_stats[stat_hour] = round(sum_stats[stat] / hours, 2)

        sum_stats['teamPlacement_noSum'] = round(sum_stats['teamPlacement'] / gamecount, 2)
        sum_stats['kdRatio_noSum'] = round(sum_stats['kills'] / sum_stats['deaths'], 2) if sum_stats['deaths'] != 0 else 0
        sum_stats['percentTimeMoving_game'] = round(sum_stats['percentTimeMoving'] / gamecount)

        return sum_stats

    def get_zero_stats(self):
        first_match = query.from_database_first_match()

        if not isinstance(first_match, dict):
            first_match = vars(first_match)
            if '_sa_instance_state' in first_match:
                del first_match['_sa_instance_state']

        for k, v in first_match.items():
            if isinstance(first_match[k], str) or k == "timestamp" or k == "id":
                continue
            if 'circle' in k:
                first_match[k] = 0
            else:
                first_match[k] = float('NaN')

        return first_match


    def clean_interval_list(self, match_list):
        n_match_list = []
        for match in match_list:
            if not isinstance(match, dict):
                match = vars(match)
                if '_sa_instance_state' in match:
                    del match['_sa_instance_state']

            n_match_list.append(match)

        return n_match_list


    def get_interval_list(self, match_list, start_timestamp, interval, max_cnt):
        interval_list = []
        cnt = 0
        while cnt < max_cnt:
            keep_interval = []
            check_next = []
            has_value = False
            zero_base_stats = self.zero_stat

            if zero_base_stats == None:
                return None

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
        name_stats = match_query[0]
        sum_dict = defaultdict(lambda: 0)
        for k, v in name_stats.items():
            if isinstance(name_stats[k], str) or k == 'timestamp' or k == 'id' or math.isnan(name_stats[k]):
                continue

            for m in range(0, len(match_query)):
                match_stats = match_query[m]

                sum_dict[k] += match_stats[k]

            if sum_dict[k] == 0 and 'circle' not in k:
                sum_dict[k] = 0

        sum_dict['game_count'] = int(len(match_query))

        return sum_dict









