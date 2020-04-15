from app import app
from app.models import WeeklyStats, LifeTimeStats
from sqlalchemy import func

q = WeeklyStats.query.filter(WeeklyStats.gameMode == 'TRIO').group_by(WeeklyStats.playername).having(func.max(WeeklyStats.timestamp))


head_rows = list(vars(q[0]).keys())


print("\t".join(head_rows[1:]))

for player in q:
    stat_list = []
    player_stats = vars(player)
    del player_stats['_sa_instance_state']
    for k, v in player_stats.items():
        #print(k)
        stat_list.append(str(v))

    print("\t".join(stat_list))


