from app import app, db
from app.models import MatchStats


def get_all_matchIDs():
    return MatchStats.query.with_entities(MatchStats.matchID).all()


def add_team_contribution(self, validated_data_list):
    return validated_data_list

def get_downs(player_matches):
    circle_downs = ['circle1','circle2','circle3','circle4','circle5','circle6','circle7']
    player_downs = []
    for match_data in player_matches:
        player_cirle_downs = []
        for circle in circle_downs:
            player_cirle_downs.append(getattr(match_data, circle))
        player_downs.append(sum(player_cirle_downs))

    return player_downs


def add_contribution(matchId):
    player_matches = MatchStats.query.filter(MatchStats.matchID == matchId).all()

    property_list = ['kills', 'downs', 'damageDone', 'damageTaken', 'deaths', 'distanceTraveled', 'revives']
    for prop in property_list:
        if prop == 'downs':
            prop_single_list = get_downs(player_matches)
        else:
            prop_single_list = []
            for match_data in player_matches:
                prop_single_list.append(getattr(match_data, prop))

        team_prop_sum = sum(prop_single_list)
        for m in range(len(player_matches)):
            if prop == 'revives':
                prop = 'objectiveReviver'
            contribution_field = 'contribution_' + prop
            if team_prop_sum == 0:
                setattr(player_matches[m], contribution_field, 0.0)
                continue
            percent = round(100 / team_prop_sum * prop_single_list[m], 1)
            setattr(player_matches[m], contribution_field, percent)
            print(percent)


    db.session.commit()

all_matchIDs = get_all_matchIDs()
for matchid in all_matchIDs:
    add_contribution(matchid[0])


