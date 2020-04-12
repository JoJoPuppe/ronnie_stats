from get_warzone_stats import WarzoneStats
import json

data_obj = WarzoneStats("dlt_orko")
data_obj.collect_data()
json_data = data_obj.player_stats

print(json.dumps(json_data,indent=4, sort_keys=True))

