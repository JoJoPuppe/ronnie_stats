import requests
from app.device_token_handler import DeviceTokenHandler


dev_tokener = DeviceTokenHandler()
reg_token = dev_tokener.load_token("ronnie_token")

tokenlist = []

if reg_token != None:
    for token in reg_token:
        token_dict = vars(token)
        tokenlist.append(token_dict['token'])


data = {
        'registration_ids': tokenlist,
        'notification': {
            'title': 'I am from PI',
            'body': 'es gibt mich wirklich!!!!!',
            },
        }

headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=AAAAtkktZeU:APA91bEjxIEKQQw-dw0NmPVIGwqgWbMHcFp9wiZY-Kf1ZxKyEwmurUcc3762SglyzsjfkdBaJdtfRvagyaK76-nraGHGAcn0BdBpOeUyPmiVQ_7gS2XVUvo8FFgiFi4PTUPnGteoxAiU'
        }

requests.post('https://fcm.googleapis.com/fcm/send', data=data, headers=headers)

