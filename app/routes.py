from app import app
from app import db
from datetime import datetime
from sqlalchemy import func
from app.models import LifeTimeStats, WeeklyStats
from flask import render_template, request

from app.convert_stats import DataConverter
from app.convert_match_stats import MatchConverter

@app.route('/')
@app.route('/index')
def index():
    data = DataConverter()
    life_time_table = data.create_LT_table()
    #print(life_time_table[0]['Time'])
    wk_trio_table = data.create_WK_table('TRIO')
    wk_quad_table = data.create_WK_table('QUAD')
    wk_solo_table = data.create_WK_table('SOLO')

    return render_template('index.html', stats=life_time_table, wk_trio_stats=wk_trio_table,
                                            wk_quad_stats=wk_quad_table, wk_solo_stats=wk_solo_table)
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



