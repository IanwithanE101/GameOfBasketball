import json
import os
import random
from datetime import datetime, timezone

DATABASE_FILENAME = "fake_database.json"

class FakeAPI:
    def __init__(self):
        if not os.path.exists(DATABASE_FILENAME):
            self._create_empty_database()
        self._load_database()
        self._build_mappings()

    def _create_empty_database(self):
        empty_db = {
            "Teams": [],
            "Games": [],
            "Players": [],
            "Stats": []
        }
        with open(DATABASE_FILENAME, "w") as f:
            json.dump(empty_db, f, indent=4)
        print(f"Created new empty database: {DATABASE_FILENAME}")

    def _load_database(self):
        with open(DATABASE_FILENAME, "r") as f:
            self.db = json.load(f)

    def _save_database(self):
        with open(DATABASE_FILENAME, "w") as f:
            json.dump(self.db, f, indent=4)
        self._build_mappings()

    def _build_mappings(self):
        self.team_by_id = { team["TeamID"]: team for team in self.db.get("Teams", []) }
        self.player_by_id = { player["PlayerID"]: player for player in self.db.get("Players", []) }

    # ----------------
    # GETTERS
    # ----------------
    def get_schedule(self):
        """
        Returns the list of game records.
        For each game, it looks up the team names from Teams (using HomeTeamID and AwayTeamID)
        and sets "home" and "away" accordingly.
        """
        games = self.db.get("Games", [])
        for game in games:
            home_team = self.team_by_id.get(game.get("HomeTeamID"), {})
            away_team = self.team_by_id.get(game.get("AwayTeamID"), {})
            game["home"] = home_team.get("Team_Name", "Unknown")
            game["away"] = away_team.get("Team_Name", "Unknown")
        return games

    def get_all_teams(self):
        teams = [team["Team_Name"] for team in self.db.get("Teams", [])]
        return sorted(teams)

    def get_game_details(self, game):
        """
        1) Get the HomeTeamID and AwayTeamID from the given game record.
        2) For each team (home and away):
           - Find all players that belong to that TeamID.
           - For each player, find the stat record for this GameID (if it exists).
           - Compute derived stats and build a formatted line.
           - Accumulate the total team score.
        3) Return home_score, away_score, home_display, away_display, etc.
        """

        game_id = game.get("GameID")
        home_team_id = game.get("HomeTeamID")
        away_team_id = game.get("AwayTeamID")

        home_display = []
        away_display = []
        home_score = 0
        away_score = 0

        # A helper to compute points, rebounds, FG% from a stat record.
        def format_stat_line(player, stat):
            # Safely fetch numeric values (cast to int).
            two_pt_made = int(stat.get("2ptMade", 0))
            two_pt_miss = int(stat.get("2ptMiss", 0))
            three_pt_made = int(stat.get("3ptMade", 0))
            three_pt_miss = int(stat.get("3ptMiss", 0))
            ft_made = int(stat.get("FreeThrowsMade", 0))
            off_reb = int(stat.get("OffensiveRebounds", 0))
            def_reb = int(stat.get("DefensiveRebounds", 0))
            assists = int(stat.get("Assists", 0))

            points = two_pt_made * 2 + three_pt_made * 3 + ft_made
            rebounds = off_reb + def_reb

            total_made = two_pt_made + three_pt_made
            total_attempts = total_made + two_pt_miss + three_pt_miss
            fg_pct_int = int(round((total_made / total_attempts) * 100)) if total_attempts > 0 else 0
            fg_str = f"{fg_pct_int}%"

            # Last name from the player's DB record:
            last_name = player.get("Last_Name", "")
            pos = player.get("Position", "???")
            number_str = str(player.get("Jersey_Number", 0))

            # Build the final string line (adjust spacing as needed).
            # Example columns: Pos (3, left), # (2, left), Last Name (12, left),
            #                 Pts (3, right), Ast (3, right), Reb (3, right), FG% (3, right)
            line = f"{pos:<3}|{number_str:<2}|{last_name:<12}|{points:>3}|{assists:>3}|{rebounds:>3}|{fg_str:>3}"
            return line, points

        # -----------------------------
        #  HOME TEAM: players, stats
        # -----------------------------
        home_players = [p for p in self.db["Players"] if p.get("TeamID") == home_team_id]

        for player in home_players:
            # Find that player's stat record for this game (if any).
            # If there's no matching record, we use a default "all zeros" stat dict.
            stat = next(
                (s for s in self.db["Stats"] if s["GameID"] == game_id and s["PlayerID"] == player["PlayerID"]),
                None
            )
            if not stat:
                stat = {
                    "2ptMade": 0, "2ptMiss": 0, "3ptMade": 0, "3ptMiss": 0,
                    "Steals": 0, "Turnovers": 0, "Assists": 0, "Blocks": 0,
                    "Fouls": 0, "OffensiveRebounds": 0, "DefensiveRebounds": 0,
                    "FreeThrowsMade": 0, "FreeThrowsMissed": 0
                }

            line_str, pts = format_stat_line(player, stat)
            home_display.append(line_str)
            home_score += pts

        # -----------------------------
        #  AWAY TEAM: players, stats
        # -----------------------------
        away_players = [p for p in self.db["Players"] if p.get("TeamID") == away_team_id]

        for player in away_players:
            # Find that player's stat record for this game (if any).
            stat = next(
                (s for s in self.db["Stats"] if s["GameID"] == game_id and s["PlayerID"] == player["PlayerID"]),
                None
            )
            if not stat:
                stat = {
                    "2ptMade": 0, "2ptMiss": 0, "3ptMade": 0, "3ptMiss": 0,
                    "Steals": 0, "Turnovers": 0, "Assists": 0, "Blocks": 0,
                    "Fouls": 0, "OffensiveRebounds": 0, "DefensiveRebounds": 0,
                    "FreeThrowsMade": 0, "FreeThrowsMissed": 0
                }

            line_str, pts = format_stat_line(player, stat)
            away_display.append(line_str)
            away_score += pts

        # Return the final dictionary
        return {
            "game_id": game_id,
            "home_score": home_score,
            "away_score": away_score,
            "home_display": home_display,
            "away_display": away_display
        }

    # ----------------
    # SETTERS / UPDATERS
    # ----------------
    def get_team_id_by_name(self, team_name):
        for team in self.db.get("Teams", []):
            if team.get("Team_Name") == team_name:
                return team.get("TeamID")
        return None

    def create_game(self, home, away, utc_dt):
        """
        Creates a new game record with keys in the following order:
            GameID, HomeTeamID, AwayTeamID, GameDate, home, away, location
        Then creates default stat records (all 0) for every player on the involved teams.
        """
        home_team_id = self.get_team_id_by_name(home)
        away_team_id = self.get_team_id_by_name(away)
        if home_team_id is None or away_team_id is None:
            print("Error: Could not find team IDs for the selected teams.")
            return None

        game_id_str = f"GAME-{random.randint(1000, 9999)}"
        new_game = {
            "GameID": game_id_str,
            "HomeTeamID": home_team_id,
            "AwayTeamID": away_team_id,
            "GameDate": utc_dt.isoformat().replace("+00:00", "Z"),
            "home": home,
            "away": away,
        }

        self.db["Games"].append(new_game)
        self._save_database()

        # For every player belonging to either team, create a default stat record (all zeros)
        for player in self.db.get("Players", []):
            if player.get("TeamID") in [home_team_id, away_team_id]:
                new_stat_id = len(self.db.get("Stats", [])) + 1
                stat_record = {
                    "StatID": new_stat_id,
                    "PlayerID": player["PlayerID"],
                    "GameID": game_id_str,
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
                self.db["Stats"].append(stat_record)
        self._save_database()
        return new_game

    def add_temp_game(self, game_dict):
        self.db["Games"].append(game_dict)
        self._save_database()

    def add_team(self, team_record):
        self.db["Teams"].append(team_record)
        self._save_database()

    def add_player(self, player_record):
        self.db["Players"].append(player_record)
        self._save_database()

    def add_stat(self, stat_record):
        self.db["Stats"].append(stat_record)
        self._save_database()

    def remake_database(self, new_db):
        self.db = new_db
        self._save_database()

    def delete_game(self, game_id):
        # Filter out the game with the matching GameID
        original_count = len(self.db.get("Games", []))
        self.db["Games"] = [
            game for game in self.db.get("Games", [])
            if game.get("GameID") != game_id
        ]
        if len(self.db["Games"]) < original_count:
            self._save_database()
            return True
        else:
            print(f"Game with ID {game_id} not found.")
            return False
