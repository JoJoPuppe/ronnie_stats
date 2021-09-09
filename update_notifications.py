from datetime import datetime, timedelta
from app.convert_interval_stats import IntervalConverter
import json
import os.path as path
from stats_config import WARZONE_CONFIG
from app.notifications import Notification
from app.PropFirst import PropFirst

def send_notification():
    json_file_name = 'last_notifications.json'
    current_path = path.abspath(__file__)
    json_path = path.join(path.dirname(current_path), json_file_name)
    start = datetime.now().timestamp()

    if path.exists(json_path) and path.getsize(json_path) > 0:
        with open('last_notifications.json', 'r') as f:
            last_note = json.load(f)

        end = last_note['last_timestamp']

    else:
        end = start - timedelta(seconds=86400).total_seconds()

    int_converter = IntervalConverter()
    data = []

    for name in WARZONE_CONFIG['NAMES']:
        matches = int_converter.get_custom_time_stats(name, int(end), int(start))
        if matches:
            data.append([matches])

    reorder = PropFirst()
    converted_list_data = reorder.convert_data_from_list(data) 
    data_list = reorder.reorganize_batch(converted_list_data, reorder.real_data, sort=False)

    for real_data in data_list:
        prop_dict = {'kills': 0, 'deaths': 0, 'damageDone': 0, 'matches': 0}
        for pl in range(len(real_data[0])):
            player_notification = Notification(real_data[0][pl]['playername'])
            for property in real_data:
                if property[pl]['prop_name'] in prop_dict:
                    sum = 0
                    for num in property[pl]['ticks']:
                        sum += num
                    prop_dict[property[pl]['prop_name']] = sum
                    prop_dict['matches'] = len(property[pl]['ticks'])
            
            if prop_dict['matches'] > 0:
                player_notification.set_stats(prop_dict['kills'], prop_dict['deaths'], prop_dict['damageDone'], prop_dict['matches'])
                #player_notification.send_notification_report()

    with open(json_path, 'w+') as f:
        json.dump({'last_timestamp': int(start)}, f)

