import json
import os
import random
from datetime import datetime, timezone

import requests

class RealAPI:
    def __init__(self):
        # Put all your normal init code here, for example:
        self.base_url = "http://localhost:5232"
        self._players_cache = {}  # optional caches
        self._stats_cache = {}  # optional caches
        # Define _team_cache as a dictionary:
        self._team_cache = {}

        # 1) Get all players for a team, sorted by Player_ID

    def get_players_for_team_sorted(self, team_id: int):
        url = f"{self.base_url}/Players"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching players: {e}")
            return []
        all_players = resp.json()  # Expecting an array of player objects.
        print("DEBUG: get_players_for_team_sorted - full response:", all_players)
        # Use the correct key: your debug shows players have 'team_ID'
        filtered = [p for p in all_players if p.get("team_ID") == team_id]
        filtered.sort(key=lambda x: x.get("Player_ID", 0))
        print("DEBUG: get_players_for_team_sorted - filtered for team", team_id, ":", filtered)
        return filtered

    def get_team_stats_for_game(self, team_id: int, game_id: int):
        url = f"{self.base_url}/Stats/Team/{team_id}/Game/{game_id}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching stats for team={team_id} in game={game_id}: {e}")
            return []
        stats = resp.json()
        print("DEBUG: get_team_stats_for_game - response for team", team_id, "in game", game_id, ":", stats)
        return stats

    def get_player_stats_for_game(self, player_id: int, game_id: int) -> dict:
        url = f"{self.base_url}/Stats/Game/{game_id}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            all_stats = resp.json()  # Expecting an array of stat objects.
        except requests.RequestException as e:
            print(f"Error fetching stats for game {game_id}: {e}")
            return None
        print("DEBUG: get_player_stats_for_game - all stats for game", game_id, ":", all_stats)
        # Filter for the player's record (using "Player_ID")
        row = next((s for s in all_stats if s.get("Player_ID") == player_id), None)
        print("DEBUG: get_player_stats_for_game - filtered stat for player", player_id, ":", row)
        return row

    def get_game_score(self, game_id: int):
        url = f"{self.base_url}/Stats/GameScore/{game_id}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching game score for game {game_id}: {e}")
            return {}
        score = resp.json()
        print("DEBUG: get_game_score - response for game", game_id, ":", score)
        return score

    def get_all_teams(self):
        url = f"{self.base_url}/Teams"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error calling {url}: {e}")
            return []
        return resp.json()

    def get_schedule(self):
        url = f"{self.base_url}/Games"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching games from {url}: {e}")
            return []
        games = resp.json()
        for game in games:
            home_id = game.get("Home_ID")
            away_id = game.get("Away_ID")
            home_name = self._get_team_name_by_id(home_id) if home_id else "Unknown"
            away_name = self._get_team_name_by_id(away_id) if away_id else "Unknown"
            game["home"] = home_name
            game["away"] = away_name
        return games

    def _get_team_name_by_id(self, team_id):
        if team_id in self._team_cache:
            return self._team_cache[team_id]
        url = f"{self.base_url}/Teams/{team_id}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching team {team_id} from {url}: {e}")
            self._team_cache[team_id] = "Unknown"
            return "Unknown"
        data = resp.json()
        team_name = data.get("Team_Name", "Unknown")
        self._team_cache[team_id] = team_name
        return team_name

    # (Optional) If you want a method to fetch the scoreboard from /Stats/GameScore/{gameId}:
    def get_game_score(self, game_id: int):
        """
        If your backend has an endpoint that returns the live score for a game,
        e.g. GET /Stats/GameScore/15 => { "GameId":15, "HomeTeamScore":72, "AwayTeamScore":68 }
        return that object. Adjust key names if needed.
        """
        url = f"{self.base_url}/Stats/GameScore/{game_id}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    def get_all_teams(self):
        """
        Makes an HTTP GET request to retrieve all teams (TeamDTOs).
        Adjust the path if your endpoint is /Team or /api/Team, etc.
        """
        url = f"{self.base_url}/Teams"
        # If your controller route is [Route("api/[controller]")], it might be f"{self.base_url}/api/Teams" instead.
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Will raise an exception if status is 4xx/5xx
        except requests.RequestException as e:
            print(f"Error calling {url}: {e}")
            return []  # or re-raise, or handle as you wish

        # If success, parse JSON (should be a list of TeamDTO)
        teams_json = response.json()  # e.g. [{ "team_ID": 1, "team_Name": "...", ... }, ...]
        return teams_json  # or you can transform that into just names if you prefer

    # ----------------
    # GETTERS
    # ----------------
    def get_schedule(self):
        """
        Fetches all games from the API (like GET /Games),
        then for each game, look up the home/away team name by ID
        and store them in game["home"] / game["away"].
        Returns a list of game dicts, each like:
          {
            "game_ID": 2,
            "home_ID": 5,
            "away_ID": 6,
            "game_Date": "2025-03-22T16:00:00",
            "home": "sandro",
            "away": "Bilitski"
          },
          ...
        just like the FakeAPI version did, but now from real data.
        """
        url = f"{self.base_url}/Games"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching games from {url}: {e}")
            return []

        # This should be a list of game objects, e.g.
        # [ { "game_ID": 2, "home_ID":5, "away_ID":6, "game_Date": ... }, ... ]
        games = resp.json()

        for game in games:
            home_id = game.get("home_ID")
            away_id = game.get("away_ID")

            # Get the team names from the helper method:
            home_name = self._get_team_name_by_id(home_id) if home_id else "Unknown"
            away_name = self._get_team_name_by_id(away_id) if away_id else "Unknown"

            # Add them to the game dict
            game["home"] = home_name
            game["away"] = away_name

        return games

    def _get_team_name_by_id(self, team_id):
        """
        Helper method to fetch a single team by its ID.
        Cache the results so repeated requests for the same ID won't re-fetch.
        Expects the API to return JSON like:
          {
            "team_ID": 7,
            "team_Name": "Duke",
            "team_City": "Pittsburgh",
            ...
          }
        """
        if team_id in self._team_cache:
            return self._team_cache[team_id]

        url = f"{self.base_url}/Teams/{team_id}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching team {team_id} from {url}: {e}")
            self._team_cache[team_id] = "Unknown"
            return "Unknown"

        data = resp.json()  # e.g. { "team_ID":7, "team_Name":"Duke", ...}
        team_name = data.get("team_Name", "Unknown")
        self._team_cache[team_id] = team_name
        return team_name

    def get_all_teams(self):
        """
        GET /Teams returns JSON like:
        [
          { "team_ID": 5, "team_Name": "sandro", "team_City": "Johnstown" },
          { "team_ID": 6, "team_Name": "Bilitski", "team_City": "Johnstown" },
          ...
        ]
        We'll extract the 'team_Name' from each and return a sorted list of names.
        """
        url = f"{self.base_url}/Teams"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raises an error if HTTP status is 4xx or 5xx
        except requests.RequestException as e:
            print(f"Error calling {url}: {e}")
            # Return an empty list (or handle differently)
            return []

        # response.json() should be the list of teams
        teams_data = response.json()  # e.g. [{ "team_ID": 5, "team_Name": "sandro", ...}, ...]

        # Extract just the team names
        team_names = [team["team_Name"] for team in teams_data]

        # Sort the list of names before returning
        return sorted(team_names)

    def get_game_details(self, game):
        """
        1) Get home_team_id and away_team_id from the game dictionary.
        2) Fetch the list of players for each team.
        3) Fetch the stats for each team in that game (via /Stats/Team/{teamId}/Game/{gameId}).
        4) For each player, if a stat row exists use it; otherwise, use zeroed stats.
        5) Compute final lines & accumulate points.
        6) Return a dictionary with game_id, home_score, away_score, and display lines.
        """
        # Use the keys as returned by your API.
        game_id = game.get("game_ID")
        home_team_id = game.get("home_ID")
        away_team_id = game.get("away_ID")

        home_display = []
        away_display = []
        home_score = 0
        away_score = 0

        # Get players using the lowercase keys (as returned by the API)
        home_players = self._get_players_for_team(home_team_id) if home_team_id else []
        away_players = self._get_players_for_team(away_team_id) if away_team_id else []

        # Get stat lists for each team.
        home_stats_list = self._get_team_stats_for_game(home_team_id, game_id) if home_team_id and game_id else []
        away_stats_list = self._get_team_stats_for_game(away_team_id, game_id) if away_team_id and game_id else []

        # Build stat mapping by player ID.
        # Check both "Player_ID" (from stat objects) and "player_ID"
        home_stats_dict = {(s.get("Player_ID") or s.get("player_ID")): s for s in home_stats_list}
        away_stats_dict = {(s.get("Player_ID") or s.get("player_ID")): s for s in away_stats_list}

        def format_stat_line(player, stat):
            # Use keys from stat objects (which are capitalized)
            two_pt_made = stat.get("Two_Points_Made", 0)
            two_pt_miss = stat.get("Two_Points_Missed", 0)
            three_pt_made = stat.get("Three_Points_Made", 0)
            three_pt_miss = stat.get("Three_Points_Missed", 0)
            ft_made = stat.get("Free_Throw_Made", 0)
            off_reb = stat.get("Off_Rebounds", 0)
            def_reb = stat.get("Def_Rebounds", 0)
            assists = stat.get("Assists", 0)
            points = (three_pt_made * 3) + (two_pt_made * 2) + ft_made
            rebounds = off_reb + def_reb
            total_made = two_pt_made + three_pt_made
            total_attempts = total_made + two_pt_miss + three_pt_miss
            fg_pct_int = int(round((total_made / total_attempts) * 100)) if total_attempts > 0 else 0
            fg_str = f"{fg_pct_int}%"

            # Use keys from player objects (which are lowercase)
            last_name = player.get("last_Name", "")
            pos_id = player.get("position_ID", "???")
            number_str = str(player.get("jersey_Number", 0))

            line = f"{pos_id:<3}|{number_str:<2}|{last_name:<12}|{points:>3}|{assists:>3}|{rebounds:>3}|{fg_str:>3}"
            return line, points

        # Process home team players.
        for player in home_players:
            pid = player.get("player_ID")
            stat = home_stats_dict.get(pid, {
                "Two_Points_Made": 0, "Two_Points_Missed": 0,
                "Three_Points_Made": 0, "Three_Points_Missed": 0,
                "Free_Throw_Made": 0, "Free_Throw_Missed": 0,
                "Steals": 0, "Turnovers": 0, "Assists": 0, "Blocks": 0,
                "Fouls": 0, "Off_Rebounds": 0, "Def_Rebounds": 0
            })
            line_str, pts = format_stat_line(player, stat)
            home_display.append(line_str)
            home_score += pts

        # Process away team players.
        for player in away_players:
            pid = player.get("player_ID")
            stat = away_stats_dict.get(pid, {
                "Two_Points_Made": 0, "Two_Points_Missed": 0,
                "Three_Points_Made": 0, "Three_Points_Missed": 0,
                "Free_Throw_Made": 0, "Free_Throw_Missed": 0,
                "Steals": 0, "Turnovers": 0, "Assists": 0, "Blocks": 0,
                "Fouls": 0, "Off_Rebounds": 0, "Def_Rebounds": 0
            })
            line_str, pts = format_stat_line(player, stat)
            away_display.append(line_str)
            away_score += pts

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
    def _get_players_for_team(self, team_id):
        url = f"{self.base_url}/Players"
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Error fetching players: {resp.status_code} {resp.text}")
            return []
        all_players = resp.json()  # e.g. [ { "player_ID":1, "team_ID":5, "last_Name":"Smith", ...}, ... ]
        # Filter the list
        return [p for p in all_players if p.get("team_ID") == team_id]

    def get_team_id_by_name(self, team_name):
        """
        Example: calls GET /Teams, finds a team whose 'team_Name' matches.
        Return the integer Team_ID or None if not found.
        """
        url = f"{self.base_url}/Teams"
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Error fetching teams: {resp.status_code} {resp.text}")
            return None
        all_teams = resp.json()  # e.g. [ { "team_ID":5,"team_Name":"sandro"...}, ... ]
        for t in all_teams:
            if t["team_Name"].lower() == team_name.lower():
                return t["team_ID"]
        return None

    def create_game(self, home, away, dt_value):
        """
        1) If dt_value is naive (no tzinfo), assume it's local New York time.
        2) Convert local time to UTC.
        3) Format the UTC time with microseconds + 'Z'.
        4) POST /Games to store in the DB as real UTC.

        Example usage:
            local_dt = datetime(2025, 3, 30, 20, 0)   # 8pm, naive
            new_game = real_api.create_game("HomeName", "AwayName", local_dt)
        """
        # --------------------------------
        # A) Ensure dt_value is local-aware
        # --------------------------------
        if dt_value.tzinfo is None:
            # If it's naive, attach America/New_York
            local_zone = ZoneInfo("America/New_York")
            dt_value = dt_value.replace(tzinfo=local_zone)

        # --------------------------------
        # B) Convert local → UTC
        # --------------------------------
        utc_dt = dt_value.astimezone(timezone.utc)

        # For debugging, print so you confirm times
        print(f"[create_game] Input local dt: {dt_value}, converted to UTC: {utc_dt}")

        # --------------------------------
        # C) Format the final string
        # --------------------------------
        fancy_zulu_str = utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        # Now look up the team IDs in your real DB
        home_team_id = self.get_team_id_by_name(home)
        away_team_id = self.get_team_id_by_name(away)
        if home_team_id is None or away_team_id is None:
            print("Error: Could not find team IDs for the selected teams.")
            return None

        # Build payload for your ASP.NET /Games endpoint
        payload_game = {
            "Home_ID": home_team_id,
            "Away_ID": away_team_id,
            "Game_Date": fancy_zulu_str  # Real UTC in ISO 8601
        }

        # --------------------------------
        # D) POST to /Games
        # --------------------------------
        url = f"{self.base_url}/Games"
        resp = requests.post(url, json=payload_game)
        if resp.status_code not in (200, 201):
            print(f"Error creating game: {resp.status_code} {resp.text}")
            return None

        created_game = resp.json()
        print(f"Created game {created_game['game_ID']} with date {created_game['game_Date']} in DB.")
        return created_game

    def delete_game(self, game_id):
        """
        Calls DELETE /Games/{game_id} on the ASP.NET API to remove the game from the DB.
        Returns True on success, False on error.
        """
        url = f"{self.base_url}/Games/{game_id}"
        response = requests.delete(url)
        if response.status_code in (200, 204):
            return True
        else:
            print(f"Error deleting game {game_id}: {response.status_code} {response.text}")
            return False

    def _get_players_for_team(self, team_id):
        """
        Example: calls GET /Players, filters by team_ID, or if you have
        GET /Teams/{teamId}/Players, use that instead.
        """
        url = f"{self.base_url}/Players"
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Error fetching players: {resp.status_code} {resp.text}")
            return []
        all_players = resp.json()  # e.g. [ { "player_ID":1,"team_ID":5,...}, ... ]
        return [p for p in all_players if p.get("team_ID") == team_id]


    def _get_team_stats_for_game(self, team_id, game_id):
        """
        We can call GET /Stats/Team/{teamId}/Game/{gameId} which returns a list of stat objects for
        every player on that team in that game. For example:
          [
            {
              "stat_ID": 12,
              "player_ID": 42,
              "game_ID": 7,
              "three_Points_Made": 2,
              "three_Points_Missed": 5,
              ...
            },
            ...
          ]
        We'll store it in a cache so we don't re-fetch unnecessarily.
        """

        if not team_id or not game_id:
            return []

        cache_key = (team_id, game_id)
        if cache_key in self._stats_cache:
            return self._stats_cache[cache_key]

        url = f"{self.base_url}/Stats/Team/{team_id}/Game/{game_id}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching stats from {url}: {e}")
            self._stats_cache[cache_key] = []
            return []

        stat_list = resp.json()
        # Cache it
        self._stats_cache[cache_key] = stat_list
        return stat_list

    def update_player_stats(self, game_id: int, player_id: int, action: str) -> None:
        """
        Posts an incremental StatCreateDTO to the StatsController to update
        or create a row for (player_id, game_id) by incrementing the relevant fields.

        The action can be something like:
          "2pt_make", "2pt_miss", "3pt_make", "3pt_miss",
          "ft_make", "ft_miss", "rebound", "steal", "TO",
          "assist", "block", "foul", etc.

        If you need more specialized variants (e.g. "ft_make_2" for 2 free throws),
        you'll see an example of how to parse that at the bottom.
        """

        # 1) Build a base payload for StatCreateDTO, with all fields 0
        #    (matching the property names in your ASP.NET StatCreateDTO).
        body = {
            "player_ID": player_id,
            "game_ID": game_id,
            "three_Points_Made": 0,
            "three_Points_Missed": 0,
            "two_Points_Made": 0,
            "two_Points_Missed": 0,
            "free_Throw_Made": 0,
            "free_Throw_Missed": 0,
            "steals": 0,
            "turnovers": 0,
            "assists": 0,
            "blocks": 0,
            "fouls": 0,
            "off_Rebounds": 0,
            "def_Rebounds": 0
        }

        # 2) Figure out which field(s) to increment based on 'action'
        #    We'll do a simple mapping.
        #    For rebounds, you might or might not differentiate offensive vs defensive.
        #    Below, "rebound" will just increment defensive rebounds by 1 for example.
        if action == "2pt_make":
            body["two_Points_Made"] = 1
        elif action == "2pt_miss":
            body["two_Points_Missed"] = 1
        elif action == "3pt_make":
            body["three_Points_Made"] = 1
        elif action == "3pt_miss":
            body["three_Points_Missed"] = 1
        elif action == "ft_make":
            body["free_Throw_Made"] = 1
        elif action == "ft_miss":
            body["free_Throw_Missed"] = 1
        elif action == "rebound":
            # Could choose off_Rebounds or def_Rebounds. Let's pick def_Rebounds for a basic example.
            body["def_Rebounds"] = 1
        elif action == "steal":
            body["steals"] = 1
        elif action == "TO":
            body["turnovers"] = 1
        elif action == "assist":
            body["assists"] = 1
        elif action == "block":
            body["blocks"] = 1
        elif action == "foul":
            body["fouls"] = 1

        # Example: If you want to handle "ft_make_2" or "ft_make_3" for multiple made free throws:
        # elif action.startswith("ft_make_"):
        #     # e.g. action == "ft_make_2"
        #     count_str = action.split("_")[-1]
        #     made_count = int(count_str)
        #     body["free_Throw_Made"] = made_count

        # 3) Send the POST request to /Stats. This will increment (or create) as needed.
        url = f"{self.base_url}/Stats"
        try:
            resp = requests.post(url, json=body)
            resp.raise_for_status()



            # On success, the server returns 201 (or 200) with the updated/created StatDTO
            print(f"Stats updated successfully: {action} => (Game={game_id}, Player={player_id})")
        except requests.RequestException as ex:
            print(f"Error posting stat update: {ex}")
            # You might pop up a messagebox or log an error here