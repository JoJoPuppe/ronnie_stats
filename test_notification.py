import requests
from app.device_token_handler import DeviceTokenHandler
from stats_config import WARZONE_CONFIG


dev_tokener = DeviceTokenHandler()
reg_token = dev_tokener.load_token(playername="ronnie_token")

print(reg_token)

tokenlist = []

if reg_token != None:
    for token in reg_token:
        token_dict = vars(token)
        tokenlist.append(token_dict['token'])

print(tokenlist)
data = {
        'registration_ids': tokenlist,
        'notification': {
            'title': 'I am from PI',
            'body': 'es gibt mich wirklich!!!!!',
            },
        }

headers = {
        'Content-Type': 'application/json',
        'Authorization': WARZONE_CONFIG['CLOUD_API_KEY']
        }

#response = requests.post('https://fcm.googleapis.com/fcm/send', data=data, headers=headers)
#print(response.status_code)
#print(response.text)

