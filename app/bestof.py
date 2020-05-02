import app
from app.convert_interval_stats import IntervalConverter
from app.calc_score import ScoreCalc
from stats_config import WARZONE_CONFIG

class Score(object):
    def __init__(self):
        self.time = {}

    def calc(self, interval, mi):
        NAMES = WARZONE_CONFIG['NAMES']
        score_list = []
        for name in NAMES:
            interval_data = IntervalConverter()
            interval_data = interval_data.consolidate_interval_stats(name, interval, int(mi))
            sc = ScoreCalc(interval_data)
            self.time['inter_start'] = interval_data['inter_start']
            self.time['inter_end'] = interval_data['inter_end']
            scores = sc.interval_and_tick_score()
            player_score_dict = {'scores': scores, 'playername': interval_data['playername'], 'inter_start': interval_data['inter_start'],
                                 'inter_end': interval_data['inter_end']}
            if scores['interval_score'][12][1][0] > 0:
                score_list.append(player_score_dict)

        score_list = sorted(score_list, key=lambda x: x['scores']['interval_score'][12][1][0], reverse=True)

        return score_list


