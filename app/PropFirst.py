class PropFirst(object):
    def __init__(self):
        self.prime_stats = ['teamPlacement_noSum', 'kdRatio_noSum', 'kills', 'downs', 'deaths', 'score', 'damageDone', 'damageTaken']
        self.side_stats = ['game_count', 'percentTimeMoving_game', 'revives', 'shopping', 'boxesOpen', 'headshots', 'pickupTablet']
        
        self.display_name = {'teamPlacement_noSum': 'Placement', 'kdRatio_noSum': 'KD', 'kills': 'Kills', 'downs': 'Downs', 'deaths': 'Deaths',
                             'score': 'Score', 'damageDone': 'Damage Done', 'damageTaken': 'Damage Taken', 'game_count': 'Games', 
                             'percentTimeMoving_game': '%Moving/Game', 'revives': 'Revives', 'shopping': 'Shopped', 'boxesOpen': 'Cache Open',
                             'headshots': 'Headshots', 'pickupTablet': 'Contracts'}

        self.colors = ['#ef476f','#ffd166','#06d6a0','#118ab2','#073b4c']
        self.reverse_sort = ['teamPlacement_noSum', 'deaths', 'damageTaken']


    def reorganize(self, player_list):
        prop_list = []
        prime_stats = [(stat, True) for stat in self.prime_stats]
        side_stats = [(stat, False) for stat in self.side_stats]

        stats = prime_stats + side_stats

        for prop in stats:
            player_index = []
            for p in range(0, len( player_list )):
                player_props = {}
                player_props['display_prop_name'] = self.display_name[prop[0]]
                player_props['prop_name'] = prop[0]
                player_props['chart_true'] = prop[1]
                player_props['inter_start'] = player_list[p]['inter_start']
                player_props['inter_end'] = player_list[p]['inter_end']
                player_props['playername'] = player_list[p]['playername']
                player_props['inter'] = player_list[p]['inter'][prop[0]]
                player_props['ticks'] = player_list[p]['ticks'][prop[0]]
                player_props['colors'] = self.colors[p]

                player_index.append(player_props)

            prop_list.append(player_index)

        prop_list = self.sort_properties(prop_list)

        return prop_list

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
