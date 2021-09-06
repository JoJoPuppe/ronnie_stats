from app import app, db
from app.models import DeviceTokens


class DeviceTokenHandler():
    def __init__(self):
        pass

    def load_token(self, token=None, playername=None):
        if token == None and playername:
            return DeviceTokens.query.filter(DeviceTokens.playername == playername).first()
        if playername == None and token:
            return DeviceTokens.query.filter(DeviceTokens.token == token).first()


    def put_token(self, reg_token, player):
        record = DeviceTokens(
                playername=player,
                token=reg_token)
        db.session.add(record)
        db.session.commit()
                

