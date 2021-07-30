import requests
import time
import simplejson as ss
import re
from collections import namedtuple
import os
import logging
import json
from stats_config import WARZONE_CONFIG

from telegram.ext import Updater

LOG_FILE = WARZONE_CONFIG['LOGFILE']

# telegram bot toten
updater = Updater(token=WARZONE_CONFIG['TELEGRAM_TOKEN'],
		use_context=True)

logging.basicConfig(level=logging.INFO, filename=LOG_FILE, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

class WarzoneStats(object):
    def __init__(self, playername):
        self.email = WARZONE_CONFIG['EMAIL']
        self.pw = WARZONE_CONFIG['PW']
        self.playername = playername
        self.GAMEMODES = {'br_87': 'SOLO',
                          'br_25': 'TRIO',
                          'br_89': 'QUAD',
                          'br_dmz_85': '2er PLUNDER',
                          'br_dmz_38': '3er PLUNDER',
                          'br_dmz_plndtrios': '3er PLUNDER',
                          'br_dmz_plnbld': 'Blood Money',
                          'br_74': 'CLASSIC TR',
                          'br_88': 'DUO',
                          'br_rebirth_rbrthquad': '4er REBIRTH',
                          'br_rebirth_rbrthtrios': '3er REBIRTH',
                          'br_rebirth_rbrthduos': '2er REBIRTH',
                          'br_rebirth_resurgence_trios': '3er REBIRTH VER',
                          'br_mini_rebirth_mini_royale_quads' :'4er Mini Royal Rebirth',
                          'br_dmz_plunquad': '4er PLUNDER'}

        self.Xsrf_token_URL = 'https://s.activision.com/activision/login'
        self.Auth_URL = 'https://s.activision.com/do_login?new_SiteId=activision'
        self.Stats_URL = 'https://my.callofduty.com/api/papi-client/stats/cod/v1/title/mw/platform/psn/gamer/' +self.playername + '/profile/type/wz'
        self.MatchID_URL = 'https://www.callofduty.com/api/papi-client/crm/cod/v2/title/mw/platform/psn/fullMatch/wz/'
        self.Match_URL = 'https://my.callofduty.com/api/papi-client/crm/cod/v2/title/mw/platform/psn/gamer/'+ self.playername +'/matches/wz/start/0/end/0/details'
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.token_file_name = 'auth.token'

    def load_cookies(self):
        cookie_file = os.path.join(self.base_path, 'auth_cookies.txt')
        sso_token, sso_exp, atkn_token, api_token = False, False, False, False
        cookie_dict = {}
        try:
            with open(cookie_file, "r") as f:
                for line in f.readlines():
                    line = line.rstrip('\n')
                    cookie_pair = line.split(",")
                    if "ACT_SSO_COOKIE" == cookie_pair[0]:
                        sso_token = cookie_pair[1]
                    if "ACT_SSO_COOKIE_EXPIRY" == cookie_pair[0]:
                        sso_exp = cookie_pair[1]
                    if "atkn" == cookie_pair[0]:
                        atkn_token = cookie_pair[1]
                    cookie_dict[cookie_pair[0]] = cookie_pair[1]

            if sso_token and sso_exp and atkn_token:
                cookies = {'ACT_SSO_COOKIE': sso_token,
                           'ACT_SSO_COOKIE_EXPIRY': sso_exp,
                           'atkn': atkn_token
                           }
                return cookies

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

        r = s.post(self.Auth_URL, params=payload, timeout=15)
        #r = s.get(self.Stats_URL)
        self.save_cookies(s.cookies)
        logging.info(f'new cookies saved')


    def request_player_data(self, cnt=5):
        cookies = self.load_cookies()
        if cnt != 0:
            if cookies:
                r = requests.get(self.Stats_URL, cookies=cookies)
                response_string = r.content.decode("utf-8")
                if 'error' not in response_string or 'not' not in response_string:
                    return r.json()['data']
                else:
                    print("getting new token")
                    logging.error(f'{response_string}')
                    self.obtain_new_token()
                    time.sleep(5)
                    cnt -= 1
                    self.request_player_data(cnt)
            else:
                self.obtain_new_token()
                time.sleep(5)
                cnt -= 1
                self.request_player_data(cnt)

        logging.error(f'5 request attemps with no result')
        print("5 attempts. no succsess")
        return None


    def request_match_data(self, cnt=5):
        cookies = self.load_cookies()
        if cnt != 0:
            if cookies:

                r = requests.get(self.Match_URL, cookies=cookies)
                response = r.json()
                if response['status'] != 'error':
                    return r.json()['data']['matches']
                else:
                    response_string = r.content.decode("utf-8")
                    logging.error(f'{response_string}')
                    print(response['data'])
                    self.obtain_new_token()
                    time.sleep(5)
                    cnt -= 1
                    self.request_match_data(cnt)
            else:
                self.obtain_new_token()
                time.sleep(5)
                cnt -= 1
                self.request_match_data(cnt)

        logging.error(f'5 request attemps with no result')
        print("5 attempts. no succsess")
        updater.bot.send_message(chat_id=WARZONE_CONFIG['TELEGRAM_CHAT_ID'],\
                text="5 request attemps. tokens may not working.")
        return None

    def request_matchID(self, match_id, cnt=5):
        cookies = self.load_cookies()
        if cnt != 0:
            if cookies:
                URL = self.MatchID_URL + match_id + "/it"
                r = requests.get(URL, cookies=cookies)
                response = r.json()
                if response['status'] != 'error':
                    return r.json()['data']['allPlayers']
                else:
                    response_string = r.content.decode("utf-8")
                    self.obtain_new_token()
                    cnt -= 1
                    self.request_match_data(cnt)
            else:
                self.obtain_new_token()
                cnt -= 1
                self.request_match_data(cnt)

        print("5 attempts. no succsess")
        return None

    def converted_playername(self, playername):
        converted_playername = re.sub(r'^\[.*\]','', playername.lower())
        if converted_playername == 'br3mmel':
            converted_playername = 'br3mm3l'
        if converted_playername == 'camarleng0':
            converted_playername = 'camarlengo'

        return converted_playername

    def collect_player_data(self):
        player_data = self.request_player_data()
        if player_data == None:
            return None

        collected_data = {}

        collected_data["br_lifetime"] = player_data['lifetime']['mode']['br']['properties']

        collected_data["br_lifetime"]['name'] = player_data['username']
        collected_data['br_lifetime']['level'] = player_data['level']

        br_weekly = {}
        for k, v in self.GAMEMODES.items():
            if k in player_data['weekly']['mode']:
                br_weekly[v] = player_data['weekly']['mode'][k]
        collected_data["br_weekly"] = br_weekly

        validated_data = self.validate_data(collected_data)

        return validated_data

    def add_team_to_match_data(self, match_data):
        TeamMatchID = namedtuple("TeamMatchID", "matchid team")
        match_id_list= []
        for match_dict in match_data:
            if match_dict['mode'] not in self.GAMEMODES:
                continue
            match_id_list.append(TeamMatchID(matchid=match_dict['matchID'], team=match_dict['player']['team']))

        team =[]
        for teammatch in match_id_list:
            all_match_players = self.request_matchID(teammatch.matchid)
            if not all_match_players:
                continue
            for player in all_match_players:
                if player['player']['team'] == teammatch.team and not player['player']['username'] == self.playername:
                    team.append(player)

        match_data.extend(team)

        return match_data


    def collect_match_data(self):
        match_data = self.request_match_data()
        match_data = self.add_team_to_match_data(match_data)

        if match_data == None:
            return None

        validate_match_list = []
        for match_dict in match_data:
            collected_data = {'MatchStat': {}, 'MatchPlayerStats': {}}
            if match_dict['mode'] not in self.GAMEMODES:
                logging.info(f"game mode {match_dict['mode']} not supported")
                print(f"game mode {match_dict['mode']} not supported")
                continue
            try:
                collected_data["MatchStat"]['utcStartSeconds'] = match_dict['utcStartSeconds']
                collected_data["MatchStat"]['utcEndSeconds'] = match_dict['utcEndSeconds']
                collected_data["MatchStat"]['matchID'] = match_dict['matchID']
                collected_data["MatchStat"]['duration'] = match_dict['duration']
                collected_data["MatchStat"]['playerCount'] = match_dict['playerCount']
                collected_data["MatchStat"]['teamCount'] = match_dict['teamCount']
                collected_data["MatchStat"]['playername'] = match_dict['player']['username']
                collected_data["MatchStat"]['gameMode'] = self.GAMEMODES[match_dict['mode']]

                collected_data['MatchPlayerStats'] = match_dict['playerStats']
                collected_data['MatchPlayerStats']['matchID'] = match_dict['matchID']

            except KeyError:
                print("Match data not complete")
                continue

            if 'teamPlacement' not in collected_data['MatchPlayerStats']:
                try:
                    #print(f'no placement found for {self.playername}. search alternative data')
                    for t in range(0, len(match_dict['rankedTeams'])):
                        for player in match_dict['rankedTeams'][t]['players']:
                            converted_playername = self.converted_playername(player['username'])
                            if self.playername == converted_playername:
                                #print(player['username'])
                                #print(f"new placement found {t + 1}")
                                collected_data['MatchPlayerStats']['teamPlacement'] = t + 1
                except:
                    print("cant find Teamplacement")
                    collected_data['MatchPlayerStats']['teamPlacement'] = 0


            validated_data = self.validate_match_data(collected_data)

            validate_match_list.append(validated_data)

        return validate_match_list

    def validate_match_data(self, raw_data):
        MATCH_STATS = ['utcStartSecond', 'utcEndSeconds', 'matchID', 'duration', 'playerCount', 'teamCount', 'playername', 'gameMode']

        MATCH_PLAYER_STATS = ['matchID', 'playername', 'wins', 'kill', 'medalXp', 'matchXp', 'scoreXp', 'score', 'totalXp', 'headshots',
                              'assists', 'challengeXp', 'scorePerMinute', 'distanceTraveled', 'teamSurvivalTime', 'deaths',
                              'kdRatio', 'objectiveBrKioskBuy', 'objectiveLastStandKill', 'objectiveBrCacheOpen', 'objectiveTeamWiped',
                              'objectiveBrMissionPickupTablet', 'bonusXp', 'timePlayed', 'percentTimeMoving', 'miscXp', 'longestStreak',
                              'teamPlacement', 'damageDone', 'damageTaken', 'objectiveBrDownEnemyCircle1', 'objectiveBrDownEnemyCircle2',
                              'objectiveBrDownEnemyCircle3', 'objectiveBrDownEnemyCircle4', 'objectiveBrDownEnemyCircle5',
                              'objectiveBrDownEnemyCircle6', 'objectiveBrDownEnemyCircle7', 'objectiveReviver' ]
        for stat in MATCH_STATS:
            if stat not in raw_data['MatchStat']:
                raw_data['MatchStat'][stat] = 0

        for stat in MATCH_PLAYER_STATS:
            if stat not in raw_data['MatchPlayerStats']:
                raw_data['MatchPlayerStats'][stat] = 0

        return raw_data

    def validate_data(self, raw_data):
        LIFE_TIME_STATS_KEYS = ['name', 'level', 'wins', 'kills', 'kdRatio', 'downs', 'deaths',
                                'topTwentyFive', 'topTen', 'topFive', 'contracts', 'score',
                                'scorePerMinute', 'timePlayed', 'gamesPlayed']

        WEEKLY_STATS_KEYS = ['wins', 'kills', 'headshots', 'kdRatio', 'deaths', 'killsPerGame',
                             'score', 'scorePerMinute', 'timePlayed', 'objectiveTeamWiped',
                             'objectiveLastStandKill', 'distanceTraveled', 'objectiveBrDownEnemyCircle1', 'objectiveBrDownEnemyCircle2', 'objectiveBrDownEnemyCircle3',
                             'objectiveBrDownEnemyCircle4', 'objectiveBrDownEnemyCircle5', 'objectiveBrDownEnemyCircle6', 'objectiveBrDownEnemyCircle7',
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
