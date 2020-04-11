from app import app
from app import db
from app.models import LifeTimeStats
from app.get_warzone_stats import WarzoneStats

NAMES = ["jojopuppe", "dlt_orko", "neuner_eisen", "topperinski", "superboergerli"]
player_stats = []
for name in NAMES:
    get_stat_obj = WarzoneStats(name)
    get_stat_obj.collect_data()
    jdata = get_stat_obj.player_stats

    record = LifeTimeStats(
                playername = jdata['basic']['name'],
                level = int(jdata['basic']['level']),
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

db.session.commit()


