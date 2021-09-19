from app import app
from app.utilities import Utilities

utilities = Utilities()

class PropFirst(object):
    def __init__(self):
        self.real_data = {}
        self.real_data['contribution_stats'] = {'kills': 'contribution_kills', 'downs': 'contribution_downs'}
        self.real_data['prime_stats'] = ['teamPlacement_noSum', 'kdRatio_noSum', 'kills', 'downs', 'deaths', 'score', 'damageDone', 'damageTaken']
        self.real_data['side_stats'] = ['game_count', 'percentTimeMoving_game', 'revives', 'shopping', 'boxesOpen', 'headshots', 'pickupTablet', 'distanceTraveled', 'timePlayed', 'contribution_downs', 'contribution_kills', 'contribution_damageDone', 'contribution_damageTaken', 'contribution_objectiveReviver',
                'contribution_deaths', 'contribution_distanceTraveled']

        self.real_data['display_name'] = {'teamPlacement_noSum': 'Placement', 'kdRatio_noSum': 'KD', 'kills': 'Kills', 'downs': 'Downs', 'deaths': 'Deaths',
                             'score': 'Score', 'damageDone': 'Damage Done', 'damageTaken': 'Damage Taken', 'game_count': 'Games',
                             'percentTimeMoving_game': '%Moving/Game', 'revives': 'Revives', 'shopping': 'Shopped', 'boxesOpen': 'Cache Open',
                             'headshots': 'Headshots', 'pickupTablet': 'Contracts', 'distanceTraveled': 'Distance', 'timePlayed': 'Playtime',
                             'contribution_downs': 'Downs Team Contribution',
                             'contribution_kills': 'Kills Team Contribution',
                             'contribution_deaths': 'Deaths Team Contribution',
                             'contribution_damageDone': 'Damage Done Team Contribution',
                             'contribution_damageTaken': 'Damage Taken Team Contribution',
                             'contribution_objectiveReviver': 'Revives Team Contribution',
                             'contribution_distanceTraveled': 'Distance Team Contribution',}

        self.real_data['format_stats'] = {'big_num': [5,6,7], 'distance': [15], 'time':[16]}


        #PERFORMANCE
        self.perf_data = {}
        self.perf_data['prime_stats'] = ['kills_hour', 'downs_hour', 'deaths_hour', 'score_hour', 'damageDone_hour', 'damageTaken_hour']
        self.perf_data['side_stats'] = ['revives_hour', 'shopping_hour', 'boxesOpen_hour', 'headshots_hour', 'pickupTablet_hour', 'distanceTraveled_hour']

        self.perf_data['display_name'] = {'kills_hour': 'Kills/h', 'downs_hour': 'Downs/h', 'deaths_hour': 'Deaths/h', 'score_hour': 'Score/h', 'damageDone_hour': 'Damage Done/h',
                                          'damageTaken_hour': 'Damage Taken/h', 'revives_hour': 'Revives/h', 'shopping_hour': 'Shopped/h', 'boxesOpen_hour': 'Cache Open/h',
                                          'headshots_hour': 'Headshots/h', 'pickupTablet_hour': 'Contracts/h', 'distanceTraveled_hour': 'Distance/h'}
        self.perf_data['format_stats'] = {'big_num': [3,4,5], 'distance': [11], 'time': [] }


        self.colors = ["#052f5f","#c81d25","#06a77d","#0d1821","#e2c044","#ff6618","#087e8b","#ed5156","#8d6a9f","#79b473"]
        self.reverse_sort = ['teamPlacement_noSum', 'deaths', 'damageTaken', 'deaths_hour', 'damageTaken_hour']


    def convert_data_from_list(self, data):
        reorder_data = []
        if not data:
            return []
        while len(data[len(data) - 1]) > 0:
            player_list = []
            for i in range(len(data)):
                player_list.append(data[i].pop())
            reorder_data.append(player_list)
        reorder_data.reverse()
        return reorder_data


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

    def reorganize_batch(self, player_list_list, data, format=True, invert=True, sort=True):
        data_list = []
        for d in player_list_list:
            data_list.append(self.reorganize(d, data, format, invert, sort))
        return data_list

    def reorganize(self, player_list, data, format=True, invert=True, sort=True):
        prop_list = []
        prime_stats = [(stat, True) for stat in data['prime_stats']]
        side_stats = [(stat, False) for stat in data['side_stats']]

        stats = prime_stats + side_stats

        if invert:
            for p in player_list:
                p['inter'] = self.rows_to_columns(p['inter'])
                p['ticks'] = self.rows_to_columns(p['ticks'])

        for prop in stats:
            player_index = []
            for p in range(0, len( player_list )):
                player_props = {}
                player_props['display_prop_name'] = data['display_name'][prop[0]]
                player_props['prop_name'] = prop[0]
                player_props['chart_true'] = prop[1]
                player_props['inter_start'] = player_list[p]['inter_start']
                player_props['inter_end'] = player_list[p]['inter_end']
                player_props['playername'] = player_list[p]['playername']
                player_props['interval_count'] = player_list[p]['interval_count']
                player_props['inter'] = player_list[p]['inter'][prop[0]]
                player_props['ticks'] = player_list[p]['ticks'][prop[0]]
                player_props['ticks_length'] = self.max_ticks(player_list)
                player_props['colors'] = self.colors[p]

                player_index.append(player_props)

            prop_list.append(player_index)

        if sort:
            prop_list = self.sort_properties(prop_list)

        if format:
            prop_list = self.format_data(prop_list, data['format_stats'])

        return prop_list

    def max_ticks(self, player_list):
        max_tick_length = max([tick_length['ticks_length'] for tick_length in player_list])
        return max_tick_length

    def sort_properties(self, prop_list):
        for prop in prop_list:
            if prop[0]['prop_name'] in self.reverse_sort:
                prop.sort(key=lambda x: x['inter'][0])
                prop = self.resort_no_data(prop, True)

            else:
                prop.sort(key=lambda x: x['inter'][0], reverse=True)
                prop = self.resort_no_data(prop, False)

        return prop_list

    def resort_no_data(self, sorted_prop, flag):
        storage = []
        pl = 0
        length = len(sorted_prop)
        while pl < length:
            p = sorted_prop[pl]['inter'][0]
            if p == 0.0 or p == 0 or p == "0" or p == "0.0":
                sorted_prop[pl]['inter'][0] = '---'
                storage.append(sorted_prop[pl])
            pl += 1

        for item in storage:
            sorted_prop.pop(sorted_prop.index(item))

        for item in storage:
            sorted_prop.append(item)

        return sorted_prop

    def format_data(self, prop_list, formats):
        for i in formats['big_num']:
            for player in range(0, len(prop_list[i])):
                prop_len = len(prop_list[i][player]['inter'])
                if prop_len > 2:
                    prop_len = 2
                for p in range(0, prop_len):
                    prop_list[i][player]['inter'][p] = utilities.convert_scores(prop_list[i][player]['inter'][p])

        for i in formats['time']:
            for player in range(0, len(prop_list[i])):
                prop_len = len(prop_list[i][player]['inter'])
                if prop_len > 2:
                    prop_len = 2
                for p in range(0, prop_len):
                    prop_list[i][player]['inter'][p] = utilities.strfdelta(prop_list[i][player]['inter'][p], "{hours}:{minutes}")

        for i in formats['distance']:
            for player in range(0, len(prop_list[i])):
                prop_len = len(prop_list[i][player]['inter'])
                if prop_len > 2:
                    prop_len = 2
                for p in range(0, prop_len):
                    prop_list[i][player]['inter'][p] = utilities.convert_inches(prop_list[i][player]['inter'][p])

        return prop_list



