from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def fetch_fpl_data():
    """Fetch FPL static data."""
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def fetch_team_data(team_id, event_id):
    """Fetch team picks for a specific event."""
    url = f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{event_id}/picks/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def fetch_team_summary(team_id):
    """Fetch overall summary of a team."""
    url = f"https://fantasy.premierleague.com/api/entry/{team_id}/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    team_id = data.get('teamId')
    event_id = 1  # Starting event (GW1)

    # Fetch core FPL data
    fpl_data = fetch_fpl_data()
    elements = {player['id']: player for player in fpl_data['elements']}
    
    # Fetch team data
    team_data = fetch_team_data(team_id, event_id)
    
    # Fetch team summary
    summary = fetch_team_summary(team_id)

    # Initialize variables
    outfield_score = 0
    sub_score = 0
    captain = ""
    captain_score = 0
    vicecaptain = ""
    vicecaptain_score = 0
    highest_scorer = ""
    highest_score = 0
    total_assists = 0
    total_goals = 0
    total_bonus = 0
    total_reds = 0
    total_yellows = 0
    total_xa = 0.0
    total_xg = 0.0

    # Process team picks
    picks = team_data['picks']
    player_array = []
    for pick in picks:
        player = elements.get(pick['element'])
        if not player:
            continue
        multiplier = pick['multiplier']
        total_points = player['total_points'] * multiplier

        # Captains and Vice Captains
        if pick['is_captain']:
            captain = player['web_name']
            captain_score = total_points
        elif pick['is_vice_captain']:
            vicecaptain = player['web_name']
            vicecaptain_score = total_points

        # Track highest scorer
        if total_points > highest_score:
            highest_score = total_points
            highest_scorer = player['web_name']

        # Calculate scores and stats
        if len(player_array) < 11:  # Starting 11
            outfield_score += total_points
        else:  # Substitutes
            sub_score += total_points

        total_assists += player.get('assists', 0)
        total_goals += player.get('goals_scored', 0)
        total_bonus += player.get('bonus', 0)
        total_reds += player.get('red_cards', 0)
        total_yellows += player.get('yellow_cards', 0)
        total_xa += float(player.get('expected_assists', 0))
        total_xg += float(player.get('expected_goals', 0))

        player_array.append({
            'name': player['web_name'],
            'points': total_points,
            'is_captain': pick['is_captain'],
            'is_vice_captain': pick['is_vice_captain']
        })

    # Calculate additional stats
    average_sub_score = sub_score / 4 if sub_score else 0
    score_to_add_from_subs = average_sub_score  # Simplified logic

    # Final calculations
    what_if_score = outfield_score + score_to_add_from_subs

    # Prepare response
    response = {
        'teamName': summary['player_first_name'],
        'currentActual': summary['summary_overall_points'],
        'currentTransfers': summary['last_deadline_total_transfers'],
        'currentValue': summary['last_deadline_value'] / 10,
        'currentRank': summary['summary_overall_rank'],
        'outfieldScore': outfield_score,
        'subScore': sub_score,
        'captain': captain,
        'captainScore': captain_score,
        'highestScorer': highest_scorer,
        'highestScore': highest_score,
        'totalAssists': total_assists,
        'totalGoals': total_goals,
        'totalBonus': total_bonus,
        'totalReds': total_reds,
        'totalYellows': total_yellows,
        'totalXA': round(total_xa, 2),
        'totalXG': round(total_xg, 2),
        'whatIfScore': what_if_score,
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
