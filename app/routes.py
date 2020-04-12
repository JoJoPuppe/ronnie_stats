from app import app
from app import db
from datetime import datetime
from sqlalchemy import func
from app.models import LifeTimeStats, WeeklyStats
from flask import render_template

from app.convert_stats import DataConverter

@app.route('/stats')
def stats():
    data = DataConverter()
    life_time_table = data.create_LT_table()
    wk_trio_table = data.create_WK_table('TRIO')
    wk_quad_table = data.create_WK_table('QUAD')
    wk_solo_table = data.create_WK_table('SOLO')

    return render_template('stats.html', stats=life_time_table, wk_trio_stats=wk_trio_table,
                                            wk_quad_stats=wk_quad_table, wk_solo_stats=wk_solo_table)


@app.route('/')
@app.route('/index')
def index():
    query_list = LifeTimeStats.query.group_by(LifeTimeStats.playername).having(func.max(LifeTimeStats.timestamp))

    query_weekly = WeeklyStats.query.group_by(WeeklyStats.gameMode).group_by(WeeklyStats.playername).having(func.max(WeeklyStats.timestamp))

    player_stat_list = []
    for player in query_list:
        player_stats = vars(player)
        if '_sa_instance_state' in player_stats:
            del player_stats['_sa_instance_state']

        for k, v in player_stats.items():
            if k == 'kdRatio':
                v = round(v, 2)
                player_stats[k] = v
            if k == 'timestamp':
                v = v.strftime("%H:%M:%S")
                player_stats[k] = v
        player_stat_list.append(player_stats)

    weekly_stats_list = []
    for player in query_weekly:
        weekly_stat = vars(player)
        if '_sa_instance_state' in weekly_stat:
            del weekly_stat['_sa_instance_state']

        for k, v in weekly_stat.items():
            if k == 'kdRatio':
                v = round(v, 2)
                weekly_stat[k] = v
            if k == 'scorePerMinute':
                v = round(v, 2)
                weekly_stat[k] = v
            if k == 'killsPerGame':
                v = round(v, 2)
                weekly_stat[k] = v
            if k == 'timestamp':
                v = v.strftime("%H:%M:%S")
                weekly_stat[k] = v

        weekly_stats_list.append(weekly_stat)

    return render_template('index.html', stats=player_stat_list, weekly_stats=weekly_stats_list)
