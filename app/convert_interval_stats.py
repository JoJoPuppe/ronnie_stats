from app import app
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from app.utilities import Utilities
from app.db_queries import DbQuery

import time
import math
import calendar

query = DbQuery()
utilities = Utilities()

class IntervalConverter(object):
    def __init__(self):
        self.day_interval = 86400
        self.week_interval = 604800
        self.year_interval = 31536000
        self.int_string = ['Week', 'Month', 'Year', 'Last-30-Matches', 'Last-50-Matches', 'Last-100-Matches']

    def get_interval_break(self, timestamp, interval):
        DAY_BREAK = 6

        def get_int_diff(daily_diff, interval):
            if interval == self.int_string[2]:
                current_year = daily_diff.year
                start_of_year = datetime(current_year, 1, 1)
                since_newyear = daily_diff - start_of_year
                return since_newyear.days
            if interval == self.int_string[0]:
                return daily_diff.weekday()
            if interval == self.int_string[1]:
                return daily_diff.day - 1
            else:
                return daily_diff.weekday()

        current_date = datetime.fromtimestamp(timestamp)

        daily_breakpoint = timedelta(seconds=DAY_BREAK * 3600)
        daily_diff = current_date - daily_breakpoint

        current_interval = get_int_diff(daily_diff, interval)

        seconds = (daily_diff.hour * 60 * 60) + (daily_diff.minute * 60) + daily_diff.second
        daily_diff = timedelta(seconds=seconds)
        diff_from_start_day = timedelta(days=current_interval)

        break_time = current_date - diff_from_start_day - daily_diff

        return int(break_time.timestamp())

    def get_seconds_of_interval(self, interval, multi):
        if interval == self.int_string[0]:
            return self.week_interval
        if interval == self.int_string[2]:
            return self.year_interval
        if interval == self.int_string[1]:
            ref_time = datetime.now()
            return calendar.monthrange(ref_time.year, ref_time.month - multi)[1] * self.day_interval

    def interval_timings(self, interval, multi):
        time_now = int(time.time())
        interval_seconds = self.get_seconds_of_interval(interval, multi)

        if interval == self.int_string[1]:
            start_time = datetime.now()
            month_span_seconds = 0
            for i in range(0, multi):
                month_span_seconds += calendar.monthrange(start_time.year, start_time.month - i)[1] * self.day_interval

            last_month_seconds = calendar.monthrange(start_time.year, start_time.month - multi - 1)[1] * self.day_interval

            multi_diff = time_now - month_span_seconds
            last_interval_start = multi_diff - last_month_seconds
            end_time_timestamp = multi_diff + last_month_seconds
        else:
            multi_diff = time_now - (multi * interval_seconds)
            last_interval_start = multi_diff - interval_seconds
            end_time_timestamp = multi_diff + interval_seconds

        current_interval_start_ts = self.get_interval_break(multi_diff, interval)
        last_interval_start_ts = self.get_interval_break(last_interval_start, interval)
        current_interval_end_ts = self.get_interval_break(end_time_timestamp, interval)

        return [last_interval_start_ts, current_interval_start_ts, current_interval_end_ts]


    def rows_to_columns(self, game_data):
        if game_data[0] == None:
            return game_data

        stats_dict = {}
        for k, v in game_data[0].items():
            property_list = []
            for player in game_data:
                property_list.append(player[k])

            stats_dict[k] = property_list

        return stats_dict

    def get_time_stats(self, playername, interval, interval_diff):

        interval_seconds = self.get_seconds_of_interval(interval, interval_diff)

        time_interval_stats_dict = {}

        interval_timings = self.interval_timings(interval, interval_diff)
        q = query.from_database_time_stats(playername, interval_timings[0], interval_timings[2])

        interval_list = self.get_interval_list(q, interval_timings[0], interval_seconds, 2)
        interval_list = interval_list[::-1]

        interval_sum_list = []
        for i in interval_list:
            interval_sum = self.sum_stats(i)
            interval_average = self.average_sum_data(interval_sum)
            interval_sum_list.append(interval_average)

        if interval == self.int_string[0]:
            tick_list = self.get_interval_list(interval_list[0], interval_timings[1], self.day_interval, 7)
        if interval == self.int_string[1]:
            ref_time = datetime.fromtimestamp(interval_timings[1])
            days_of_month = calendar.monthrange(ref_time.year, ref_time.month)[1]
            tick_list = self.get_interval_list(interval_list[0], interval_timings[1], self.day_interval, days_of_month)
        if interval == self.int_string[2]:
            tick_list = self.get_interval_list(interval_list[0], interval_timings[1], self.week_interval, 52)

        ticks = []
        for tick in tick_list:
            ticks.append(self.average_sum_data(self.sum_stats(tick)))

        interval_sum_list = self.rows_to_columns(interval_sum_list)
        ticks = self.aggregate_stats(ticks)
        ticks = self.rows_to_columns(ticks)

        time_interval_stats_dict['inter_start'] = utilities.convert_epoch_time(interval_timings[1])
        time_interval_stats_dict['inter_end'] = utilities.convert_epoch_time(interval_timings[2])
        time_interval_stats_dict['inter'] = interval_sum_list
        time_interval_stats_dict['ticks'] = ticks
        time_interval_stats_dict['playername'] = playername

        return time_interval_stats_dict

    def get_match_count_stats(self, playername, interval):
        count_interval_stats_dict = {}
        count = {self.int_string[3]: 30, self.int_string[4]: 50, self.int_string[5]: 100}

        interval_count = count[interval]

        q = query.from_database_count_stats(playername, interval_count)
        match_list = self.clean_interval_list(q)

        interval_sum_list = self.average_sum_data(self.sum_stats(match_list))

        interval_sum_list = self.rows_to_columns([interval_sum_list])

        ticks = []
        for tick in match_list:
            ticks.append(self.average_sum_data(tick))

        ticks = self.rows_to_columns(ticks)

        count_interval_stats_dict['inter_start'] = utilities.convert_epoch_time(match_list[0]['utcStartSeconds'])
        count_interval_stats_dict['inter_end'] = utilities.convert_epoch_time(match_list[-1]['utcStartSeconds'])
        count_interval_stats_dict['inter'] = interval_sum_list
        count_interval_stats_dict['ticks'] = ticks
        count_interval_stats_dict['playername'] = playername

        return count_interval_stats_dict


    def consolidate_interval_stats(self, playername, interval, interval_diff):

        if interval in [self.int_string[0], self.int_string[1], self.int_string[2]]:
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

        #if sum_stats['downs'] == 0:
        #    sum_stats['downs'] = float('NaN')

        for stat in per_hour_stats:
            if math.isnan(sum_stats[stat]):
                continue
            stat_hour = stat + "_hour"
            sum_stats[stat_hour] = round(sum_stats[stat] / hours, 1)

        sum_stats['teamPlacement_noSum'] = round(sum_stats['teamPlacement'] / gamecount, 1)
        sum_stats['kdRatio_noSum'] = round(sum_stats['kills'] / sum_stats['deaths'], 1) if sum_stats['deaths'] != 0 else 0
        sum_stats['percentTimeMoving_game'] = round(sum_stats['percentTimeMoving'] / gamecount)

        sum_stats['distanceTraveled_hour'] = utilities.convert_inches(round(sum_stats['distanceTraveled'] / hours))
        sum_stats['distanceTraveled'] = utilities.convert_inches(sum_stats['distanceTraveled'])

        sum_stats['timePlayed'] = utilities.strfdelta(sum_stats['timePlayed'], "{hours}h: {minutes}m")

        return sum_stats


    def get_zero_stats(self, match_list):
        if len(match_list) < 1:
            first_match = query.from_database_first_match()
        else:
            first_match = match_list[0]

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
            zero_base_stats = self.get_zero_stats(match_list)

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








