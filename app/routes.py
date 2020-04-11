from app import app
from app import db
from datetime import datetime
from sqlalchemy import func
from app.models import LifeTimeStats
from flask import render_template
from .get_warzone_stats import WarzoneStats

@app.route('/')
@app.route('/index')
def index():
    query_list = LifeTimeStats.query.group_by(LifeTimeStats.playername).having(func.max(LifeTimeStats.timestamp))
    
    player_stat_list = []
    for player in query_list:
        player_stats = vars(player)
        del player_stats['_sa_instance_state']

        for k, v in player_stats.items():
            if k == 'kdRatio':
                v = round(v, 2)
                player_stats[k] = v
            if k == 'timestamp':
                v = v.strftime("%H:%M:%S")
                player_stats[k] = v
        player_stat_list.append(player_stats)

    print(player_stat_list)
    return render_template('index.html', stats=player_stat_list)
