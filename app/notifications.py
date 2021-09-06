import firebase_admin
from firebase_admin import messaging
from app.device_token_handler import DeviceTokenHandler


default_app = firebase_admin.initialize_app()

class Notification(object):
    def __init__(self, name: str):
        self.name = name
        self.kills = 0
        self.matches = 0
        self.deaths = 0
        self.kd = 0.0
        self.damage_done = 0

    
    def add_match(self, kills: int, deaths:int, damage_done:int):
        self.kills += kills
        self.deaths += deaths
        self.damage_done += damage_done
        self.matches += 1


    def create_title_string(self):
        return f"{self.name} played {self.matches} new matches."


    def create_body_string(self):
        kd_death = self.deaths
        if self.deaths == 0:
            kd_death = 1

        kd = round(self.kills / kd_death, 1)
        damage_match = round(self.damage_done / self.matches)

        return f"{self.kills}: Kills | {kd}: K/D | {damage_match}: Damage/Match"


    def send_notification_report(self):
        dev_tokener = DeviceTokenHandler()
        reg_token = dev_tokener.load_token("ronnie_token")

        tokenlist = []


        if reg_token != None:
            for token in reg_token:
                token_dict = vars(token)
                tokenlist.append(token_dict['token'])

            message = messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=self.create_title_string(),
                        body=self.create_body_string()
                        ),
                    tokens=tokenlist
                    )
            response = messaging.send_multicast(message)
            print(f'Successfully sent {response.success_count} messages:')
        else:
            print(f'no token yet')

        
        





