from app import db
from datetime import datetime

class LifeTimeStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    playername = db.Column(db.String(64))
    level = db.Column(db.Integer)
    wins = db.Column(db.Integer)
    kills = db.Column(db.Integer)
    kdRatio = db.Column(db.Float)
    downs = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    topTwentyFive = db.Column(db.Integer)
    topTen = db.Column(db.Integer)
    topFive = db.Column(db.Integer)
    contracts = db.Column(db.Integer)
    score = db.Column(db.Integer)
    scorePerMinute = db.Column(db.Float)
    timePlayed = db.Column(db.Integer)
    gamesPlayed = db.Column(db.Integer)

    def __repr__(self):
        return f'Player: {self.playername}, kills: {self.timestamp}'

