import requests
import re
from collections import namedtuple
import logging
from stats_config import WARZONE_CONFIG

LOG_FILE = WARZONE_CONFIG['LOGFILE']

logging.basicConfig(level=logging.INFO, filename=LOG_FILE, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

class WarzoneStats(object):
    def __init__(self, playername, cookies):
        self.playername = playername
        self.cookies = cookies
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

        self.Stats_URL = 'https://my.callofduty.com/api/papi-client/stats/cod/v1/title/mw/platform/psn/gamer/' +self.playername + '/profile/type/wz'
        self.MatchID_URL = 'https://www.callofduty.com/api/papi-client/crm/cod/v2/title/mw/platform/psn/fullMatch/wz/'
        self.Match_URL = 'https://my.callofduty.com/api/papi-client/crm/cod/v2/title/mw/platform/psn/gamer/'+ self.playername +'/matches/wz/start/0/end/0/details'


    def request_player_data(self):
        cookie = self.cookies
        if not cookie:
            return None
        cookies = cookie['data']
        r = requests.get(self.Stats_URL, cookies=cookies)
        response_string = r.content.decode("utf-8")
        if 'error' not in response_string or 'not' not in response_string:
            return r.json()['data']
        
        return None


    def request_match_data(self):
        cookie = self.cookies
        if not cookie:
            return None
        cookies = cookie['data']
        r = requests.get(self.Match_URL, cookies=cookies)
        response = r.json()
        if response['status'] != 'error':
            return r.json()['data']['matches']

        return None


    def request_matchID(self, match_id):
        cookie = self.cookies
        if not cookie:
            return None
        cookies = cookie['data']
        URL = self.MatchID_URL + match_id + "/it"
        r = requests.get(URL, cookies=cookies)
        response = r.json()
        if response['status'] != 'error':
            return r.json()['data']['allPlayers']
        else:
            print("request matchID failed")
            logging.error("request MatchID failed")
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


    def collect_match_data(self, match_data_in):
        match_data = match_data_in
        match_data = self.add_team_to_match_data(match_data)

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
