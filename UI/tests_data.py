import random
from datetime import timedelta, date


class TestData:
    """
    Simulates an API client that returns schedule and game details.
    Prints a warning that it's using test data.

    Later, you can replace these methods with real API calls.
    """
    def __init__(self):
        print("WARNING: Using TestData class, replace with real API calls later!")

    def manual_add_game(self, game):
        print("WARNING: Adding manual test game to schedule.")
        if not hasattr(self, '_manual_games'):
            self._manual_games = []
        self._manual_games.append(game)

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
        if hasattr(self, '_manual_games'):
            schedule.extend(self._manual_games)
        return sorted(schedule, key=lambda g: g['date'])

    import random
    from datetime import date

    def get_game_details(self, game_data):
        print("WARNING: Using FAKE GAME DETAILS data! (TestData.get_game_details called)")

        # 1) Save the current random state
        old_state = random.getstate()

        # 2) Seed the random generator from the date, ensuring reproducibility
        #    Using date.toordinal() is a clean way to get an integer from a date
        game_seed = game_data['date'].toordinal()
        random.seed(game_seed)

        today = date.today()
        game_is_future = game_data['date'] >= today

        # Example game_id based on the date's ordinal as well
        # (so it remains stable for that date)
        game_id = game_seed

        # Scores: 0 if future, else random in [80..120]
        if game_is_future:
            home_score = 0
            away_score = 0
        else:
            home_score = random.randint(80, 120)
            away_score = random.randint(80, 120)

        def generate_player_stats(name, forced_position=None):
            positions = ["PG", "SG", "SF", "PF", "C"]
            return {
                "name": name,
                "number": random.randint(1, 99),
                "points": random.randint(0, 35),
                "assists": random.randint(0, 10),
                "rebounds": random.randint(0, 15),
                "position": forced_position if forced_position else random.choice(positions),
                "fg_pct": round(random.uniform(0.30, 0.60), 2)
            }

        # Home team: 5 starters + bench
        home_starters = [
            generate_player_stats("HomeStarter1", "PG"),
            generate_player_stats("HomeStarter2", "SG"),
            generate_player_stats("HomeStarter3", "SF"),
            generate_player_stats("HomeStarter4", "PF"),
            generate_player_stats("HomeStarter5", "C"),
        ]
        home_bench = [
            generate_player_stats("HomeBench1"),
            generate_player_stats("HomeBench2"),
        ]

        # Away team: 5 starters + bench
        away_starters = [
            generate_player_stats("AwayStarter1", "PG"),
            generate_player_stats("AwayStarter2", "SG"),
            generate_player_stats("AwayStarter3", "SF"),
            generate_player_stats("AwayStarter4", "PF"),
            generate_player_stats("AwayStarter5", "C"),
        ]
        away_bench = [
            generate_player_stats("AwayBench1"),
            generate_player_stats("AwayBench2"),
        ]

        # 3) Restore the old random state so other random calls in your app aren’t affected
        random.setstate(old_state)

        return {
            "game_id": game_id,
            "home_score": home_score,
            "away_score": away_score,
            "home_players": home_starters + home_bench,
            "away_players": away_starters + away_bench,
        }
