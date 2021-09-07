from app import db
from app.models import DeviceTokens


class DeviceTokenHandler():
    def __init__(self):
        pass

    def load_token_by_token(self, token):
        return DeviceTokens.query.filter(DeviceTokens.token == token).all()

    def load_token_by_name(self, playername):
        return DeviceTokens.query.filter(DeviceTokens.playername == playername).all()

    def put_token(self, reg_token, player):
        record = DeviceTokens(
                playername=player,
                token=reg_token)
        db.session.add(record)
        db.session.commit()

    def delete_all(self):
        db.session.query(DeviceTokens).delete()
        db.session.commit()

    def get_all_rows(self):
        return DeviceTokens.query.all()
                

