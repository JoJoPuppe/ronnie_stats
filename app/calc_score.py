class ScoreCalc(object):
    def __init__(self, data):
        self.dataset = data
        self.weights = {'kdRatio_noSum': [400, 'KD'],
                        'kills_hour': [ 50, 'Kills/h' ],
                        'downs_hour': [ 30, 'Downs/h' ],
                        'score_hour': [0.05, 'Score/h'],
                        'teamPlacement_noSum': [1, 'Avg. Placement'],
                        'damageDone_hour': [0.1, 'Damage Done/h'],
                        'revives_hour': [200, 'Revives/h'],
                        'headshots_hour': [150, 'Headshots/h'],
                        'shopping_hour': [50, 'Shopping/h'],
                        'boxesOpen_hour': [25, 'Caches/h'],
                        'pickupTablet_hour': [75, 'Contracts/h'],
                        'distanceTraveled_hour': [0.0001, 'Distance/h']}

    def interval_and_tick_score(self):
        interval_score = self.calculate_skill(self.dataset['inter'])
        tick_score = []
        for tick in self.dataset['ticks']:
            tick_score.append(self.calculate_skill([tick]))

        badges = self.calc_badges()

        return { 'interval_score': interval_score, 'tick_score': tick_score, 'badges': badges }


    def calculate_skill(self, data):
        score_dict = {}
        for k, v in self.weights.items():
            score_dict[k] = [round(data[0][k] * self.weights[k][0], 1), self.weights[k][1]]

        if score_dict['teamPlacement_noSum'][0] != 0:
                score_dict['teamPlacement_noSum'][0] = round((150 - score_dict['teamPlacement_noSum'][0]) / 150 * 500, 1)

        score_dict= sorted(score_dict.items(), key=lambda x: x[1][0], reverse=True)

        total = round(sum([x[1][0] for x in score_dict]))
        score_dict.append(('SUM',[total, 'TOTAL SP']))

        return score_dict

    def calc_badges(self):
        inter = self.dataset['inter']
        badges = []
        badge = 0

        #placement
        #caches
        #shopping
        #headshots


        if inter[0]['kills'] > 100:
            badge = ['Terminator', 'Kill more than 100 other players']
        elif inter[0]['kills'] > 50:
            badge = ['Monster', 'Kill more than 50 other players']
        elif inter[0]['kills'] > 25:
            badge = ['Killer', 'Kill more than 25 other players']
        if badge != 0:
            badges.append(badge)
            badge = 0

        if inter[0]['deaths'] > 100:
            badge = ['DIE DIE DIE', 'Die more than 100 times']
        elif inter[0]['deaths'] > 50:
            badge = ['The Ripper likes you', 'Die more than 50 times']
        elif inter[0]['deaths'] > 25:
            badge = ['RIP', 'Die more than 25 times']
        if badge != 0:
            badges.append(badge)
            badge = 0

        if inter[0]['distanceTraveled'] > 11811000:
            badge = ['Forrest Gump', 'Travel more than 300km']
        elif inter[0]['distanceTraveled'] > 7874000:
            badge = ['Usain Bolt', 'Travel more than 200km']
        elif inter[0]['distanceTraveled'] > 3937000:
            badge = ['Traveller', 'Travel more than 100km']
        if badge != 0:
            badges.append(badge)
            badge = 0

        if inter[0]['kdRatio_noSum'] > 2.0:
            badge = ['Destroyer', 'KD of more than 2.0']
        elif inter[0]['kdRatio_noSum'] > 1.5:
            badge = ['Better than others', 'KD of more than 1.5']
        elif inter[0]['kdRatio_noSum'] > 1.0:
            badge = ['Even', 'KD of more than 1.0']
        elif inter[0]['kdRatio_noSum'] > 0.8:
            badge = ['Nerfgun', 'KD of more than 0.8']
        if badge != 0:
            badges.append(badge)
            badge = 0

        return badges

