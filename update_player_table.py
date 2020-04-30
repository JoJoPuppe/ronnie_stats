from app import app
from app import db
from app.models import LifeTimeStats, WeeklyStats
from app.get_warzone_stats import WarzoneStats
import time
import logging

from stats_config import WARZONE_CONFIG

NAMES = WARZONE_CONFIG['NAMES']
LOG_FILE = WARZONE_CONFIG['LOGFILE']

logging.basicConfig(level=logging.INFO, filename=LOG_FILE, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

test_request = WarzoneStats('jojopuppe')
if test_request.request_player_data() == None:
    logging.error(f"no player data recorded")

else:
    for name in NAMES:
        get_stat_obj = WarzoneStats(name)
        jdata = get_stat_obj.collect_player_data()

        time_played = jdata['br_lifetime']['timePlayed']

        q = LifeTimeStats.query.filter(LifeTimeStats.timePlayed == time_played).first()
        if q != None:
            logging.info(f'no lifetime change of {name}')
        else:
            logging.info(f'new lifetime stats for {name}')
            record = LifeTimeStats(
                        playername = jdata['br_lifetime']['name'],
                        level = int(jdata['br_lifetime']['level']),
                        wins = int(jdata['br_lifetime']['wins']),
                        kills = int(jdata['br_lifetime']['kills']),
                        kdRatio = jdata['br_lifetime']['kdRatio'],
                        downs = int(jdata['br_lifetime']['downs']),
                        deaths = int(jdata['br_lifetime']['deaths']),
                        topTwentyFive = int(jdata['br_lifetime']['topTwentyFive']),
                        topTen = int(jdata['br_lifetime']['topTen']),
                        topFive = int(jdata['br_lifetime']['topFive']),
                        contracts = int(jdata['br_lifetime']['contracts']),
                        score = int(jdata['br_lifetime']['score']),
                        scorePerMinute = int(jdata['br_lifetime']['scorePerMinute']),
                        timePlayed = int(jdata['br_lifetime']['timePlayed']),
                        gamesPlayed = int(jdata['br_lifetime']['gamesPlayed']
            ))
            db.session.add(record)

        for k, v in jdata['br_weekly'].items():

            time_played = jdata['br_weekly'][k]['properties']['timePlayed']

            q = WeeklyStats.query.filter(WeeklyStats.timePlayed == time_played,
                                         WeeklyStats.gameMode == k).first()
            if q != None:
                logging.info(f'weekly stat of {k} of {name} has not changed')
            else:
                logging.info(f'new weekly {k} stats for {name}')
                record_weekly = WeeklyStats(
                            playername = jdata['br_lifetime']['name'],
                            gameMode = k,
                            wins = int(jdata['br_weekly'][k]['properties']['wins']),
                            kills = int(jdata['br_weekly'][k]['properties']['kills']),
                            headshots = int(jdata['br_weekly'][k]['properties']['headshots']),
                            kdRatio = jdata['br_weekly'][k]['properties']['kdRatio'],
                            deaths = int(jdata['br_weekly'][k]['properties']['deaths']),
                            killsPerGame = jdata['br_weekly'][k]['properties']['killsPerGame'],
                            score = int(jdata['br_weekly'][k]['properties']['score']),
                            scorePerMinute = jdata['br_weekly'][k]['properties']['scorePerMinute'],
                            timePlayed = int(jdata['br_weekly'][k]['properties']['timePlayed']),
                            teamWipes = int(jdata['br_weekly'][k]['properties']['objectiveTeamWiped']),
                            lastStandKills = int(jdata['br_weekly'][k]['properties']['objectiveLastStandKill']),
                            distanceTraveled = int(jdata['br_weekly'][k]['properties']['distanceTraveled']),
                            circle1 = int(jdata['br_weekly'][k]['properties']['objectiveBrDownEnemyCircle1']),
                            circle2 = int(jdata['br_weekly'][k]['properties']['objectiveBrDownEnemyCircle2']),
                            circle3 = int(jdata['br_weekly'][k]['properties']['objectiveBrDownEnemyCircle3']),
                            circle4 = int(jdata['br_weekly'][k]['properties']['objectiveBrDownEnemyCircle4']),
                            circle5 = int(jdata['br_weekly'][k]['properties']['objectiveBrDownEnemyCircle5']),
                            circle6 = int(jdata['br_weekly'][k]['properties']['objectiveBrDownEnemyCircle6']),
                            circle7 = int(jdata['br_weekly'][k]['properties']['objectiveBrDownEnemyCircle7']),
                            pickupTablet = int(jdata['br_weekly'][k]['properties']['objectiveBrMissionPickupTablet']),
                            revives = int(jdata['br_weekly'][k]['properties']['objectiveReviver']),
                            boxesOpen = int(jdata['br_weekly'][k]['properties']['objectiveBrCacheOpen']),
                            shopping = int(jdata['br_weekly'][k]['properties']['objectiveBrKioskBuy']),
                            matchesPlayed = int(jdata['br_weekly'][k]['properties']['matchesPlayed']),
                            damageDone = int(jdata['br_weekly'][k]['properties']['damageDone']),
                            damageTaken = int(jdata['br_weekly'][k]['properties']['damageTaken'])
                )

                db.session.add(record_weekly)

        logging.info(f'lifetime and weekly stats of {name} done. wait 3s')
        time.sleep(3)

    db.session.commit()


