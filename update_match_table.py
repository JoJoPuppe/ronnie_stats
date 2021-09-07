from app import app
from app import db
from app.models import MatchStats
from app.get_warzone_stats import WarzoneStats
from app.authentication import Authentication
from app.notifications import Notification
import time
from sqlalchemy import and_
import re
import logging

from stats_config import WARZONE_CONFIG

NAMES = WARZONE_CONFIG['NAMES']
LOG_FILE = WARZONE_CONFIG['LOGFILE']

logging.basicConfig(level=logging.INFO, filename=LOG_FILE, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

auth = Authentication()
auth.update_cookies()
cookie_dict = auth.cookies

if not cookie_dict:
    print('no cookies available, please add more cookies')
else:
    cookies_working = False

    for c in range(len(cookie_dict['cookies'])):
        if cookies_working:
            break
        for name in NAMES:
            get_stat_obj = WarzoneStats(name, cookie_dict['cookies'][c])
            match_data = get_stat_obj.request_match_data()
            if match_data == None:
                logging.error(f"cant get match data: {name}")
                print(f"cant get macht data: {name}")
                auth.failed_cookies(c)
                break
            else:
                match_notification = Notification(name)

                cookies_working = True
                jdata = get_stat_obj.collect_match_data(match_data)
                cnt = 0

                for m in jdata:

                    matchid = str(m['MatchStat']['matchID'])

                    converted_playername = re.sub(r'^\[.*\]','', m["MatchStat"]['playername']).lower()
                    if(converted_playername == 'br3mmel'):
                        converted_playername = 'br3mm3l'
                    if(converted_playername == 'camarleng0'):
                        converted_playername = 'camarlengo'

                    q = MatchStats.query.filter(and_(MatchStats.matchID == matchid,
                                                        MatchStats.playername == converted_playername)).first()
                    if q == None:
                        if name == converted_playername:
                            pass
                            match_notification.add_match(
                                    kills=m['MatchPlayerStats']['kills'],
                                    deaths=m['MatchPlayerStats']['deaths'],
                                    damage_done=m['MatchPlayerStats']['damageDone'])

                        epoch = m['MatchStat']['utcStartSeconds']
                        start_match_time = time.strftime("%a, %d%b%Y %H:%M:%S", time.localtime(epoch))
                        logging.info(f'match {start_match_time} of {name} added')

                             

                    else:
                        #print(f"match from {name} already in db")
                        continue

                    record = MatchStats(
                                utcStartSeconds = int(m["MatchStat"]['utcStartSeconds']),
                                utcEndSeconds = int(m["MatchStat"]['utcEndSeconds']),
                                matchID = str(m["MatchStat"]['matchID']),
                                duration = int(m["MatchStat"]['duration']),
                                playerCount = int(m["MatchStat"]['playerCount']),
                                teamCount = int(m["MatchStat"]['teamCount']),
                                playername = converted_playername,
                                gameMode = m["MatchStat"]['gameMode'],
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
                                pickupTablet = int(m['MatchPlayerStats']['objectiveBrMissionPickupTablet']),
                                teamWipes = int(m['MatchPlayerStats']['objectiveTeamWiped']),
                                boxesOpen = int(m['MatchPlayerStats']['objectiveBrCacheOpen']),
                                lastStandKills = int(m['MatchPlayerStats']['objectiveLastStandKill']),
                                shopping = int(m['MatchPlayerStats']['objectiveBrKioskBuy']),
                                bonusXp = int(m['MatchPlayerStats']['bonusXp']),
                                circle1 = int(m['MatchPlayerStats']['objectiveBrDownEnemyCircle1']),
                                circle2 = int(m['MatchPlayerStats']['objectiveBrDownEnemyCircle2']),
                                circle3 = int(m['MatchPlayerStats']['objectiveBrDownEnemyCircle3']),
                                circle4 = int(m['MatchPlayerStats']['objectiveBrDownEnemyCircle4']),
                                circle5 = int(m['MatchPlayerStats']['objectiveBrDownEnemyCircle5']),
                                circle6 = int(m['MatchPlayerStats']['objectiveBrDownEnemyCircle6']),
                                circle7 = int(m['MatchPlayerStats']['objectiveBrDownEnemyCircle7']),
                                revives = int(m['MatchPlayerStats']['objectiveReviver']),
                                timePlayed = int(m['MatchPlayerStats']['timePlayed']),
                                percentTimeMoving = int(m['MatchPlayerStats']['percentTimeMoving']),
                                miscXp = int(m['MatchPlayerStats']['miscXp']),
                                longestStreak = int(m['MatchPlayerStats']['longestStreak']),
                                teamPlacement = int(m['MatchPlayerStats']['teamPlacement']),
                                damageDone = int(m['MatchPlayerStats']['damageDone']),
                                damageTaken = int(m['MatchPlayerStats']['damageTaken']))

                    db.session.add(record)
                    cnt += 1
                    #print(f"match added {name}")

            print(f'{cnt} matches of {name} added. wait 3s')
            logging.info(f'{cnt} matches of {name} added. wait 3s')
            if match_notification.matches != 0:
                match_notification.send_notification_report()
            time.sleep(3)

    db.session.commit()
