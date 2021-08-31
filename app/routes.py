from app import app
from app.models import LifeTimeStats, WeeklyStats
from flask import render_template, request

from app.db_queries import DbQuery
from app.convert_stats import DataConverter
from app.convert_match_stats import MatchConverter
from app.convert_interval_stats import IntervalConverter
from app.PropFirst import PropFirst
from app.bestof import Score
from stats_config import WARZONE_CONFIG
import json

query = DbQuery()

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


@app.route('/matches_json')
def matches_json():
    player = request.args['player']
    page = request.args['page']
    match_query = MatchConverter()
    matches = match_query.create_match_data_paginate(player, page)
    for match in matches:
        del match['timestamp']
    response = app.response_class(
            response=json.dumps(matches),
            status=200,
            mimetype='application/json'
        )
    return response


@app.route('/detail_matches_json')
def detail_matches_json():
    player = request.args['player']
    page = request.args['page']
    match_query = MatchConverter()
    matches = match_query.create_detail_match_data_paginate(player, page)
    for match in matches:
        del match['timestamp']
    response = app.response_class(
            response=json.dumps(matches),
            status=200,
            mimetype='application/json'
        )
    return response

@app.route('/squad_match_json')
def squad_match_json():
    matchId = request.args['matchid']
    match_query = MatchConverter()
    match = match_query.create_squad_match_details(matchId)
    print(match)
    for player in match:
        del player['timestamp']
    response = app.response_class(
            response=json.dumps(match),
            status=200,
            mimetype='application/json'
        )
 
    return response

@app.route('/grouped_stats_json')
def grouped_stats():

    NAMES = WARZONE_CONFIG['NAMES']
    INTERVAL_NAMES = ['Day', 'Week', 'Month', 'Year', 'Last-30-Matches', 'Last-50-Matches', 'Last-100-Matches', 'Last-7-Days']
    players = request.args.getlist('players')
    interval = request.args.get('interval')
    mi = request.args.get('mi')
    only_teams_stats = request.args.get('team')

    try:
        x = int(mi)
    except:
        mi = 0

    if mi == None or int(mi) < 0:
        mi = 0

    if int(mi) < 0:
        mi = 0

    if interval not in INTERVAL_NAMES:
        interval = 'Week'

    checked_players = []
    for player in players:
        if not isinstance(player, str) or player not in NAMES:
            checked_players.append('jojopuppe')
        else:
            checked_players.append(player)

    checked_players = list(dict.fromkeys(checked_players))

    profil_query = IntervalConverter()
    data = []

    if only_teams_stats:
        interval = 'Last-20-Matches'
        data = profil_query.get_team_matches(checked_players)

    else:
        for player in checked_players:
            data.append(profil_query.consolidate_interval_stats(player, interval, int(mi)))

    reorder = PropFirst()
    real_data = reorder.reorganize(data, reorder.real_data)
    # perf_data = reorder.reorganize(data, reorder.perf_data, invert=False)

    #return render_template('weekly.html', data=real_data, pdata=perf_data, names=NAMES, interval_names=INTERVAL_NAMES, interval=interval)

    response = app.response_class(
            response=json.dumps(real_data),
            status=200,
            mimetype='application/json'
        )
 
    return response

# @app.route('/squad_match/<match_id>')
# def squad_match(match_id):
#     match_query = MatchConverter()
#     match = match_query.create_squad_match_details(match_id)
# 
#     return render_template('squad_match.html', match=match)

@app.route('/match_data/<match_id>')
def squad_match(match_id):
    match_query = MatchConverter()
    match = match_query.create_squad_match_details(match_id)
    return render_template('squad_match.html', match=match)

@app.route('/weekly')
def player_profil():

    NAMES = WARZONE_CONFIG['NAMES']
    INTERVAL_NAMES = ['Day', 'Week', 'Month', 'Year', 'Last-30-Matches', 'Last-50-Matches', 'Last-100-Matches',]
    players = request.args.getlist('players')
    interval = request.args.get('interval')
    mi = request.args.get('mi')
    only_teams_stats = request.args.get('team')

    try:
        x = int(mi)
    except:
        mi = 0

    if mi == None or int(mi) < 0:
        mi = 0

    if int(mi) < 0:
        mi = 0

    if interval not in INTERVAL_NAMES:
        interval = 'Week'

    checked_players = []
    for player in players:
        if not isinstance(player, str) or player not in NAMES:
            checked_players.append('jojopuppe')
        else:
            checked_players.append(player)

    checked_players = list(dict.fromkeys(checked_players))

    profil_query = IntervalConverter()
    data = []

    if only_teams_stats:
        interval = 'Last-20-Matches'
        data = profil_query.get_team_matches(checked_players)

    else:
        for player in checked_players:
            data.append(profil_query.consolidate_interval_stats(player, interval, int(mi)))

    reorder = PropFirst()
    real_data = reorder.reorganize(data, reorder.real_data)
    perf_data = reorder.reorganize(data, reorder.perf_data, invert=False)

    return render_template('weekly.html', data=real_data, pdata=perf_data, names=NAMES, interval_names=INTERVAL_NAMES, interval=interval)

@app.route('/skill')
def skill():
    INTERVAL_NAMES = ['Day', 'Week', 'Month', 'Year', 'Last-30-Matches', 'Last-50-Matches', 'Last-100-Matches']
    interval = request.args.get('interval')
    mi = request.args.get('mi')

    try:
        x = int(mi)
    except:
        mi = 0

    if mi == None or int(mi) < 0:
        mi = 0

    if int(mi) < 0:
        mi = 0

    if interval not in INTERVAL_NAMES:
        interval = 'Week'

    sk= Score()
    skill = sk.calc(interval, mi)
    times = sk.time

    return render_template('skill.html', skill=skill, times=times)

