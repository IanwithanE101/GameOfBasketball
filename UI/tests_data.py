from datetime import timedelta


class TestData:
    """
    Simulates an API client that returns schedule and game details.
    Prints a warning that it's using test data.

    Later, you can replace these methods with real API calls.
    """
    def __init__(self):
        print("WARNING: Using TestData class, replace with real API calls later!")

    def get_schedule(self, start_date, end_date):
        print("WARNING: Using FAKE SCHEDULE data! (TestData.get_schedule called)")
        schedule = []
        current_date = start_date
        while current_date <= end_date:
            schedule.append({
                'date': current_date,
                'home': f"Team{current_date.day}",
                'away': f"Team{current_date.day + 1}",
                'location': f"Arena {current_date.day}"
            })
            current_date += timedelta(days=1)
        return schedule

    def get_game_details(self, game_data):
        print("WARNING: Using FAKE GAME DETAILS data! (TestData.get_game_details called)")
        # Example of a more complex return structure: scoreboard & rosters
        # In reality, you'd generate or fetch real data.
        # We'll just mock them for demonstration.
        return {
            "home_score": 102,
            "away_score": 98,
            "home_players": [
                # first 5 are 'starters'
                {"name": "John Doe", "number": 11, "points": 28, "assists": 5, "rebounds": 7},
                {"name": "Player2", "number": 5, "points": 16, "assists": 2, "rebounds": 4},
                {"name": "Player3", "number": 7, "points": 10, "assists": 5, "rebounds": 2},
                {"name": "Player4", "number": 12, "points": 8,  "assists": 2, "rebounds": 9},
                {"name": "Player5", "number": 20, "points": 14, "assists": 1, "rebounds": 3},
                # bench
                {"name": "Bench1",  "number": 15, "points": 5, "assists": 0, "rebounds": 2},
                {"name": "Bench2",  "number": 23, "points": 2, "assists": 1, "rebounds": 1},
            ],
            "away_players": [
                # first 5 are 'starters'
                {"name": "Alice Jones", "number": 22, "points": 21, "assists": 7, "rebounds": 5},
                {"name": "Away2", "number": 10, "points": 12, "assists": 3, "rebounds": 6},
                {"name": "Away3", "number": 45, "points": 20, "assists": 4, "rebounds": 8},
                {"name": "Away4", "number": 9,  "points": 10, "assists": 8, "rebounds": 0},
                {"name": "Away5", "number": 14, "points": 5,  "assists": 2, "rebounds": 3},
                # bench
                {"name": "AwayBench1", "number": 19, "points": 1, "assists": 1, "rebounds": 2},
                {"name": "AwayBench2", "number": 30, "points": 0, "assists": 0, "rebounds": 1},
            ],
        }
