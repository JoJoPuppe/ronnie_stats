from app import app, db
from sqlalchemy import func, desc
from app.models import MatchStats

class DbQuery(object):
    def __init__(self):
        pass

    def from_database_matchstats(self, playername):
        return MatchStats.query.filter(MatchStats.playername == playername).\
                order_by(desc(MatchStats.utcStartSeconds)).limit(20).all()

    def from_database_matchstats_paginate(self, playername, page):
        return MatchStats.query.filter(MatchStats.playername == playername).\
                order_by(desc(MatchStats.utcStartSeconds)).paginate(page=page, per_page=5)

    def from_database_squad_match(self, playername):
        sub = MatchStats.query.with_entities(MatchStats.id, MatchStats.matchID, func.count(MatchStats.matchID).label("count_id") ).group_by(MatchStats.matchID).having((func.count(MatchStats.matchID) > 1)).subquery()
        q = db.session.query(MatchStats.matchID, sub.c.count_id, MatchStats.playername).join(sub, MatchStats.matchID == sub.c.matchID).filter(MatchStats.playername == playername).all()
        return [s[0] for s in q]

    def from_database_team_matches(self, playernames):
        sub = MatchStats.query.with_entities(MatchStats.id, MatchStats.matchID, MatchStats.playername).filter(MatchStats.playername.in_(playernames)).group_by(MatchStats.matchID).having(func.count(MatchStats.matchID) == len(playernames)).subquery()
        q = MatchStats.query.join(sub, MatchStats.matchID == sub.c.matchID).filter(MatchStats.playername.in_(playernames)).order_by(MatchStats.utcStartSeconds).limit(60).all()
        return q

    def from_database_squad_details(self, matchID):
        return MatchStats.query.filter(MatchStats.matchID == matchID).all()

    def from_database_time_stats(self, playername, start_time, end_time):
        return MatchStats.query.filter(MatchStats.playername == playername, MatchStats.gameMode != 'Blood Money', MatchStats.gameMode != '3er PLUNDER', MatchStats.gameMode != '2er PLUNDER', MatchStats.gameMode != '4er PLUNDER', MatchStats.utcStartSeconds > start_time, MatchStats.utcStartSeconds < end_time).order_by(MatchStats.utcStartSeconds).all()

    def from_database_count_stats(self, playername, match_count):
        return MatchStats.query.filter(MatchStats.playername == playername, MatchStats.gameMode!= 'Blood Money', MatchStats.gameMode != '3er PLUNDER', MatchStats.gameMode != '2er PLUNDER', MatchStats.gameMode != '4er PLUNDER').order_by(MatchStats.utcStartSeconds).limit(match_count).all()

    def from_database_first_match(self):
        return MatchStats.query.first()

