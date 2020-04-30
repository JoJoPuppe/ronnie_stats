from app import app
from app import db
from datetime import datetime
from sqlalchemy import func
from app.models import LifeTimeStats, WeeklyStats
from flask import render_template, request

from app.convert_stats import DataConverter
from app.convert_match_stats import MatchConverter
from app.PropFirst import PropFirst
from stats_config import WARZONE_CONFIG

@app.route('/')
@app.route('/index')
def index():
    data = DataConverter()
    life_time_table = data.create_LT_table()
    #print(life_time_table[0]['Time'])
    #wk_trio_table = data.create_WK_table('TRIO')
    #wk_quad_table = data.create_WK_table('QUAD')
    #wk_solo_table = data.create_WK_table('SOLO')

    return render_template('index.html', stats=life_time_table)

@app.route('/matches/<player>')
def matches(player):
    match_query = MatchConverter()
    matches = match_query.create_match_data(player)

    return render_template('matches.html', matches=matches)

@app.route('/squad_match/<match_id>')
def squad_match(match_id):
    match_query = MatchConverter()
    match = match_query.create_squad_match_details(match_id)

    return render_template('squad_match.html', match=match)

@app.route('/weekly')
def player_profile():

    NAMES = WARZONE_CONFIG['NAMES']
    INTERVAL_NAMES = ['Week', 'Month', 'Year', 'Last-30-Matches', 'Last-50-Matches', 'Last-100-Matches']
    players = request.args.getlist('players')
    interval = request.args.get('interval')
    mi = request.args.get('mi')

    if mi == None:
        mi = 0

    if int(mi) < 0:
        mi = 0

    if interval == None:
        interval = 'Week'

    profil_query = MatchConverter()
    data = []
    for player in players:
        data.append(profil_query.consolidate_interval_stats(player, interval, int(mi)))

    reorder_props = PropFirst()
    data = reorder_props.reorganize(data)

    return render_template('weekly.html', data=data, names=NAMES, interval_names=INTERVAL_NAMES, interval=interval)

