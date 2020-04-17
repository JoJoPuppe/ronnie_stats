import requests
import time
import simplejson as ss
import re
import os

class WarzoneStats(object):
    def __init__(self, playername):
        self.email = 'marcusloeper@gmx.de'
        self.pw = '01hzkdfbwx389f'
        self.playername = playername
        self.GAMEMODES = {'SOLO': 'br_87', 'TRIO': 'br_25', 'QUAD': 'br_89'}
        self.Xsrf_token_URL = 'https://profile.callofduty.com/cod/login'
        self.Auth_URL = 'https://profile.callofduty.com/do_login?new_SiteId=cod'
        self.Stats_URL = 'https://my.callofduty.com/api/papi-client/stats/cod/v1/title/mw/platform/psn/gamer/' +self.playername + '/profile/type/wz'
        self.Games_URL = 'https://my.callofduty.com/api/papi-client/crm/cod/v2/title/mw/platform/psn/gamer/'+ self.playername +'/matches/wz/start/0/end/0/details'
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.token_file_name = 'auth.token'

    def load_all_cookies(self):
        cookie_file = os.path.join(self.base_path, 'auth_cookies.txt')
        cookie_dict = {}
        try:
            with open(cookie_file, "r") as f:
                for line in f.readlines():
                    line = line.rstrip('\n')
                    cookie_pair = line.split(",")
                    cookie_dict[cookie_pair[0]] = cookie_pair[1]

        except IOError:
            print("File does not exist")
            cookie_dict = False

        return cookie_dict


    def save_cookies(self, cookies):
        cookies_file = os.path.join(self.base_path, 'auth_cookies.txt')
        with open(cookies_file, 'w+') as f:
            for k, v in cookies.items():
                line = k + "," + v + "\n"
                f.write(line)

    def obtain_new_token(self):

        s = requests.Session()

        r = s.get(self.Xsrf_token_URL)
        xsrf_token = r.cookies['XSRF-TOKEN']
        payload = {'username': self.email, 'password': self.pw,
                   'remember_me':'true', '_csrf': xsrf_token}

        r = s.post(self.Auth_URL, data=payload)
        r = s.get(self.Stats_URL)

        self.save_cookies(s.cookies)


    def request_player_data(self, cnt=5):

        cookies = self.load_all_cookies()
        if cnt != 0:
            if cookies:
                cookies = {'rtkn': cookies['rtkn'], 'atkn': cookies['atkn'],
                           'ACT_SSO_COOKIE': cookies['ACT_SSO_COOKIE']}

                r = requests.get(self.Stats_URL, cookies=cookies)
                response_string = r.content.decode("utf-8")
                error = re.search(r'error', response_string)
                if error == None:
                    return r.json()['data']
                else:
                    self.obtain_new_token()
                    cnt -= 1
                    self.request_player_data(cnt)
            else:
                self.obtain_new_token()
                cnt -= 1
                self.request_player_data(cnt)

        print("5 attempts. no succsess")


    def collect_player_data(self):

        player_data = self.request_player_data()

        collected_data = {}

        collected_data["br_lifetime"] = player_data['lifetime']['mode']['br']['properties']

        collected_data["br_lifetime"]['name'] = player_data['username']
        collected_data['br_lifetime']['level'] = player_data['level']

        br_weekly = {}
        for k, v in self.GAMEMODES.items():
            if v in player_data['weekly']['mode']:
                br_weekly[k] = player_data['weekly']['mode'][v]
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
