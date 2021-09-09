from datetime import datetime, timedelta
import calendar
import time

class Timings(object):
    def __init__(self):
        self.day_interval = 86400
        self.week_day_count = 7
        self.week_interval = 604800
        self.year_interval = 31536000
        self.int_string = ['Week', 'Month', 'Year', 'Last-30-Matches', 'Last-50-Matches', 'Last-100-Matches', 'Day', 'Last-7-Days']
        #self.zero_stat = self.get_zero_stats()

    def get_days_of_month(self, timestamp):
        ref_time = datetime.fromtimestamp(timestamp)
        return calendar.monthrange(ref_time.year, ref_time.month)[1]

    def get_interval_break(self, timestamp, interval):
        DAY_BREAK = 2

        if interval == self.int_string[7]:
            return timestamp

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
            if interval == self.int_string[6]:
                return 0
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
        if interval == self.int_string[6]:
            return self.day_interval;
        if interval == self.int_string[0] or interval == self.int_string[7]:
            return self.week_interval
        if interval == self.int_string[2]:
            return self.year_interval
        if interval == self.int_string[1]:
            ref_time = datetime.now()
            new_month = (ref_time.month - multi) % 13
            if new_month < 1:
                new_month = 12 - new_month

            return calendar.monthrange(ref_time.year, new_month)[1] * self.day_interval


    def interval_timings(self, interval, multi):
        time_now = int(time.time())
        interval_seconds = self.get_seconds_of_interval(interval, multi)

        if interval == self.int_string[1]:
            start_time = datetime.now()
            new_month = (start_time.month - multi - 1) % 13
            if new_month < 1:
                new_month = 12 - new_month
            month_span_seconds = 0
            for i in range(0, multi):
                for_month = (start_time.month - i) % 13
                if for_month < 1:
                    for_month = 12 - for_month

                month_span_seconds += calendar.monthrange(start_time.year, for_month)[1] * self.day_interval

            last_month_seconds = calendar.monthrange(start_time.year, new_month)[1] * self.day_interval

            multi_diff = time_now - month_span_seconds
            last_interval_start = multi_diff - last_month_seconds
            end_time_timestamp = multi_diff + last_month_seconds

        elif interval == self.int_string[7]:

            multi_diff = time_now - interval_seconds
            last_interval_start = multi_diff - interval_seconds
            end_time_timestamp = time_now
        else:
            multi_diff = time_now - (multi * interval_seconds)
            last_interval_start = multi_diff - interval_seconds
            end_time_timestamp = multi_diff + interval_seconds

        current_interval_start_ts = self.get_interval_break(multi_diff, interval)
        last_interval_start_ts = self.get_interval_break(last_interval_start, interval)
        current_interval_end_ts = self.get_interval_break(end_time_timestamp, interval)

        print(interval)

        utc_time = [current_interval_start_ts, last_interval_start_ts, current_interval_end_ts, multi_diff, last_interval_start, end_time_timestamp]
        for t in utc_time:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t)))

        return [last_interval_start_ts, current_interval_start_ts, current_interval_end_ts]


