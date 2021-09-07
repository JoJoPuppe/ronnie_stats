from app import db
from datetime import datetime


class DeviceTokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    playername = db.Column(db.String(64))
    token = db.Column(db.String(128))

    def __repr__(self):
        return f'Player: {self.playername}, timestamp: {self.timestamp.strftime("%H:%M:%S") }, tkn: {self.token}'


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
    teamWipes = db.Column(db.Integer)
    lastStandKills = db.Column(db.Integer)
    avgLifeTime = db.Column(db.Integer)
    distanceTraveled = db.Column(db.Integer)
    circle1 = db.Column(db.Integer)
    circle2 = db.Column(db.Integer)
    circle3 = db.Column(db.Integer)
    circle4 = db.Column(db.Integer)
    circle5 = db.Column(db.Integer)
    circle6 = db.Column(db.Integer)
    circle7 = db.Column(db.Integer)
    pickupTablet = db.Column(db.Integer)
    revives = db.Column(db.Integer)
    shopping = db.Column(db.Integer)
    matchesPlayed = db.Column(db.Integer)
    boxesOpen = db.Column(db.Integer)
    damageDone = db.Column(db.Integer)
    damageTaken = db.Column(db.Integer)

    def __repr__(self):
        return f'Player: {self.playername}, timestamp: {self.timestamp.strftime("%m-%d-%H:%M")}'

class MatchStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    utcStartSeconds = db.Column(db.Integer)
    utcEndSeconds = db.Column(db.Integer)
    playername = db.Column(db.String(64))
    gameMode = db.Column(db.String(32))
    matchID = db.Column(db.String(64))
    duration = db.Column(db.Integer)
    playerCount = db.Column(db.Integer)
    teamCount = db.Column(db.Integer)
    kills = db.Column(db.Integer)
    medalXp = db.Column(db.Integer)
    matchXp = db.Column(db.Integer)
    scoreXp = db.Column(db.Integer)
    score = db.Column(db.Integer)
    totalXp = db.Column(db.Integer)
    headshots = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    challengeXp = db.Column(db.Integer)
    scorePerMinute = db.Column(db.Integer)
    distanceTraveled = db.Column(db.Integer)
    teamSurvivalTime = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    kdRatio = db.Column(db.Float)
    pickupTablet = db.Column(db.Integer)
    boxesOpen = db.Column(db.Integer)
    teamWipes= db.Column(db.Integer)
    lastStandKills = db.Column(db.Integer)
    shopping = db.Column(db.Integer)
    bonusXp = db.Column(db.Integer)
    timePlayed = db.Column(db.Integer)
    percentTimeMoving = db.Column(db.Float)
    miscXp = db.Column(db.Integer)
    longestStreak = db.Column(db.Integer)
    teamPlacement = db.Column(db.Integer)
    revives = db.Column(db.Integer)
    damageDone = db.Column(db.Integer)
    damageTaken = db.Column(db.Integer)
    circle1 = db.Column(db.Integer)
    circle2 = db.Column(db.Integer)
    circle3 = db.Column(db.Integer)
    circle4 = db.Column(db.Integer)
    circle5 = db.Column(db.Integer)
    circle6 = db.Column(db.Integer)
    circle7 = db.Column(db.Integer)

    def __repr__(self):
        return f'Match: {self.matchID}, player: {self.playername}, timestamp: {self.timestamp.strftime("%m-%d-%H:%M")}'
