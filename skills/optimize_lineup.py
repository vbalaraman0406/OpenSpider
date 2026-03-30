import json
from datetime import datetime
import sys

def optimize_lineup(player_data):
    active_batters = []
    bench_batters = []
    il_batters = []
    active_pitchers = []
    bench_pitchers = []
    il_pitchers = []

    for player in player_data:
        if player['status'] in ['IL', 'IL10']:
            if player['type'] == 'Batter':
                il_batters.append(player)
            else:
                il_pitchers.append(player)
        elif player['position'] == 'BN':
            if player['type'] == 'Batter':
                bench_batters.append(player)
            else:
                bench_pitchers.append(player)
        else:
            if player['type'] == 'Batter':
                active_batters.append(player)
            else:
                active_pitchers.append(player)

    recommendations = []

    # 1. Handle IL players
    if il_batters or il_pitchers:
        recommendations.append("## Injury List (IL) Recommendations\n")
        for player in il_batters:
            recommendations.append(f"- **{player['name']} ({player['position']})**: Currently on IL. Ensure they are moved to an IR slot if available to free up a roster spot.")
        for player in il_pitchers:
            recommendations.append(f"- **{player['name']} ({player['position']})**: Currently on IL. Ensure they are moved to an IR slot if available to free up a roster spot.")
        recommendations.append("\n")

    # 2. Review active lineup for today's games
    recommendations.append("## Today's Active Lineup Review\n")
    for player in active_batters:
        if player['game_time'] != 'N/A':
            recommendations.append(f"- **{player['name']} ({player['position']})**: Playing today against {player['opponent']} at {player['game_time']}. Keep in lineup.")
        else:
            recommendations.append(f"- **{player['name']} ({player['position']})**: Active, but game time/opponent not specified. Verify game status.")
    for player in active_pitchers:
        if player['game_time'] != 'N/A':
            recommendations.append(f"- **{player['name']} ({player['position']})**: Scheduled to pitch today against {player['opponent']} at {player['game_time']}. Evaluate matchup for optimal performance.")
        else:
            recommendations.append(f"- **{player['name']} ({player['position']})**: Active, but game time/opponent not specified. Verify game status.")
    recommendations.append("\n")

    # 3. Review bench players for potential swaps
    if bench_batters or bench_pitchers:
        recommendations.append("## Bench Player Review\n")
        for player in bench_batters:
            if player['game_time'] != 'N/A':
                recommendations.append(f"- **{player['name']} ({player['position']})**: On bench, playing today against {player['opponent']} at {player['game_time']}. Consider for active lineup if a starter has a poor matchup or is inactive.")
            else:
                recommendations.append(f"- **{player['name']} ({player['position']})**: On bench, game time/opponent not specified. Monitor for potential starts.")
        for player in bench_pitchers:
            if player['game_time'] != 'N/A':
                recommendations.append(f"- **{player['name']} ({player['position']})**: On bench, scheduled to pitch today against {player['opponent']} at {player['game_time']}. Consider for active lineup if an active pitcher has a poor matchup or is inactive.")
            else:
                recommendations.append(f"- **{player['name']} ({player['position']})**: On bench, game time/opponent not specified. Monitor for potential starts.")
        recommendations.append("\n")

    # General optimization tips (since I don't have real-time performance data or Statcast)
    recommendations.append("## General Optimization Tips\n")
    recommendations.append("- **Check for late-breaking news**: Always verify player status (injuries, day-off, last-minute scratches) before game time.")
    recommendations.append("- **Pitcher Matchups**: For active pitchers, consider their opponent's batting strength. Bench pitchers against high-powered offenses if possible.")
    recommendations.append("- **Weather Delays**: Be aware of potential game delays or cancellations due to weather, especially for outdoor games.")
    recommendations.append("- **Streaming**: If you have open roster spots, consider streaming pitchers with favorable matchups against weaker offenses.")

    return "\n".join(recommendations)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        player_data_json = sys.argv[1]
        player_data = json.loads(player_data_json)
    else:
        # For debugging, use the sample output from the previous step
        sample_player_data = [
  {
    "name": "Carter Jensen",
    "position": "C",
    "status": "Active",
    "opponent": "ATL",
    "game_time": "4:15 pm",
    "type": "Batter"
  },
  {
    "name": "Tyler Soderstrom",
    "position": "1B",
    "status": "Active",
    "opponent": "TOR",
    "game_time": "4:07 pm",
    "type": "Batter"
  },
  {
    "name": "Cole YoungNew",
    "position": "2B",
    "status": "Active",
    "opponent": "CLE",
    "game_time": "6:45 pm",
    "type": "Batter"
  },
  {
    "name": "Jazz Chisholm Jr.",
    "position": "3B",
    "status": "Active",
    "opponent": "SF",
    "game_time": "1:35 pm",
    "type": "Batter"
  },
  {
    "name": "Zach Neto",
    "position": "SS",
    "status": "Active",
    "opponent": "HOU",
    "game_time": "5:15 pm",
    "type": "Batter"
  },
  {
    "name": "Cody Bellinger",
    "position": "OF",
    "status": "Active",
    "opponent": "SF",
    "game_time": "1:35 pm",
    "type": "Batter"
  },
  {
    "name": "Chase DeLauterNew",
    "position": "OF",
    "status": "Active",
    "opponent": "SEA",
    "game_time": "6:45 pm",
    "type": "Batter"
  },
  {
    "name": "Giancarlo Stanton",
    "position": "OF",
    "status": "Active",
    "opponent": "SF",
    "game_time": "1:35 pm",
    "type": "Batter"
  },
  {
    "name": "Daulton Varsho",
    "position": "Util",
    "status": "Active",
    "opponent": "ATH",
    "game_time": "4:07 pm",
    "type": "Batter"
  },
  {
    "name": "Brenton Doyle",
    "position": "BN",
    "status": "Active",
    "opponent": "MIA",
    "game_time": "4:10 pm",
    "type": "Batter"
  },
  {
    "name": "Pete Alonso",
    "position": "BN",
    "status": "Active",
    "opponent": "N/A",
    "game_time": "N/A",
    "type": "Batter"
  },
  {
    "name": "Jarren Duran",
    "position": "BN",
    "status": "Active",
    "opponent": "N/A",
    "game_time": "N/A",
    "type": "Batter"
  },
  {
    "name": "Caleb Durbin",
    "position": "BN",
    "status": "Active",
    "opponent": "N/A",
    "game_time": "N/A",
    "type": "Batter"
  },
  {
    "name": "Samuel Basallo",
    "position": "BN",
    "status": "Active",
    "opponent": "N/A",
    "game_time": "N/A",
    "type": "Batter"
  },
  {
    "name": "Jackson Chourio",
    "position": "BN",
    "status": "IL10",
    "opponent": "N/A",
    "game_time": "N/A",
    "type": "Batter"
  },
  {
    "name": "Jakob Marsee",
    "position": "BN",
    "status": "Active",
    "opponent": "COL",
    "game_time": "4:10 pm",
    "type": "Batter"
  },
  {
    "name": "Ezequiel Tovar",
    "position": "BN",
    "status": "Active",
    "opponent": "MIA",
    "game_time": "4:10 pm",
    "type": "Batter"
  },
  {
    "name": "Xavier Edwards",
    "position": "BN",
    "status": "Active",
    "opponent": "COL",
    "game_time": "4:10 pm",
    "type": "Batter"
  },
  {
    "name": "Marcell Ozuna",
    "position": "BN",
    "status": "Active",
    "opponent": "N/A",
    "game_time": "N/A",
    "type": "Batter"
  },
  {
    "name": "TJ Friedl",
    "position": "BN",
    "status": "Active",
    "opponent": "N/A",
    "game_time": "N/A",
    "type": "Batter"
  },
  {
    "name": "Garrett CrochetNew",
    "position": "SP",
    "status": "Active",
    "opponent": "N/A",
    "game_time": "N/A",
    "type": "Pitcher"
  },
  {
    "name": "Max Meyer",
    "position": "SP",
    "status": "Active",
    "opponent": "COL",
    "game_time": "4:10 pm",
    "type": "Pitcher"
  },
  {
    "name": "Adrian Morejon",
    "position": "RP",
    "status": "Active",
    "opponent": "DET",
    "game_time": "6:40 pm",
    "type": "Pitcher"
  },
  {
    "name": "Garrett Whitlock",
    "position": "RP",
    "status": "Active",
    "opponent": "N/A",
    "game_time": "N/A",
    "type": "Pitcher"
  }
]
        player_data = sample_player_data

    recommendations = optimize_lineup(player_data)
    print(recommendations)
