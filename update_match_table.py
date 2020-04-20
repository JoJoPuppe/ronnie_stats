from app import app
from app import db
from app.models import MatchStats, MatchPlayerStats
from app.get_warzone_stats import WarzoneStats
import os
import time
from sqlalchemy import and_
import re
import logging

from stats_config import WARZONE_CONFIG

#NAMES = ['jojopuppe', 'dlt_orko', 'neuner_eisen', 'topperinski', 'superboergerli']

LOG_FILE = WARZONE_CONFIG['LOGFILE']

logging.basicConfig(level=logging.INFO, filename=LOG_FILE, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')



NAMES = ['jojopuppe', 'dlt_orko', 'neuner_eisen', 'topperinski', 'superboergerli',
         'kiishonsuu', 'br3mm3l', 'bratlos', 'camarlengo', 'knabenbube', 'schwabilton']

for name in NAMES:
    get_stat_obj = WarzoneStats(name)
    jdata = get_stat_obj.collect_match_data()

    for m in jdata:

        matchid = str(m['MatchStat']['matchID'])

        converted_playername = re.sub(r'^\[.*\]','', m["MatchStat"]['playername']).lower()
        if(converted_playername == 'br3mmel'):
            converted_playername = 'br3mm3l'
        if(converted_playername == 'camarleng0'):
            converted_playername = 'camarlengo'

        q = MatchStats.query.filter(and_(MatchStats.matchID == matchid,
                                         MatchStats.playername == name)).first()
        if q == None:
            epoch = m['MatchStat']['utcStartSeconds']
            start_match_time = time.strftime("%a, %d%b%Y %H:%M:%S", time.localtime(epoch))
            logging.info(f'match {start_match_time} of {name} added')
        else:
            continue

        record = MatchStats(
                    utcStartSeconds = int(m["MatchStat"]['utcStartSeconds']),
                    utcEndSeconds = int(m["MatchStat"]['utcEndSeconds']),
                    matchID = str(m["MatchStat"]['matchID']),
                    duration = int(m["MatchStat"]['duration']),
                    playerCount = int(m["MatchStat"]['playerCount']),
                    teamCount = int(m["MatchStat"]['teamCount']),
                    playername = converted_playername,
                    gameMode = m["MatchStat"]['gameMode']
        )
        db.session.add(record)

        record_player = MatchPlayerStats(
                    playername = converted_playername,
                    matchID = str(m['MatchPlayerStats']['matchID']),
                    kills = int(m['MatchPlayerStats']['kills']),
                    medalXp = int(m['MatchPlayerStats']['medalXp']),
                    matchXp = int(m['MatchPlayerStats']['matchXp']),
                    scoreXp = int(m['MatchPlayerStats']['scoreXp']),
                    score = int(m['MatchPlayerStats']['score']),
                    totalXp = int(m['MatchPlayerStats']['totalXp']),
                    headshots = int(m['MatchPlayerStats']['headshots']),
                    assists = int(m['MatchPlayerStats']['assists']),
                    challengeXp = int(m['MatchPlayerStats']['challengeXp']),
                    scorePerMinute = int(m['MatchPlayerStats']['scorePerMinute']),
                    distanceTraveled = int(m['MatchPlayerStats']['distanceTraveled']),
                    teamSurvivalTime = int(m['MatchPlayerStats']['teamSurvivalTime']),
                    deaths = int(m['MatchPlayerStats']['deaths']),
                    kdRatio = m['MatchPlayerStats']['kdRatio'],
                    objectiveBrMissionPickupTablet = int(m['MatchPlayerStats']['objectiveBrMissionPickupTablet']),
                    objectiveTeamWiped = int(m['MatchPlayerStats']['objectiveTeamWiped']),
                    objectiveBrCacheOpen = int(m['MatchPlayerStats']['objectiveBrCacheOpen']),
                    objectiveLastStandKill = int(m['MatchPlayerStats']['objectiveLastStandKill']),
                    objectiveBrKioskBuy = int(m['MatchPlayerStats']['objectiveBrKioskBuy']),
                    bonusXp = int(m['MatchPlayerStats']['bonusXp']),
                    timePlayed = int(m['MatchPlayerStats']['timePlayed']),
                    percentTimeMoving = int(m['MatchPlayerStats']['percentTimeMoving']),
                    miscXp = int(m['MatchPlayerStats']['miscXp']),
                    longestStreak = int(m['MatchPlayerStats']['longestStreak']),
                    teamPlacement = int(m['MatchPlayerStats']['teamPlacement']),
                    damageDone = int(m['MatchPlayerStats']['damageDone']),
                    damageTaken = int(m['MatchPlayerStats']['damageTaken']))

        db.session.add(record_player)

    logging.info(f'matches of {name} done. wait 3s')
    time.sleep(3)

db.session.commit()
