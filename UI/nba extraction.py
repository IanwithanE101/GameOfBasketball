"""
Script: nba_extraction_to_fake_db.py

This script uses nba_api to locate two specific NBA games:
  1. Thursday, January 23, 2025 – Pacers (home) vs Spurs (away)
  2. Saturday, January 25, 2025 – Spurs (home) vs Pacers (away)

For each game found, it fetches the traditional box score (if available),
parses player stats (using "TO" for turnovers, replacing NaN with 0),
and builds an in-memory database with the following tables:

Teams:
  - TeamID, Team_Name, City

Games:
  - GameID, HomeTeamID, AwayTeamID, GameDate (UTC)

Players:
  - PlayerID, TeamID (nullable), First_Name, Last_Name, Position, Jersey_Number

Stats:
  - StatID, PlayerID, GameID, 2ptMade, 2ptMiss, 3ptMade, 3ptMiss,
    Steals, Turnovers, Assists, Blocks, Fouls, OffensiveRebounds,
    DefensiveRebounds, FreeThrowsMade, FreeThrowsMissed

Finally, the database is written out to "fake_database.json".
"""

import json
import random
import datetime
import math
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder, boxscoretraditionalv2

DATABASE_FILENAME = "fake_database.json"

# ---------------------------------------------------------------------------
# Helper function to safely get a value, converting NaN to 0.
# ---------------------------------------------------------------------------
def safe_get(row, key):
    val = row.get(key, 0)
    if isinstance(val, float) and math.isnan(val):
        return 0
    return val

# ---------------------------------------------------------------------------
# Helper functions for nba_api extraction
# ---------------------------------------------------------------------------
def find_team_id_by_nickname(nickname):
    """Returns the nba_api team id for a given nickname (e.g. 'Pacers' or 'Spurs')."""
    all_teams = teams.get_teams()
    for t in all_teams:
        if t["nickname"].lower() == nickname.lower():
            return t["id"]
    return None

def find_game_id_for_date(team_id, opponent_nickname, game_date):
    """
    Queries LeagueGameFinder for a given team (by nba_api team id)
    on a specific date (datetime.date) and returns the GAME_ID of a game
    where the MATCHUP contains the opponent's abbreviation.
    """
    date_str = game_date.strftime("%m/%d/%Y")
    gf = leaguegamefinder.LeagueGameFinder(
        team_id_nullable=team_id,
        date_from_nullable=date_str,
        date_to_nullable=date_str
    )
    df = gf.get_data_frames()[0]
    if df.empty:
        return None

    opp_team_id = find_team_id_by_nickname(opponent_nickname)
    if not opp_team_id:
        return None

    all_team_objs = teams.get_teams()
    opp_abbrev = None
    for t in all_team_objs:
        if t["id"] == opp_team_id:
            opp_abbrev = t["abbreviation"]
            break
    if not opp_abbrev:
        return None

    subset = df[df["MATCHUP"].str.contains(opp_abbrev)]
    if subset.empty:
        return None

    return subset.iloc[0]["GAME_ID"]

def get_boxscore_stats(game_id):
    """
    Uses BoxScoreTraditionalV2 to get player stats for the game.
    Returns a dict keyed by TEAM_ABBREVIATION with a list of player records.
    Each player record includes:
         - player_name
         - ext_player_id (nba_api PLAYER_ID)
         - stats: dict with keys: 2ptMade, 2ptMiss, 3ptMade, 3ptMiss,
           Steals, Turnovers, Assists, Blocks, Fouls,
           OffensiveRebounds, DefensiveRebounds, FreeThrowsMade, FreeThrowsMissed.
    Any NaN values are replaced with 0.
    """
    bs = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
    df = bs.get_data_frames()[0]
    if df.empty:
        return None

    results = {}
    for _, row in df.iterrows():
        team_abbrev = safe_get(row, "TEAM_ABBREVIATION")
        player_name = safe_get(row, "PLAYER_NAME")
        ext_player_id = row.get("PLAYER_ID", None)
        fgm = safe_get(row, "FGM")
        fga = safe_get(row, "FGA")
        fg3m = safe_get(row, "FG3M")
        fg3a = safe_get(row, "FG3A")
        ftm = safe_get(row, "FTM")
        fta = safe_get(row, "FTA")
        two_pt_made = fgm - fg3m
        two_pt_attempts = fga - fg3a
        stats_record = {
            "2ptMade": two_pt_made,
            "2ptMiss": two_pt_attempts - two_pt_made,
            "3ptMade": fg3m,
            "3ptMiss": fg3a - fg3m,
            "Steals": safe_get(row, "STL"),
            "Turnovers": safe_get(row, "TO"),
            "Assists": safe_get(row, "AST"),
            "Blocks": safe_get(row, "BLK"),
            "Fouls": safe_get(row, "PF"),
            "OffensiveRebounds": safe_get(row, "OREB"),
            "DefensiveRebounds": safe_get(row, "DREB"),
            "FreeThrowsMade": ftm,
            "FreeThrowsMissed": fta - ftm
        }
        if team_abbrev not in results:
            results[team_abbrev] = []
        results[team_abbrev].append({
            "player_name": player_name,
            "ext_player_id": ext_player_id,
            "stats": stats_record
        })
    return results

# ---------------------------------------------------------------------------
# NBADatabase class – our in-memory mini-database
# ---------------------------------------------------------------------------
class NBADatabase:
    def __init__(self):
        self.teams = []    # List of team records
        self.games = []    # List of game records
        self.players = []  # List of player records
        self.stats = []    # List of stat records

        self.next_team_id = 1
        self.next_game_id = 1
        self.next_player_id = 1
        self.next_stat_id = 1

        # Mappings to avoid duplicates:
        self.team_mapping = {}    # external team id -> our db TeamID
        self.player_mapping = {}  # external player id -> our db PlayerID

    def add_team(self, external_team):
        ext_team_id = external_team["id"]
        if ext_team_id in self.team_mapping:
            return self.team_mapping[ext_team_id]
        team_record = {
            "TeamID": self.next_team_id,
            "Team_Name": external_team["full_name"],
            "City": external_team["city"]
        }
        self.teams.append(team_record)
        self.team_mapping[ext_team_id] = self.next_team_id
        self.next_team_id += 1
        return team_record["TeamID"]

    def add_game(self, game_info):
        game_record = {
            "GameID": game_info["GameID"],
            "HomeTeamID": game_info["HomeTeamID"],
            "AwayTeamID": game_info["AwayTeamID"],
            "GameDate": game_info["GameDate"]
        }
        self.games.append(game_record)
        return game_record["GameID"]

    def add_player(self, player_info):
        ext_player_id = player_info["ext_player_id"]
        if ext_player_id is not None and ext_player_id in self.player_mapping:
            return self.player_mapping[ext_player_id]
        player_record = {
            "PlayerID": self.next_player_id,
            "TeamID": player_info["team_id"],
            "First_Name": player_info["first_name"],
            "Last_Name": player_info["last_name"],
            "Position": player_info["position"],
            "Jersey_Number": player_info["jersey_number"]
        }
        self.players.append(player_record)
        if ext_player_id is not None:
            self.player_mapping[ext_player_id] = self.next_player_id
        self.next_player_id += 1
        return player_record["PlayerID"]

    def add_stat(self, stat_info):
        stat_record = {
            "StatID": self.next_stat_id,
            "PlayerID": stat_info["player_id"],
            "GameID": stat_info["game_id"],
            "2ptMade": stat_info["2ptMade"],
            "2ptMiss": stat_info["2ptMiss"],
            "3ptMade": stat_info["3ptMade"],
            "3ptMiss": stat_info["3ptMiss"],
            "Steals": stat_info["Steals"],
            "Turnovers": stat_info["Turnovers"],
            "Assists": stat_info["Assists"],
            "Blocks": stat_info["Blocks"],
            "Fouls": stat_info["Fouls"],
            "OffensiveRebounds": stat_info["OffensiveRebounds"],
            "DefensiveRebounds": stat_info["DefensiveRebounds"],
            "FreeThrowsMade": stat_info["FreeThrowsMade"],
            "FreeThrowsMissed": stat_info["FreeThrowsMissed"]
        }
        self.stats.append(stat_record)
        self.next_stat_id += 1
        return stat_record["StatID"]

    def to_json(self, filename):
        db = {
            "Teams": self.teams,
            "Games": self.games,
            "Players": self.players,
            "Stats": self.stats
        }
        with open(filename, "w") as f:
            json.dump(db, f, indent=4)
        print(f"Fake database saved to {filename}")

# ---------------------------------------------------------------------------
# Main function: Build the database using nba_api extraction
# ---------------------------------------------------------------------------
def main():
    db = NBADatabase()

    # Retrieve external team info for Pacers and Spurs
    all_team_objs = teams.get_teams()
    pacers = next((t for t in all_team_objs if t["nickname"].lower() == "pacers"), None)
    spurs = next((t for t in all_team_objs if t["nickname"].lower() == "spurs"), None)
    if not pacers or not spurs:
        print("ERROR: Could not find Pacers or Spurs in nba_api listings!")
        return

    # Add teams to our database; store our internal team IDs.
    db_pacers_id = db.add_team(pacers)
    db_spurs_id = db.add_team(spurs)

    # Create an unassigned player: Mystery Man
    mystery_player_info = {
        "ext_player_id": None,
        "team_id": None,
        "first_name": "Mystery",
        "last_name": "Man",
        "position": "PG",
        "jersey_number": 0
    }
    db.add_player(mystery_player_info)

    # Define two games:
    # Game 1: Thursday, January 23, 2025 – Pacers (home) vs Spurs (away)
    # Game 2: Saturday, January 25, 2025 – Spurs (home) vs Pacers (away)
    game1_date = datetime.date(2025, 1, 23)
    game2_date = datetime.date(2025, 1, 25)

    # Find game IDs via LeagueGameFinder (if available)
    game_id_1 = find_game_id_for_date(team_id=pacers["id"], opponent_nickname="Spurs", game_date=game1_date)
    game_id_2 = find_game_id_for_date(team_id=spurs["id"], opponent_nickname="Pacers", game_date=game2_date)

    # If a game is not found, we can still create a game record with default stats.
    if not game_id_1:
        game_id_1 = f"GAME-{random.randint(1000, 9999)}"
        print("WARNING: Using default game id for 01/23/2025 game.")
    if not game_id_2:
        game_id_2 = f"GAME-{random.randint(1000, 9999)}"
        print("WARNING: Using default game id for 01/25/2025 game.")

    games_to_process = [
        {
            "GameID": game_id_1,
            "home_team_ext_id": pacers["id"],   # Pacers are home in game 1
            "away_team_ext_id": spurs["id"],
            "GameDate": game1_date.isoformat() + "T00:00:00Z"
        },
        {
            "GameID": game_id_2,
            "home_team_ext_id": spurs["id"],      # Spurs are home in game 2
            "away_team_ext_id": pacers["id"],
            "GameDate": game2_date.isoformat() + "T00:00:00Z"
        }
    ]

    # Process each game: add game record and then add player stats
    for game_info in games_to_process:
        # Map external team ids to our db team ids via our mapping in NBADatabase
        home_db_id = db.team_mapping.get(game_info["home_team_ext_id"])
        away_db_id = db.team_mapping.get(game_info["away_team_ext_id"])
        game_record = {
            "GameID": game_info["GameID"],
            "HomeTeamID": home_db_id,
            "AwayTeamID": away_db_id,
            "GameDate": game_info["GameDate"]
        }
        db.add_game(game_record)
        # Fetch box score stats for this game, if available
        boxscore = get_boxscore_stats(game_info["GameID"])
        if not boxscore:
            print(f"WARNING: Box score data for game {game_info['GameID']} is empty. Creating default stat records.")
            # For every player belonging to either team, create a default stat record (all 0)
            for player in db.players:
                if player.get("TeamID") in [home_db_id, away_db_id]:
                    new_stat = {
                        "player_id": player["PlayerID"],
                        "game_id": game_info["GameID"],
                        "2ptMade": 0,
                        "2ptMiss": 0,
                        "3ptMade": 0,
                        "3ptMiss": 0,
                        "Steals": 0,
                        "Turnovers": 0,
                        "Assists": 0,
                        "Blocks": 0,
                        "Fouls": 0,
                        "OffensiveRebounds": 0,
                        "DefensiveRebounds": 0,
                        "FreeThrowsMade": 0,
                        "FreeThrowsMissed": 0
                    }
                    db.add_stat(new_stat)
            continue

        # Process box score data if available
        for team_abbrev, players_list in boxscore.items():
            # Determine which db team id corresponds to the team_abbrev
            if team_abbrev == pacers["abbreviation"]:
                team_db_id = db_pacers_id
            elif team_abbrev == spurs["abbreviation"]:
                team_db_id = db_spurs_id
            else:
                team_db_id = None
            for player_data in players_list:
                ext_player_id = player_data.get("ext_player_id")
                full_name = player_data.get("player_name", "Unknown")
                parts = full_name.split(" ", 1)
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else ""
                # If nba_api doesn't provide position/jersey, assign random for demonstration.
                position = random.choice(["PG", "SG", "SF", "PF", "C"])
                jersey_number = random.randint(0, 99)
                player_db_id = db.add_player({
                    "ext_player_id": ext_player_id,
                    "team_id": team_db_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "position": position,
                    "jersey_number": jersey_number
                })
                s = player_data["stats"]
                stat_info = {
                    "player_id": player_db_id,
                    "game_id": game_info["GameID"],
                    "2ptMade": s["2ptMade"],
                    "2ptMiss": s["2ptMiss"],
                    "3ptMade": s["3ptMade"],
                    "3ptMiss": s["3ptMiss"],
                    "Steals": s["Steals"],
                    "Turnovers": s["Turnovers"],
                    "Assists": s["Assists"],
                    "Blocks": s["Blocks"],
                    "Fouls": s["Fouls"],
                    "OffensiveRebounds": s["OffensiveRebounds"],
                    "DefensiveRebounds": s["DefensiveRebounds"],
                    "FreeThrowsMade": s["FreeThrowsMade"],
                    "FreeThrowsMissed": s["FreeThrowsMissed"]
                }
                db.add_stat(stat_info)

    # Write out the complete database to a JSON file.
    db.to_json("fake_database.json")

if __name__ == "__main__":
    main()
