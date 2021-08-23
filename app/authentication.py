import requests
import os
import logging
import json
from stats_config import WARZONE_CONFIG
from telegram.ext import Updater

LOG_FILE = WARZONE_CONFIG['LOGFILE']

# telegram bot toten
updater = Updater(token=WARZONE_CONFIG['TELEGRAM_TOKEN'],
		use_context=True)

logging.basicConfig(level=logging.INFO, filename=LOG_FILE, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')


class Authentication(object):
    def __init__(self):
        self.email = WARZONE_CONFIG['EMAIL']
        self.pw = WARZONE_CONFIG['PW']
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.cookie_file = os.path.join(self.base_path, 'auth_cookies.json')
        self.new_cookie_file = os.path.join(self.base_path, 'new_auth_cookies.json')
        self.cookies = {}
    

    def update_cookies(self):
        updated_cookies = []
        new_cookies = self.load_cookies(self.new_cookie_file)
        current_cookies = self.load_cookies(self.cookie_file)
        write_new_cookie_file = False

        if new_cookies['cookies']:
            write_new_cookie_file = True
            updated_cookies.extend(new_cookies['cookies'])
        
        if current_cookies['cookies']:
            for cookie in current_cookies['cookies']:
                if cookie['fails'] >= 8:
                    write_new_cookie_file = True
                    continue
                updated_cookies.append(cookie)


        if len(updated_cookies) <= 0:
            updater.bot.send_message(chat_id=WARZONE_CONFIG['TELEGRAM_CHAT_ID'],\
                    text="no working cookies left. please add more cookies.")
        else:
            self.cookies = {"cookies": updated_cookies}
            if write_new_cookie_file:
                with open(self.cookie_file, "w+") as f:
                    json.dump(self.cookies, f)

            try:
                pass
                #os.remove(self.new_cookie_file)
            except:
                print(f"{self.new_cookie_file}: does not exist")


    def load_cookies(self, path_to_file) -> dict:
        cookie_dict = {}
        try:
            with open(path_to_file, "r") as f:
                cookie_dict = json.load(f)
                return cookie_dict

        except IOError:
            print("File does not exist")
            return {}


    def cookies_failed(self, index: int):
        self._cookies["cookies"][index]["fails"] += 1
        with open(self.cookie_file, 'w+') as f:
            json.dump(self.cookies, f)
