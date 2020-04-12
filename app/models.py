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
    scorePerMinute = db.Column(db.Integer)
    timePlayed = db.Column(db.Integer)
    gamesPlayed = db.Column(db.Integer)

    def __repr__(self):
        return f'Player: {self.playername}, timestamp: {self.timestamp.strftime("%H:%M:%S") }'

class WeeklyStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    playername = db.Column(db.String(64))
    gameMode = db.Column(db.String(32))
    wins = db.Column(db.Integer)
    kills = db.Column(db.Integer)
    headshots = db.Column(db.Integer)
    kdRatio = db.Column(db.Float)
    deaths = db.Column(db.Integer)
    killsPerGame = db.Column(db.Float)
    score = db.Column(db.Integer)
    scorePerMinute = db.Column(db.Integer)
    timePlayed = db.Column(db.Integer)
    TeamWipes = db.Column(db.Integer)
    LastStandKills = db.Column(db.Integer)
    avgLifeTime = db.Column(db.Integer)
    distanceTraveled = db.Column(db.Integer)
    circle1 = db.Column(db.Integer)
    circle2 = db.Column(db.Integer)
    circle3 = db.Column(db.Integer)
    circle4 = db.Column(db.Integer)
    circle5 = db.Column(db.Integer)
    pickupTablet = db.Column(db.Integer)
    revives = db.Column(db.Integer)
    shopping = db.Column(db.Integer)
    matchesPlayed = db.Column(db.Integer)
    boxesOpen = db.Column(db.Integer)
    damageDone = db.Column(db.Integer)
    damageTaken = db.Column(db.Integer)

    def __repr__(self):
        return f'Player: {self.playername}, timestamp: {self.timestamp.strftime("%H:%M:%S") }, played: {self.timePlayed}'
