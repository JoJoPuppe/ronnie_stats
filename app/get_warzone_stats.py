import requests
import time
import simplejson as ss

class WarzoneStats(object):
    def __init__(self, playername):
        self.playername = playername
        self.GAMEMODES = {'SOLO': 'br_87', 'TRIO': 'br_25', 'QUAD': 'br_89'}
        self.Stats_URL = 'https://my.callofduty.com/api/papi-client/stats/cod/v1/title/mw/platform/psn/gamer/' + self.playername + '/profile/type/wz'
        self.player_stats = self.collect_data()

    def request_playerdata(self, url):
        r = requests.get(self.Stats_URL)
        status = r.status_code
        cnt = 0
        while cnt < 5 or status != 200:
            print("no data received - waiting 5sec")
            time.sleep(5)
            cnt += 1

        if status != 200:
            print(f"can not get {self.playername} data")
        else:
            self.data = r.json()['data']


    def collect_data(self):
        self.request_playerdata(self.Stats_URL)

        collected_data = {}

        if self.data == None:
            return None

        collected_data["br_lifetime"] = self.data['lifetime']['mode']['br']['properties']

        collected_data["br_lifetime"]['name'] = self.data['username']
        collected_data['br_lifetime']['level'] = self.data['level']

        br_weekly = {}
        for k, v in self.GAMEMODES.items():
            if v in self.data['weekly']['mode']:
                br_weekly[k] = self.data['weekly']['mode'][v]
        collected_data["br_weekly"] = br_weekly

        validated_data = self.validate_data(collected_data)

        return validated_data


    def validate_data(self, raw_data):
        LIFE_TIME_STATS_KEYS = ['name', 'level', 'wins', 'kills', 'kdRatio', 'downs', 'deaths',
                                'topTwentyFive', 'topTen', 'topFive', 'contracts', 'score',
                                'scorePerMinute', 'timePlayed', 'gamesPlayed']

        WEEKLY_STATS_KEYS = ['wins', 'kills', 'headshots', 'kdRatio', 'deaths', 'killsPerGame',
                             'score', 'scorePerMinute', 'timePlayed', 'objectiveTeamWiped',
                             'objectiveLastStandKill', 'distanceTraveled', 'objectiveBrDownEnemyCircle1', 'objectiveBrDownEnemyCircle2', 'objectiveBrDownEnemyCircle3',
                             'objectiveBrDownEnemyCircle4', 'objectiveBrDownEnemyCircle5',
                             'objectiveBrMissionPickupTablet', 'objectiveReviver',
                             'objectiveBrCacheOpen', 'objectiveBrKioskBuy', 'matchesPlayed',
                             'damageDone', 'damageTaken']

        for stat in LIFE_TIME_STATS_KEYS:
            if stat not in raw_data['br_lifetime']:
                raw_data['br_lifetime'][stat] = 0

        for stat in WEEKLY_STATS_KEYS:
            for k, v in raw_data['br_weekly'].items():
                if stat not in raw_data['br_weekly'][k]['properties']:
                    raw_data['br_weekly'][k]['properties'][stat] = 0

        return raw_data
