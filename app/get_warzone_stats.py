import requests
import simplejson as ss

class WarzoneStats(object):
    def __init__(self, playername):
        self.playername = playername
        self.GAMEMODES = {'SOLO': 'br_87', 'TRIO': 'br_25', 'QUAD': 'br_89', 'PLUNDER_TRIO': 'br_dmz_104'}
        self.Stats_URL = 'https://my.callofduty.com/api/papi-client/stats/cod/v1/title/mw/platform/psn/gamer/' + self.playername + '/profile/type/wz'
        self.player_stats = {}


    def request_playerdata(self, url):
        r = requests.get(self.Stats_URL)
        status = r.status_code
        print(status)
        if status != 200:
            print("no data received")
            self.data = None
        else:
            self.data = r.json()['data']


    def collect_data(self):
        self.request_playerdata(self.Stats_URL)

        if self.data == None:
            return None
        self.player_stats["basic"] = { 'name': self.data['username'], 'level': self.data['level'], 'levelXpRemainder': self.data['levelXpRemainder'], 'levelXpGained': self.data['levelXpGained'], 'totalXp': self.data['totalXp'] }

        self.player_stats["br_lifetime"] = self.data['lifetime']['mode']['br']['properties']

        br_weekly = {}
        for k, v in self.GAMEMODES.items():
            if v in self.data['weekly']['mode']:
                br_weekly[k] = self.data['weekly']['mode'][v]
        self.player_stats["br_weekly"] = br_weekly




