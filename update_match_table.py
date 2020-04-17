from app import app
from app import db
from app.models import MatchStats, MatchPlayerStats
from app.get_warzone_stats import WarzoneStats
import time
from sqlalchemy import and_

NAMES = ['jojopuppe', 'dlt_orko', 'neuner_eisen', 'topperinski', 'superboergerli']

for name in NAMES:
    print("delay next request by 3s")
    time.sleep(3)
    get_stat_obj = WarzoneStats(name)
    jdata = get_stat_obj.collect_match_data()

    for m in jdata:

        matchid = str(m['MatchStat']['matchID'])

        q = MatchStats.query.filter(and_(MatchStats.matchID == matchid,
                                         MatchStats.playername == name)).first()
        if q != None:
            print('match already in db')
            continue

        record = MatchStats(
                    utcStartSeconds = int(m["MatchStat"]['utcStartSeconds']),
                    utcEndSeconds = int(m["MatchStat"]['utcEndSeconds']),
                    matchID = str(m["MatchStat"]['matchID']),
                    duration = int(m["MatchStat"]['duration']),
                    playerCount = int(m["MatchStat"]['playerCount']),
                    teamCount = int(m["MatchStat"]['teamCount']),
                    playername = m["MatchStat"]['playername'],
                    gameMode = m["MatchStat"]['gameMode']
        )
        db.session.add(record)

        record_player = MatchPlayerStats(
                    playername = m['MatchPlayerStats']['playername'],
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

db.session.commit()
