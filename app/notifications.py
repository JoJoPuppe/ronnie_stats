from app.device_token_handler import DeviceTokenHandler
from stats_config import WARZONE_CONFIG
import requests
import logging

LOG_FILE = WARZONE_CONFIG['LOGFILE']
logging.basicConfig(level=logging.INFO, filename=LOG_FILE, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

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
        reg_token = dev_tokener.load_token_by_name("ronnie_token")

        tokenlist = []


        if reg_token != None:
            for token in reg_token:
                token_dict = vars(token)
                tokenlist.append(token_dict['token'])

        data = {
                'registration_ids': tokenlist,
                'notification': {
                    'title': self.create_title_string(),
                    'body': self.create_body_string(),
                    },
                }

        headers = {
                'Content-Type': 'application/json',
                'Authorization': WARZONE_CONFIG['CLOUD_API_KEY']
                }

        response = requests.post('https://fcm.googleapis.com/fcm/send', json=data, headers=headers)
        logging.info(f"notification response code: {response.status_code}")
        logging.info(f"notification response body: {response.text}")


        
        





