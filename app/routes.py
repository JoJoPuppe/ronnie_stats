from app import app
from app import db
from datetime import datetime
from sqlalchemy import func
from app.models import LifeTimeStats, WeeklyStats
from flask import render_template

from app.convert_stats import DataConverter

@app.route('/')
@app.route('/index')
def index():
    data = DataConverter()
    life_time_table = data.create_LT_table()
    wk_trio_table = data.create_WK_table('TRIO')
    wk_quad_table = data.create_WK_table('QUAD')
    wk_solo_table = data.create_WK_table('SOLO')

    return render_template('index.html', stats=life_time_table, wk_trio_stats=wk_trio_table,
                                            wk_quad_stats=wk_quad_table, wk_solo_stats=wk_solo_table)



