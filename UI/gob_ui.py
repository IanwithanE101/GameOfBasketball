import random
import tkinter as tk
import os
from tkinter import ttk
from PIL import Image, ImageTk, ImageFont, ImageDraw
from datetime import date, timedelta, datetime, timezone
from fake_api import FakeAPI
from zoneinfo import ZoneInfo

UI_ELEMENTS = "GOB UI ELEMENTS"

class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Basketball Manager")
        self.default_width = 1100
        self.default_height = 800
        self.minsize(1100,800)
        self.geometry("1100x800")

        # ===================== Window & Style Setup =====================
        self.set_window_icon()
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure('Default.TButton', background='#DDDDDD', foreground='black', padding=5)
        style.configure('Past.TButton', background='#AAAAAA', foreground='black', padding=5)
        style.map('Past.TButton', background=[('active', '#999999')])
        style.configure('Selected.TButton', background='lightblue', foreground='black', padding=5)
        style.map('Selected.TButton', background=[('active', '#87CEFA')])

        # ==================== Setup =====================
        self.test_data = FakeAPI()

        # ===================== Tabs =====================
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        # ===================== Schedule Tab =====================
        self.schedule_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.schedule_tab, text='Schedule')

        # Layout: left 25% (schedule), right 75% (details)
        self.schedule_frame = ttk.Frame(self.schedule_tab)
        self.schedule_frame.pack(fill="both", expand=True)

        # ---------- LEFT: Scrollable Schedule ----------
        self.schedule_list_frame = ttk.Frame(self.schedule_frame, width=275)
        self.schedule_list_frame.pack(side="left", fill="both")
        self.schedule_list_frame.pack_propagate(False)  # Prevent the frame from resizing to its content
        self.schedule_canvas = tk.Canvas(self.schedule_list_frame, bg="white")
        self.schedule_scrollbar = ttk.Scrollbar(self.schedule_list_frame, orient="vertical",command=self.schedule_canvas.yview)
        self.scrollable_schedule_frame = tk.Frame(self.schedule_canvas, bg="white")
        self.scrollable_schedule_frame.bind("<Configure>",lambda e: self.schedule_canvas.configure(scrollregion=self.schedule_canvas.bbox("all")))
        self.scrollable_window = self.schedule_canvas.create_window((0, 0), window=self.scrollable_schedule_frame, anchor="nw")
        self.schedule_canvas.configure(yscrollcommand=self.schedule_scrollbar.set)
        self.schedule_canvas.pack(side="left", fill="both", expand=True)
        self.schedule_scrollbar.pack(side="right", fill="y")

        # ---------- RIGHT: Game Details + Creation Form ----------
        self.details_box = ttk.Frame(self.schedule_frame, relief="sunken", borderwidth=2)
        self.details_box.pack(side="left", fill="both", expand=True)
        # Top 75%: Detail preview
        self.details_top = ttk.Frame(self.details_box)
        self.details_top.pack(fill="both", expand=True)
        # Bottom 25%: Game creation form
        self.details_bottom = ttk.Frame(self.details_box)
        self.details_bottom.pack(fill="x", pady=5)

        # ----- TOP: Game Preview Panel -----
        self.details_container = ttk.Frame(self.details_top)
        self.details_container.pack(expand=True)
        self.details_placeholder = ttk.Label(self.details_container, text="Click a game to view details", font=("Consolas", 14, "italic"))
        self.details_placeholder.pack(anchor="center", expand=True)

        # ----- BOTTOM: Game Creation Form (button placed inline) -----
        self.create_game_form = ttk.Frame(self.details_bottom)
        self.create_game_form.pack(anchor="center", pady=5)
        ttk.Label(self.create_game_form, text="Create New Game", font=("Consolas", 12, "bold")).grid(row=0, column=0, columnspan=4, pady=(5,5))
        ttk.Label(self.create_game_form, text="Home Team:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.home_team_var = tk.StringVar()
        self.home_dropdown = ttk.Combobox(self.create_game_form, textvariable=self.home_team_var, state="readonly")
        self.home_dropdown['values'] = self.test_data.get_all_teams()
        self.home_dropdown.grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(self.create_game_form, text="Away Team:").grid(row=1, column=2, sticky="e", padx=5, pady=2)
        self.away_team_var = tk.StringVar()
        self.away_dropdown = ttk.Combobox(self.create_game_form, textvariable=self.away_team_var, state="readonly")
        self.away_dropdown['values'] = self.test_data.get_all_teams()
        self.away_dropdown.grid(row=1, column=3, padx=5, pady=2)
        ttk.Label(self.create_game_form, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.date_entry = ttk.Entry(self.create_game_form)
        self.date_entry.insert(0, str(date.today() + timedelta(days=1)))
        self.date_entry.grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(self.create_game_form, text="Time (HH:MM AM/PM):").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.time_entry = ttk.Entry(self.create_game_form)
        self.time_entry.insert(0, "06:00 PM")
        self.time_entry.grid(row=3, column=1, padx=5, pady=2)
        # New code: Two vertically–stacked buttons in the creation form
        self.create_button = ttk.Button(self.create_game_form, text="Create Game", command=self.create_new_game)
        self.create_button.grid(row=2, column=2, columnspan=2, padx=5, pady=(2, 2))
        self.delete_button = ttk.Button(self.create_game_form, text="Delete Game", command=self.delete_game)
        self.delete_button.grid(row=3, column=2, columnspan=2, padx=5, pady=(2, 2))

        # ===================== Game Tab (Scorekeeping) =====================
        self.game_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.game_tab, text='Game')

        # Create a container that will be updated with game details (e.g., players, jerseys, stat buttons).
        self.game_ui_container = ttk.Frame(self.game_tab)
        self.game_ui_container.pack(fill="both", expand=True, padx=10, pady=10)

        # ===================== Teams Tab =====================
        teams_tab = ttk.Frame(self.notebook)
        self.notebook.add(teams_tab, text='Teams')
        ttk.Label(teams_tab, text="Teams:", font=("Consolas", 14, "bold")).pack(pady=10)
        for team in self.test_data.get_all_teams():
            ttk.Label(teams_tab, text=team, font=("Consolas", 12)).pack(anchor="w", padx=10, pady=2)

        # ===================== Final Setup =====================
        self.selected_game_index = None
        self.game_buttons = []
        self.build_schedule_contents()
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self._enable_scroll_wheel()

    # ======================================================
    # BUILD SCHEDULE CONTENTS
    # ======================================================
    def build_schedule_contents(self):
        from_zone = timezone.utc
        to_zone = ZoneInfo("America/New_York")
        self.clear_schedule_ui()
        # Sort games by GameDate (using our new key)
        games = sorted(self.test_data.get_schedule(), key=lambda g: datetime.fromisoformat(g["GameDate"].replace("Z", "+00:00")))
        for idx, game in enumerate(games):
            utc_dt = datetime.fromisoformat(game["GameDate"].replace("Z", "+00:00")).astimezone(to_zone)
            is_past = (datetime.now(to_zone) - utc_dt).total_seconds() > 7200
            style_to_use = 'Past.TButton' if is_past else 'Default.TButton'
            day_str = utc_dt.strftime("%Y-%m-%d")
            time_str = utc_dt.strftime("%I:%M %p").lstrip("0")
            frame = ttk.Frame(self.scrollable_schedule_frame, width=250, height=60)
            frame.pack_propagate(False)
            frame.pack(fill="x", pady=5, padx=8)
            btn_text = f"{game.get('home', 'Unknown')} vs {game.get('away', 'Unknown')}"
            btn = ttk.Button(frame, text=btn_text, style=style_to_use, width=35, command=lambda idx=idx: self.select_game(idx))
            btn.pack(anchor="w", ipady=6)
            ttk.Label(frame, text=f"{day_str} {time_str}", font=("Consolas", 9), width=35).pack(anchor="w", padx=10)
            self.game_buttons.append((btn, is_past, game))

    def display_column_headers(self, parent, is_starter=False):
        # Columns: Pos (3 left), # (2 left), Name (12 left), Pts (3 right), Ast (3 right), Reb (3 right), FG% (3 right)
        font_used = ("Consolas", 12, "bold") if is_starter else ("Consolas", 10)
        headers = f"{'Pos':<3}|{'#':<2}|{' Name':<15}|{'Pts':>3}|{'Ast':>3}|{'Reb':>3}|{'FG%':>3}"
        ttk.Label(parent, text=headers, font=font_used).pack(anchor="w", padx=5)

    def select_game(self, index):
        if self.selected_game_index is not None:
            old_btn, old_is_past, _ = self.game_buttons[self.selected_game_index]
            old_btn.configure(style='Past.TButton' if old_is_past else 'Default.TButton')
        btn, is_past, game_data = self.game_buttons[index]
        btn.configure(style='Selected.TButton')
        self.selected_game_index = index
        # Fetch game details from FakeAPI (which now returns home_display and away_display)
        details = self.test_data.get_game_details(game_data)
        self.selected_game_id = details["game_id"]
        self.update_game_details_ui(game_data, details)

    def _enable_scroll_wheel(self):
        self.schedule_canvas.bind("<Enter>", lambda e: self.schedule_canvas.focus_set())

    def set_window_icon(self):
        ico_path = os.path.join(UI_ELEMENTS, "icon.ico")
        png_path = os.path.join(UI_ELEMENTS, "icon.png")
        if os.path.exists(ico_path):
            self.iconbitmap(ico_path)
        elif os.path.exists(png_path):
            from PIL import Image
            img = Image.open(png_path).resize((32, 32), Image.Resampling.LANCZOS)
            icon_img = ImageTk.PhotoImage(img)
            self._icon_image = icon_img
            self.iconphoto(False, icon_img)

    def on_tab_changed(self, event):
        tab_text = self.notebook.tab(self.notebook.select(), 'text')
        if tab_text == 'Schedule':
            self.bind_all("<MouseWheel>", self._on_mousewheel_global_win)
        else:
            self.unbind_all("<MouseWheel>")
        if tab_text == 'Game':
            # Check if the selected game has changed or if a reset is required.
            if not hasattr(self, 'last_selected_game_id'):
                self.last_selected_game_id = None
            if self.selected_game_id != self.last_selected_game_id or getattr(self, '_need_reset', False):
                self.update_game_ui()
                self.last_selected_game_id = self.selected_game_id
                self._need_reset = False

    def update_game_ui(self):
        # First, if a previous stat_detail_frame exists, destroy it.
        if hasattr(self, 'stat_detail_frame'):
            try:
                self.stat_detail_frame.destroy()
            except tk.TclError:
                pass
            del self.stat_detail_frame

        # Clear the entire game_ui_container to rebuild it.
        for widget in self.game_ui_container.winfo_children():
            widget.destroy()

        # Retrieve the full game record using the selected game ID.
        if not hasattr(self, 'selected_game_id') or not self.selected_game_id:
            print("No game selected to update.")
            return
        game = next((g for g in self.test_data.get_schedule() if g["GameID"] == self.selected_game_id), None)
        if not game:
            print("Game record not found!")
            return

        # Get team IDs and on-court players.
        home_team_id = game.get("HomeTeamID")
        away_team_id = game.get("AwayTeamID")
        home_players = [p for p in self.test_data.db["Players"] if p.get("TeamID") == home_team_id][:5]
        away_players = [p for p in self.test_data.db["Players"] if p.get("TeamID") == away_team_id][:5]

        # Build currentLineup (on-court players) and bench (remaining players).
        self.currentLineup = [p["PlayerID"] for p in home_players + away_players]
        self.bench = {}
        for tid in [home_team_id, away_team_id]:
            full_roster = [p["PlayerID"] for p in self.test_data.db["Players"] if p.get("TeamID") == tid]
            self.bench[tid] = [pid for pid in full_roster if pid not in self.currentLineup]

        # Create header label.
        header = ttk.Label(self.game_ui_container, text=f"{game['home']} vs {game['away']}",
                           font=("Consolas", 16, "bold"))
        header.pack(pady=5)

        # Create players frame.
        players_frame = ttk.Frame(self.game_ui_container)
        players_frame.pack(fill="x", padx=10, pady=10)

        # Create a fresh stat detail frame (empty) inside the Game tab.
        self.stat_detail_frame = ttk.LabelFrame(self.game_ui_container, text="")
        self.stat_detail_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Left frame for home players.
        home_frame = ttk.Frame(players_frame)
        home_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        # Vertical separator.
        separator = tk.Frame(players_frame, width=2, bg="black")
        separator.grid(row=0, column=1, sticky="ns")
        # Right frame for away players.
        away_frame = ttk.Frame(players_frame)
        away_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        players_frame.columnconfigure(0, weight=1)
        players_frame.columnconfigure(2, weight=1)

        def create_player_row(parent, player):
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill="x", pady=2)
            if player["PlayerID"] not in self.currentLineup:
                self.currentLineup.append(player["PlayerID"])
            jersey_img = self.generate_jersey_image(player["Jersey_Number"])
            if jersey_img:
                jersey_label = ttk.Label(row_frame, image=jersey_img)
                jersey_label.image = jersey_img
                jersey_label.pack(side="left", padx=2)
                jersey_label.bind("<Button-1>", lambda e: self.on_stat_button(player, "jersey"))
            else:
                ttk.Label(row_frame, text=str(player["Jersey_Number"]), font=("Consolas", 10)) \
                    .pack(side="left", padx=2)
            name_label = ttk.Label(row_frame, text=f"{player['Last_Name']:<15}", font=("Consolas", 10), width=15)
            name_label.pack(side="left", padx=2)
            stats_frame = ttk.Frame(row_frame)
            stats_frame.pack(side="left", padx=2, fill="x", expand=True)
            stat_categories = ["2pt", "3pt", "Stl", "TO", "Ast", "Blk", "Foul", "Reb", "FT"]
            for i, stat in enumerate(stat_categories):
                btn = ttk.Button(stats_frame, text=stat,
                                 command=lambda p=player, s=stat: self.on_stat_button(p, s),
                                 width=3)
                btn.grid(row=0, column=i, padx=1, sticky="nsew")
                stats_frame.columnconfigure(i, weight=1, uniform="stats")
            return row_frame

        ttk.Label(home_frame, text="Home", font=("Consolas", 12, "bold")).pack(pady=(0, 5))
        for player in home_players:
            create_player_row(home_frame, player)
        ttk.Label(away_frame, text="Away", font=("Consolas", 12, "bold")).pack(pady=(0, 5))
        for player in away_players:
            create_player_row(away_frame, player)

    def _on_mousewheel_global_win(self, event):
        self.schedule_canvas.yview_scroll(int(-event.delta / 120), "units")

    def delete_game(self):
        # Ensure a game is selected:
        if not hasattr(self, 'selected_game_id') or not self.selected_game_id:
            print("No game selected to delete.")
            return
        # Call the API's delete function and refresh the schedule:
        result = self.test_data.delete_game(self.selected_game_id)
        if result:
            print(f"Game {self.selected_game_id} deleted.")
            self.clear_schedule_ui()
            self.build_schedule_contents()
            # Reset selected game variables
            self.selected_game_index = None
            self.selected_game_id = None
            # Optionally, clear any displayed details:
            for widget in self.details_container.winfo_children():
                widget.destroy()
            self.details_placeholder = ttk.Label(
                self.details_container,
                text="Click a game to view details",
                font=("Consolas", 14, "italic")
            )
            self.details_placeholder.pack(anchor="center", expand=True)
        else:
            print("Error deleting game.")

    def scroll_near_today(self, today_index, offset=4):
        if 0 <= today_index < len(self.game_buttons):
            adjusted_index = max(0, today_index - offset)
            self.scrollable_schedule_frame.update_idletasks()
            target_widget, _, _ = self.game_buttons[adjusted_index]
            y_coord = target_widget.winfo_y()
            total_height = self.scrollable_schedule_frame.winfo_height()
            fraction = y_coord / float(total_height)
            fraction = max(0.0, min(fraction, 1.0))
            self.schedule_canvas.yview_moveto(fraction)

    def clear_schedule_ui(self):
        for widget in self.scrollable_schedule_frame.winfo_children():
            widget.destroy()
        self.game_buttons.clear()

    def update_game_details_ui(self, game_data, details):
        # Clear existing widgets
        for widget in self.details_container.winfo_children():
            widget.destroy()

        # Create a bold scoreboard label
        score_label = ttk.Label(
            self.details_container,
            text=f"{game_data['home']} ({details['home_score']}) vs {game_data['away']} ({details['away_score']})",
            font=("Consolas", 16, "bold")
        )
        score_label.pack(anchor="center", pady=10)

        teams_frame = ttk.Frame(self.details_container)
        teams_frame.pack(expand=True, pady=10)

        # Home team display
        home_frame = ttk.Frame(teams_frame)
        home_frame.grid(row=0, column=0, padx=30, sticky="n")
        ttk.Label(home_frame, text=f"{game_data['home']} (Home)", font=("Consolas", 12, "bold")).pack()
        ttk.Label(home_frame, text="Players:", font=("Consolas", 10, "bold underline")).pack(pady=(10, 0))
        for line in details["home_display"]:
            # Process each line to ensure the name field is max 12 characters.
            # Assume the fields are separated by '|' and the name is the third field.
            parts = line.split('|')
            if len(parts) >= 3:
                name = parts[2].strip()
                if len(name) > 12:
                    name = name[:12]
                parts[2] = f" {name:<14}"
                new_line = '|'.join(parts)
            else:
                new_line = line
            ttk.Label(home_frame, text=new_line, font=("Consolas", 12, "bold")).pack(anchor="w", padx=5)

        # Away team display
        away_frame = ttk.Frame(teams_frame)
        away_frame.grid(row=0, column=1, padx=30, sticky="n")
        ttk.Label(away_frame, text=f"{game_data['away']} (Away)", font=("Consolas", 12, "bold")).pack()
        ttk.Label(away_frame, text="Players:", font=("Consolas", 10, "bold underline")).pack(pady=(10, 0))
        for line in details["away_display"]:
            # Process each line similarly for the away team
            parts = line.split('|')
            if len(parts) >= 3:
                name = parts[2].strip()
                if len(name) > 12:
                    name = name[:12]
                parts[2] = f" {name:<14}"
                new_line = '|'.join(parts)
            else:
                new_line = line
            ttk.Label(away_frame, text=new_line, font=("Consolas", 12, "bold")).pack(anchor="w", padx=5)


    def generate_jersey_image(self, number):
        jersey_path = os.path.join(UI_ELEMENTS, "Jersey.png")
        if not os.path.exists(jersey_path):
            print(f"Error: Jersey image not found at {jersey_path}")
            return None
        try:
            from PIL import Image
            img = Image.open(jersey_path).convert("RGBA").resize((32, 32), Image.Resampling.LANCZOS)
            style = ttk.Style()
            bg_color = style.lookup('TFrame', 'background')
            def tk_to_rgb(color):
                return self.winfo_rgb(color)[0] // 256, self.winfo_rgb(color)[1] // 256, self.winfo_rgb(color)[2] // 256
            bg_rgb = tk_to_rgb(bg_color)
            new_img = Image.new("RGBA", img.size, (*bg_rgb, 255))
            new_img.paste(img, (0, 0), img)
            txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)
            font = ImageFont.load_default()
            text = str(number)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (32 - text_width) // 2
            y = (32 - text_height) // 2
            draw.text((x, y), text, fill="black", font=font)
            final_image = Image.alpha_composite(new_img, txt_layer)
            return ImageTk.PhotoImage(final_image)
        except Exception as e:
            print(f"Error generating jersey image: {e}")
            return None

    def update_jersey_display(self):
        if not hasattr(self, 'selected_game_id') or not self.selected_game_id:
            return
        random_number = random.randint(1, 99)
        jersey_image = self.generate_jersey_image(random_number)
        if jersey_image:
            self.jersey_canvas.delete("all")
            self.jersey_canvas.create_image(30, 30, image=jersey_image)
            self.jersey_canvas.image = jersey_image

    def create_new_game(self):
        home = self.home_team_var.get()
        away = self.away_team_var.get()
        date_str = self.date_entry.get()
        time_str = self.time_entry.get()  # Time of day

        if home == away:
            print("Error: Home and away teams must be different.")
            return

        try:
            game_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            return

        try:
            game_time = datetime.strptime(time_str.strip(), "%I:%M %p").time()
        except ValueError:
            print("Invalid time format. Use HH:MM AM/PM")
            return

        local_dt = datetime.combine(game_date, game_time)
        local_zone = ZoneInfo("America/New_York")
        local_dt = local_dt.replace(tzinfo=local_zone)
        utc_dt = local_dt.astimezone(timezone.utc)

        # Create the new game (and default stat records) using the FakeAPI.
        new_game = self.test_data.create_game(home, away, utc_dt)
        if new_game is not None:
            self.clear_schedule_ui()
            self.build_schedule_contents()

    def update_game_ui_with_lineup(self, starters, bench):
        """
        Rebuilds the game UI using the provided 'starters' array (on-court player IDs)
        and 'bench' dictionary (teamID -> list of bench player IDs).
        """
        # Clear the game UI container.
        for widget in self.game_ui_container.winfo_children():
            widget.destroy()

        # Retrieve the game record using the selected game ID.
        if not hasattr(self, 'selected_game_id') or not self.selected_game_id:
            print("No game selected to update.")
            return
        game = next((g for g in self.test_data.get_schedule() if g["GameID"] == self.selected_game_id), None)
        if not game:
            print("Game record not found!")
            return

        # Get team IDs.
        home_team_id = game.get("HomeTeamID")
        away_team_id = game.get("AwayTeamID")

        # Filter on-court players from starters using the provided array.
        home_players = [p for p in self.test_data.db["Players"]
                        if p["PlayerID"] in starters and p.get("TeamID") == home_team_id]
        away_players = [p for p in self.test_data.db["Players"]
                        if p["PlayerID"] in starters and p.get("TeamID") == away_team_id]

        # Create header label.
        header = ttk.Label(self.game_ui_container, text=f"{game['home']} vs {game['away']}",
                           font=("Consolas", 16, "bold"))
        header.pack(pady=5)

        # Create players frame.
        players_frame = ttk.Frame(self.game_ui_container)
        players_frame.pack(fill="x", padx=10, pady=10)

        # Create a fresh stat detail frame (empty) inside the Game tab.
        self.stat_detail_frame = ttk.LabelFrame(self.game_ui_container, text="")
        self.stat_detail_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Left frame for home players.
        home_frame = ttk.Frame(players_frame)
        home_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        # Vertical separator.
        separator = tk.Frame(players_frame, width=2, bg="black")
        separator.grid(row=0, column=1, sticky="ns")
        # Right frame for away players.
        away_frame = ttk.Frame(players_frame)
        away_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        players_frame.columnconfigure(0, weight=1)
        players_frame.columnconfigure(2, weight=1)

        # Helper: create a column header (for stats) in a given parent frame.
        def create_headers(parent, is_starter=False):
            font_used = ("Consolas", 12, "bold") if is_starter else ("Consolas", 10)
            headers = f"{'Pos':<3}|{'#':<2}|{' Name':<15}|{'Pts':>3}|{'Ast':>3}|{'Reb':>3}|{'FG%':>3}"
            ttk.Label(parent, text=headers, font=font_used).pack(anchor="w", padx=5)

        # Create a row for each player in the provided starters list.
        def create_player_row(parent, player):
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill="x", pady=2)
            # Save widget references for potential substitution.
            jersey_img = self.generate_jersey_image(player["Jersey_Number"])
            if jersey_img:
                jersey_label = ttk.Label(row_frame, image=jersey_img)
                jersey_label.image = jersey_img
                jersey_label.pack(side="left", padx=2)
                # Bind a click event for substitution.
                jersey_label.bind("<Button-1>", lambda e, p=player: self.on_stat_button(p, "jersey"))
                # Store the widget reference.
                player["jersey_widget"] = jersey_label
            else:
                ttk.Label(row_frame, text=str(player["Jersey_Number"]), font=("Consolas", 10)).pack(side="left", padx=2)
            name_label = ttk.Label(row_frame, text=f"{player['Last_Name']:<15}", font=("Consolas", 10), width=15)
            name_label.pack(side="left", padx=2)
            # Store the name label for potential substitution updates.
            player["name_widget"] = name_label
            stats_frame = ttk.Frame(row_frame)
            stats_frame.pack(side="left", padx=2, fill="x", expand=True)
            stat_categories = ["2pt", "3pt", "Stl", "TO", "Ast", "Blk", "Foul", "Reb", "FT"]
            for i, stat in enumerate(stat_categories):
                btn = ttk.Button(stats_frame, text=stat,
                                 command=lambda p=player, s=stat: self.on_stat_button(p, s),
                                 width=3)
                btn.grid(row=0, column=i, padx=1, sticky="nsew")
                stats_frame.columnconfigure(i, weight=1, uniform="stats")
            return row_frame

        # Populate home team section.
        ttk.Label(home_frame, text="Home", font=("Consolas", 12, "bold")).pack(pady=(0, 5))
        create_headers(home_frame, is_starter=True)
        for player in home_players:
            create_player_row(home_frame, player)

        # Populate away team section.
        ttk.Label(away_frame, text="Away", font=("Consolas", 12, "bold")).pack(pady=(0, 5))
        create_headers(away_frame, is_starter=True)
        for player in away_players:
            create_player_row(away_frame, player)

    def on_stat_button(self, player, stat):
        # Clear the current contents of the stat detail frame.
        for widget in self.stat_detail_frame.winfo_children():
            widget.destroy()
        # Switch statement for each stat type.
        match stat:
            case "2pt":
                # Set header text and clear previous content.
                self.stat_detail_frame.config(text=f"2-Point Attempt for {player['Last_Name']}")
                for widget in self.stat_detail_frame.winfo_children():
                    widget.destroy()
                self.stat_detail_frame.grid_columnconfigure(0, weight=1)

                # --- Dynamic Row Counter ---
                row_counter = [0]

                def next_row():
                    r = row_counter[0]
                    row_counter[0] += 1
                    return r

                def clear_rows_after(r):
                    # Remove any widget whose grid row is greater than r.
                    for widget in self.stat_detail_frame.winfo_children():
                        try:
                            if int(widget.grid_info().get("row", 0)) > r:
                                widget.destroy()
                        except Exception:
                            pass

                # --- Reset Lower Inputs ---
                def reset_lower_inputs():
                    foul_choice.set("")
                    free_throw1.set("")
                    free_throw2.set("")
                    assist_choice.set("")
                    block_choice.set("")
                    rebound_choice.set("")
                    foul_player.set(0)
                    assist_player.set(0)
                    block_player.set(0)
                    rebound_player.set(0)
                    selected_foul_btn[0] = None
                    selected_assist_btn[0] = None
                    selected_block_btn[0] = None
                    selected_rebound_btn[0] = None
                    nonlocal submit_btn
                    if submit_btn is not None:
                        submit_btn.master.destroy()
                        submit_btn = None

                # --- Control Variables & Button Trackers ---
                shot_result = tk.StringVar(value="")  # "made" or "missed"
                foul_choice = tk.StringVar(value="")  # "yes" or "no"
                free_throw1 = tk.StringVar(value="")  # "made" or "missed"
                free_throw2 = tk.StringVar(value="")  # for a 2-pt miss free throw #2
                assist_choice = tk.StringVar(value="")  # "yes" or "no"
                block_choice = tk.StringVar(value="")  # "yes" or "no"
                rebound_choice = tk.StringVar(value="")  # "yes" or "no"
                foul_player = tk.IntVar(value=0)
                assist_player = tk.IntVar(value=0)
                block_player = tk.IntVar(value=0)
                rebound_player = tk.IntVar(value=0)
                selected_foul_btn = [None]
                selected_assist_btn = [None]
                selected_block_btn = [None]
                selected_rebound_btn = [None]
                submit_btn = None  # This will hold the submit button widget

                # Retrieve game record for color coding.
                game_rec = next((g for g in self.test_data.db["Games"] if g["GameID"] == self.selected_game_id), {})
                home_team_id = game_rec.get("HomeTeamID")
                away_team_id = game_rec.get("AwayTeamID")

                # --- Row 0: Shot Outcome ---
                shot_frame = ttk.Frame(self.stat_detail_frame)
                shot_frame.grid(row=next_row(), column=0, pady=5)
                ttk.Label(shot_frame, text="Was the shot made?").grid(row=0, column=0, padx=5, pady=5)
                shot_rb_frame = ttk.Frame(shot_frame)
                shot_rb_frame.grid(row=0, column=1, padx=5, pady=5)
                ttk.Radiobutton(shot_rb_frame, text="Made", variable=shot_result, value="made",
                                command=lambda: (
                                reset_lower_inputs(), clear_rows_after(int(shot_frame.grid_info()["row"])),
                                update_shot())).grid(row=0, column=0, padx=10)
                ttk.Radiobutton(shot_rb_frame, text="Missed", variable=shot_result, value="missed",
                                command=lambda: (
                                reset_lower_inputs(), clear_rows_after(int(shot_frame.grid_info()["row"])),
                                update_shot())).grid(row=0, column=1, padx=10)

                def update_shot():
                    add_foul_question()

                # --- Row 1: Fouled Question ---
                def add_foul_question():
                    r = next_row()
                    f_frame = ttk.Frame(self.stat_detail_frame)
                    f_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(f_frame, text="Was the shooter fouled?").grid(row=0, column=0, padx=5, pady=5)
                    f_rb = ttk.Frame(f_frame)
                    f_rb.grid(row=0, column=1, padx=5, pady=5)
                    ttk.Radiobutton(f_rb, text="Yes", variable=foul_choice, value="yes",
                                    command=lambda: (clear_rows_after(r), add_foul_player_selection())).grid(row=0,
                                                                                                             column=0,
                                                                                                             padx=10)
                    ttk.Radiobutton(f_rb, text="No", variable=foul_choice, value="no",
                                    command=lambda: (clear_rows_after(r), add_free_throw_section())).grid(row=0,
                                                                                                          column=1,
                                                                                                          padx=10)
                    update_submit_if_allowed()

                # --- Row 2: Fouling Player Selection (if fouled) ---
                def add_foul_player_selection():
                    r = next_row()
                    fp_frame = ttk.Frame(self.stat_detail_frame)
                    fp_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(fp_frame, text="Select fouling player:").grid(row=0, column=0, columnspan=4, padx=5,
                                                                            pady=5)
                    btn_frame = ttk.Frame(fp_frame)
                    btn_frame.grid(row=1, column=0, columnspan=4)
                    shooter_team = player.get("TeamID")
                    opposing_team = home_team_id if shooter_team != home_team_id else away_team_id
                    candidates = [p for p in self.test_data.db["Players"]
                                  if p["PlayerID"] in self.currentLineup and p.get("TeamID") == opposing_team][:5]
                    col = 0
                    for cand in candidates:
                        img = self.generate_jersey_image(cand["Jersey_Number"])
                        bg = "lightblue" if cand.get("TeamID") == home_team_id else "lightpink"
                        btn = tk.Button(btn_frame, image=img, relief="raised", borderwidth=2, bg=bg)
                        btn.image = img
                        btn.grid(row=0, column=col, padx=5, pady=2)
                        btn.config(command=lambda pid=cand["PlayerID"], b=btn: make_foul_select(pid, b))
                        col += 1
                    update_submit_if_allowed()
                    add_free_throw_section()

                def make_foul_select(pid, btn):
                    if selected_foul_btn[0] is not None and selected_foul_btn[0].winfo_exists():
                        selected_foul_btn[0].config(relief="raised")
                    foul_player.set(pid)
                    selected_foul_btn[0] = btn
                    btn.config(relief="sunken")
                    update_submit_if_allowed()

                # --- Row 3: Free Throw Section ---
                def add_free_throw_section():
                    r = next_row()
                    ft_frame = ttk.Frame(self.stat_detail_frame)
                    ft_frame.grid(row=r, column=0, pady=5)
                    if foul_choice.get() == "yes":
                        if shot_result.get() == "made":
                            ttk.Label(ft_frame, text="Free Throw Attempt:").grid(row=0, column=0, padx=5, pady=5)
                            ft_rb = ttk.Frame(ft_frame)
                            ft_rb.grid(row=0, column=1, padx=5, pady=5)
                            ttk.Radiobutton(ft_rb, text="Made", variable=free_throw1, value="made",
                                            command=lambda: (clear_rows_after(r), add_next_question())).grid(row=0,
                                                                                                             column=0,
                                                                                                             padx=10)
                            ttk.Radiobutton(ft_rb, text="Missed", variable=free_throw1, value="missed",
                                            command=lambda: (clear_rows_after(r), add_next_question())).grid(row=0,
                                                                                                             column=1,
                                                                                                             padx=10)
                        elif shot_result.get() == "missed":
                            ttk.Label(ft_frame, text="Free Throw Attempt 1:").grid(row=0, column=0, padx=5, pady=5)
                            ft1_rb = ttk.Frame(ft_frame)
                            ft1_rb.grid(row=0, column=1, padx=5, pady=5)
                            ttk.Radiobutton(ft1_rb, text="Made", variable=free_throw1, value="made",
                                            command=lambda: (clear_rows_after(r), add_next_question())).grid(row=0,
                                                                                                             column=0,
                                                                                                             padx=10)
                            ttk.Radiobutton(ft1_rb, text="Missed", variable=free_throw1, value="missed",
                                            command=lambda: (clear_rows_after(r), add_next_question())).grid(row=0,
                                                                                                             column=1,
                                                                                                             padx=10)
                            ttk.Label(ft_frame, text="Free Throw Attempt 2:").grid(row=1, column=0, padx=5, pady=5)
                            ft2_rb = ttk.Frame(ft_frame)
                            ft2_rb.grid(row=1, column=1, padx=5, pady=5)
                            ttk.Radiobutton(ft2_rb, text="Made", variable=free_throw2, value="made",
                                            command=lambda: (clear_rows_after(r), add_next_question())).grid(row=0,
                                                                                                             column=0,
                                                                                                             padx=10)
                            ttk.Radiobutton(ft2_rb, text="Missed", variable=free_throw2, value="missed",
                                            command=lambda: (clear_rows_after(r), add_next_question())).grid(row=0,
                                                                                                             column=1,
                                                                                                             padx=10)
                    else:
                        add_next_question()
                    update_submit_if_allowed()

                # --- Row 4: Next Branch ---
                def add_next_question():
                    clear_rows_after(next_row() - 1)
                    if shot_result.get() == "made":
                        add_assist_question()
                    elif shot_result.get() == "missed":
                        if foul_choice.get() == "yes":
                            add_rebound_question()
                        else:
                            add_block_question()
                    else:
                        update_submit_if_allowed()

                # --- Row 5: Assist Question (for made shots) ---
                def add_assist_question():
                    r = next_row()
                    a_frame = ttk.Frame(self.stat_detail_frame)
                    a_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(a_frame, text="Was it assisted?").grid(row=0, column=0, padx=5, pady=5)
                    a_rb = ttk.Frame(a_frame)
                    a_rb.grid(row=0, column=1, padx=5, pady=5)
                    ttk.Radiobutton(a_rb, text="Yes", variable=assist_choice, value="yes",
                                    command=lambda: (clear_rows_after(r), add_assist_player_selection())).grid(row=0,
                                                                                                               column=0,
                                                                                                               padx=10)
                    ttk.Radiobutton(a_rb, text="No", variable=assist_choice, value="no",
                                    command=lambda: (clear_rows_after(r), update_submit_if_allowed())).grid(row=0,
                                                                                                            column=1,
                                                                                                            padx=10)

                def add_assist_player_selection():
                    r = next_row()
                    ap_frame = ttk.Frame(self.stat_detail_frame)
                    ap_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(ap_frame, text="Select assisting player:").grid(row=0, column=0, columnspan=4, padx=5,
                                                                              pady=5)
                    btn_frame = ttk.Frame(ap_frame)
                    btn_frame.grid(row=1, column=0, columnspan=4)
                    teammates = [p for p in self.test_data.db["Players"]
                                 if p["PlayerID"] in self.currentLineup and p.get("TeamID") == player.get("TeamID")
                                 and p["PlayerID"] != player["PlayerID"]][:4]
                    col = 0
                    for tm in teammates:
                        img = self.generate_jersey_image(tm["Jersey_Number"])
                        bg = "lightblue" if tm.get("TeamID") == home_team_id else "lightpink"
                        cur_btn = tk.Button(btn_frame, image=img, relief="raised", borderwidth=2, bg=bg)
                        cur_btn.image = img
                        cur_btn.grid(row=0, column=col, padx=5, pady=2)
                        cur_btn.config(command=lambda pid=tm["PlayerID"], btn=cur_btn: make_assist_select(pid, btn))
                        col += 1
                    update_submit_if_allowed()

                def make_assist_select(pid, btn):
                    if selected_assist_btn[0] is not None and selected_assist_btn[0].winfo_exists():
                        selected_assist_btn[0].config(relief="raised")
                    assist_player.set(pid)
                    selected_assist_btn[0] = btn
                    btn.config(relief="sunken")
                    update_submit_if_allowed()

                # --- Block Question (for missed shots without foul) ---
                def add_block_question():
                    r = next_row()
                    b_frame = ttk.Frame(self.stat_detail_frame)
                    b_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(b_frame, text="Was it blocked?").grid(row=0, column=0, padx=5, pady=5)
                    b_rb = ttk.Frame(b_frame)
                    b_rb.grid(row=0, column=1, padx=5, pady=5)
                    ttk.Radiobutton(b_rb, text="Yes", variable=block_choice, value="yes",
                                    command=lambda: (clear_rows_after(r), add_block_player_selection())).grid(row=0,
                                                                                                              column=0,
                                                                                                              padx=10)
                    ttk.Radiobutton(b_rb, text="No", variable=block_choice, value="no",
                                    command=lambda: (clear_rows_after(r), add_rebound_question())).grid(row=0, column=1,
                                                                                                        padx=10)
                    update_submit_if_allowed()

                def add_block_player_selection():
                    r = next_row()
                    bp_frame = ttk.Frame(self.stat_detail_frame)
                    bp_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(bp_frame, text="Select blocking player:").grid(row=0, column=0, columnspan=5, padx=5,
                                                                             pady=5)
                    btn_frame = ttk.Frame(bp_frame)
                    btn_frame.grid(row=1, column=0, columnspan=5)
                    shooter_team = player.get("TeamID")
                    opposing_team = home_team_id if game_rec["HomeTeamID"] != shooter_team else game_rec["AwayTeamID"]
                    opponents = [p for p in self.test_data.db["Players"]
                                 if p["PlayerID"] in self.currentLineup and p.get("TeamID") == opposing_team][:5]
                    col = 0
                    for opp in opponents:
                        img = self.generate_jersey_image(opp["Jersey_Number"])
                        bg = "lightblue" if opp.get("TeamID") == home_team_id else "lightpink"
                        cur_btn = tk.Button(btn_frame, image=img, relief="raised", borderwidth=2, bg=bg)
                        cur_btn.image = img
                        cur_btn.grid(row=0, column=col, padx=5, pady=2)
                        cur_btn.config(command=lambda pid=opp["PlayerID"], btn=cur_btn: make_block_select(pid, btn))
                        col += 1
                    add_rebound_question()

                def make_block_select(pid, btn):
                    if selected_block_btn[0] is not None and selected_block_btn[0].winfo_exists():
                        selected_block_btn[0].config(relief="raised")
                    block_player.set(pid)
                    selected_block_btn[0] = btn
                    btn.config(relief="sunken")
                    update_submit_if_allowed()

                # --- Rebound Question ---
                def add_rebound_question():
                    r = next_row()
                    r_frame = ttk.Frame(self.stat_detail_frame)
                    r_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(r_frame, text="Was it rebounded?").grid(row=0, column=0, padx=5, pady=5)
                    r_rb = ttk.Frame(r_frame)
                    r_rb.grid(row=0, column=1, padx=5, pady=5)
                    ttk.Radiobutton(r_rb, text="Yes", variable=rebound_choice, value="yes",
                                    command=lambda: (clear_rows_after(r), add_rebound_player_selection())).grid(row=0,
                                                                                                                column=0,
                                                                                                                padx=10)
                    ttk.Radiobutton(r_rb, text="No", variable=rebound_choice, value="no",
                                    command=lambda: (clear_rows_after(r), update_submit_if_allowed())).grid(row=0,
                                                                                                            column=1,
                                                                                                            padx=10)
                    update_submit_if_allowed()

                def add_rebound_player_selection():
                    r = next_row()
                    rp_frame = ttk.Frame(self.stat_detail_frame)
                    rp_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(rp_frame, text="Select rebounder:").grid(row=0, column=0, columnspan=10, padx=5, pady=5)
                    btn_frame = ttk.Frame(rp_frame)
                    btn_frame.grid(row=1, column=0, columnspan=10)
                    rebounders = [p for p in self.test_data.db["Players"] if p["PlayerID"] in self.currentLineup][:10]
                    col = 0
                    for rp in rebounders:
                        img = self.generate_jersey_image(rp["Jersey_Number"])
                        bg = "lightblue" if rp.get("TeamID") == home_team_id else "lightpink"
                        cur_btn = tk.Button(btn_frame, image=img, relief="raised", borderwidth=2, bg=bg)
                        cur_btn.image = img
                        cur_btn.grid(row=0, column=col, padx=5, pady=2)
                        cur_btn.config(command=lambda pid=rp["PlayerID"], btn=cur_btn: make_rebound_select(pid, btn))
                        col += 1
                    update_submit_if_allowed()

                def make_rebound_select(pid, btn):
                    if selected_rebound_btn[0] is not None and selected_rebound_btn[0].winfo_exists():
                        selected_rebound_btn[0].config(relief="raised")
                    rebound_player.set(pid)
                    selected_rebound_btn[0] = btn
                    btn.config(relief="sunken")
                    update_submit_if_allowed()

                # --- Submit Section ---
                def update_submit_if_allowed():
                    # Only allow submit at the following points:
                    # • After selecting an assisting player OR after saying “no” to assist,
                    # • After saying “no” to rebound,
                    # • After selecting a rebounder.
                    # Conditions for completeness:
                    complete = True
                    if shot_result.get() not in ["made", "missed"]:
                        complete = False
                    if foul_choice.get() not in ["yes", "no"]:
                        complete = False
                    if foul_choice.get() == "yes" and foul_player.get() == 0:
                        complete = False
                    if foul_choice.get() == "yes":
                        if free_throw1.get() not in ["made", "missed"]:
                            complete = False
                    if shot_result.get() == "made":
                        if assist_choice.get() not in ["yes", "no"]:
                            complete = False
                        if assist_choice.get() == "yes" and assist_player.get() == 0:
                            complete = False
                    if shot_result.get() == "missed" and foul_choice.get() == "no":
                        if block_choice.get() not in ["yes", "no"]:
                            complete = False
                    if shot_result.get() == "missed":
                        if rebound_choice.get() not in ["yes", "no"]:
                            complete = False
                        if rebound_choice.get() == "yes" and rebound_player.get() == 0:
                            complete = False

                    nonlocal submit_btn
                    if complete:
                        if submit_btn is None:
                            s_frame = ttk.Frame(self.stat_detail_frame)
                            s_frame.grid(row=next_row(), column=0, pady=5)
                            submit_btn = ttk.Button(s_frame, text="Submit", command=submit_all)
                            submit_btn.grid(row=0, column=0, padx=5, pady=5)
                    else:
                        if submit_btn is not None:
                            submit_btn.master.destroy()
                            submit_btn = None

                def submit_all():
                    game_id = self.selected_game_id
                    shooter_id = player["PlayerID"]
                    if shot_result.get() == "made":
                        self.update_player_stats(game_id, shooter_id, "2pt_make")
                        if foul_choice.get() == "yes":
                            if free_throw1.get() == "made":
                                self.update_player_stats(game_id, shooter_id, "ft_make")
                            elif free_throw1.get() == "missed":
                                self.update_player_stats(game_id, shooter_id, "ft_miss")
                        if assist_choice.get() == "yes" and assist_player.get() != 0:
                            self.update_player_stats(game_id, assist_player.get(), "assist")
                    elif shot_result.get() == "missed":
                        self.update_player_stats(game_id, shooter_id, "2pt_miss")
                        if foul_choice.get() == "yes":
                            if free_throw1.get() == "made":
                                self.update_player_stats(game_id, shooter_id, "ft_make")
                            elif free_throw1.get() == "missed":
                                self.update_player_stats(game_id, shooter_id, "ft_miss")
                            if free_throw2.get() == "made":
                                self.update_player_stats(game_id, shooter_id, "ft_make")
                            elif free_throw2.get() == "missed":
                                self.update_player_stats(game_id, shooter_id, "ft_miss")
                        else:
                            if block_choice.get() == "yes" and block_player.get() != 0:
                                self.update_player_stats(game_id, block_player.get(), "block")
                        if rebound_choice.get() == "yes" and rebound_player.get() != 0:
                            self.update_player_stats(game_id, rebound_player.get(), "rebound")
                    clear_rows_after(0)
                    final_frame = ttk.Frame(self.stat_detail_frame)
                    final_frame.grid(row=next_row(), column=0, pady=5)
                    ttk.Label(final_frame, text="Stat(s) updated.").grid(row=0, column=0, padx=5, pady=5)

                update_submit_if_allowed()

            case "3pt":
                # Set header and clear previous content.
                self.stat_detail_frame.config(text=f"3-Point Attempt for {player['Last_Name']}")
                for widget in self.stat_detail_frame.winfo_children():
                    widget.destroy()
                self.stat_detail_frame.grid_columnconfigure(0, weight=1)

                # --- Dynamic Row Counter & Helpers ---
                row_counter = [0]

                def next_row():
                    r = row_counter[0]
                    row_counter[0] += 1
                    return r

                def clear_rows_after(r):
                    for widget in self.stat_detail_frame.winfo_children():
                        try:
                            if int(widget.grid_info().get("row", 0)) > r:
                                widget.destroy()
                        except Exception:
                            pass

                def reset_lower_inputs():
                    foul_choice.set("")
                    free_throw1.set("")
                    free_throw2.set("")
                    free_throw3.set("")
                    assist_choice.set("")
                    block_choice.set("")
                    rebound_choice.set("")
                    foul_player.set(0)
                    assist_player.set(0)
                    block_player.set(0)
                    rebound_player.set(0)
                    selected_foul_btn[0] = None
                    selected_assist_btn[0] = None
                    selected_block_btn[0] = None
                    selected_rebound_btn[0] = None
                    nonlocal submit_btn
                    if submit_btn is not None:
                        submit_btn.master.destroy()
                        submit_btn = None

                # --- Control Variables & Button Trackers ---
                shot_result = tk.StringVar(value="")  # "made" or "missed"
                foul_choice = tk.StringVar(value="")  # "yes" or "no"
                free_throw1 = tk.StringVar(value="")  # for free throw 1
                free_throw2 = tk.StringVar(value="")  # for free throw 2 (only for missed 3pt)
                free_throw3 = tk.StringVar(value="")  # for free throw 3 (only for missed 3pt)
                assist_choice = tk.StringVar(value="")  # "yes" or "no"
                block_choice = tk.StringVar(value="")  # "yes" or "no"
                rebound_choice = tk.StringVar(value="")  # "yes" or "no"
                foul_player = tk.IntVar(value=0)
                assist_player = tk.IntVar(value=0)
                block_player = tk.IntVar(value=0)
                rebound_player = tk.IntVar(value=0)
                selected_foul_btn = [None]
                selected_assist_btn = [None]
                selected_block_btn = [None]
                selected_rebound_btn = [None]
                submit_btn = None  # Will store the submit button widget

                # --- Retrieve Game Record for Color Coding ---
                game_rec = next((g for g in self.test_data.db["Games"] if g["GameID"] == self.selected_game_id), {})
                home_team_id = game_rec.get("HomeTeamID")
                away_team_id = game_rec.get("AwayTeamID")

                # --- Row 0: Shot Outcome ---
                shot_frame = ttk.Frame(self.stat_detail_frame)
                shot_frame.grid(row=next_row(), column=0, pady=5)
                ttk.Label(shot_frame, text="Was the shot made?").grid(row=0, column=0, padx=5, pady=5)
                shot_rb_frame = ttk.Frame(shot_frame)
                shot_rb_frame.grid(row=0, column=1, padx=5, pady=5)
                ttk.Radiobutton(shot_rb_frame, text="Made", variable=shot_result, value="made",
                                command=lambda: (
                                reset_lower_inputs(), clear_rows_after(int(shot_frame.grid_info()["row"])),
                                update_shot())).grid(row=0, column=0, padx=10)
                ttk.Radiobutton(shot_rb_frame, text="Missed", variable=shot_result, value="missed",
                                command=lambda: (
                                reset_lower_inputs(), clear_rows_after(int(shot_frame.grid_info()["row"])),
                                update_shot())).grid(row=0, column=1, padx=10)

                def update_shot():
                    add_foul_question()

                # --- Row 1: Fouled Question ---
                def add_foul_question():
                    r = next_row()
                    f_frame = ttk.Frame(self.stat_detail_frame)
                    f_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(f_frame, text="Was the shooter fouled?").grid(row=0, column=0, padx=5, pady=5)
                    f_rb = ttk.Frame(f_frame)
                    f_rb.grid(row=0, column=1, padx=5, pady=5)
                    ttk.Radiobutton(f_rb, text="Yes", variable=foul_choice, value="yes",
                                    command=lambda: (clear_rows_after(r), add_foul_player_selection())).grid(row=0,
                                                                                                             column=0,
                                                                                                             padx=10)
                    ttk.Radiobutton(f_rb, text="No", variable=foul_choice, value="no",
                                    command=lambda: (clear_rows_after(r), add_free_throw_section())).grid(row=0,
                                                                                                          column=1,
                                                                                                          padx=10)
                    update_submit_if_allowed()

                # --- Row 2: Fouling Player Selection (if fouled) ---
                def add_foul_player_selection():
                    r = next_row()
                    fp_frame = ttk.Frame(self.stat_detail_frame)
                    fp_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(fp_frame, text="Select fouling player:").grid(row=0, column=0, columnspan=4, padx=5,
                                                                            pady=5)
                    btn_frame = ttk.Frame(fp_frame)
                    btn_frame.grid(row=1, column=0, columnspan=4)
                    shooter_team = player.get("TeamID")
                    opposing_team = home_team_id if shooter_team != home_team_id else away_team_id
                    candidates = [p for p in self.test_data.db["Players"]
                                  if p["PlayerID"] in self.currentLineup and p.get("TeamID") == opposing_team][:5]
                    col = 0
                    for cand in candidates:
                        img = self.generate_jersey_image(cand["Jersey_Number"])
                        bg = "lightblue" if cand.get("TeamID") == home_team_id else "lightpink"
                        btn = tk.Button(btn_frame, image=img, relief="raised", borderwidth=2, bg=bg)
                        btn.image = img
                        btn.grid(row=0, column=col, padx=5, pady=2)
                        btn.config(command=lambda pid=cand["PlayerID"], b=btn: make_foul_select(pid, b))
                        col += 1
                    update_submit_if_allowed()
                    add_free_throw_section()

                def make_foul_select(pid, btn):
                    if selected_foul_btn[0] is not None and selected_foul_btn[0].winfo_exists():
                        selected_foul_btn[0].config(relief="raised")
                    foul_player.set(pid)
                    selected_foul_btn[0] = btn
                    btn.config(relief="sunken")
                    update_submit_if_allowed()

                # --- Row 3: Free Throw Section ---
                def add_free_throw_section():
                    r = next_row()
                    ft_frame = ttk.Frame(self.stat_detail_frame)
                    ft_frame.grid(row=r, column=0, pady=5)
                    if foul_choice.get() == "yes":
                        if shot_result.get() == "made":
                            ttk.Label(ft_frame, text="Free Throw Attempt:").grid(row=0, column=0, padx=5, pady=5)
                            ft_rb = ttk.Frame(ft_frame)
                            ft_rb.grid(row=0, column=1, padx=5, pady=5)
                            ttk.Radiobutton(ft_rb, text="Made", variable=free_throw1, value="made",
                                            command=lambda: (clear_rows_after(r), add_next_question())).grid(row=0,
                                                                                                             column=0,
                                                                                                             padx=10)
                            ttk.Radiobutton(ft_rb, text="Missed", variable=free_throw1, value="missed",
                                            command=lambda: (clear_rows_after(r), add_next_question())).grid(row=0,
                                                                                                             column=1,
                                                                                                             padx=10)
                        elif shot_result.get() == "missed":
                            # For a missed 3pt attempt with a foul, there are three free throws.
                            ttk.Label(ft_frame, text="Free Throw Attempt 1:").grid(row=0, column=0, padx=5, pady=5)
                            ft1_rb = ttk.Frame(ft_frame)
                            ft1_rb.grid(row=0, column=1, padx=5, pady=5)
                            ttk.Radiobutton(ft1_rb, text="Made", variable=free_throw1, value="made",
                                            command=lambda: (clear_rows_after(r), add_next_question())).grid(row=0,
                                                                                                             column=0,
                                                                                                             padx=10)
                            ttk.Radiobutton(ft1_rb, text="Missed", variable=free_throw1, value="missed",
                                            command=lambda: (clear_rows_after(r), add_next_question())).grid(row=0,
                                                                                                             column=1,
                                                                                                             padx=10)
                            ttk.Label(ft_frame, text="Free Throw Attempt 2:").grid(row=1, column=0, padx=5, pady=5)
                            ft2_rb = ttk.Frame(ft_frame)
                            ft2_rb.grid(row=1, column=1, padx=5, pady=5)
                            ttk.Radiobutton(ft2_rb, text="Made", variable=free_throw2, value="made",
                                            command=lambda: (clear_rows_after(r), add_next_question())).grid(row=0,
                                                                                                             column=0,
                                                                                                             padx=10)
                            ttk.Radiobutton(ft2_rb, text="Missed", variable=free_throw2, value="missed",
                                            command=lambda: (clear_rows_after(r), add_next_question())).grid(row=0,
                                                                                                             column=1,
                                                                                                             padx=10)
                            ttk.Label(ft_frame, text="Free Throw Attempt 3:").grid(row=2, column=0, padx=5, pady=5)
                            ft3_rb = ttk.Frame(ft_frame)
                            ft3_rb.grid(row=2, column=1, padx=5, pady=5)
                            ttk.Radiobutton(ft3_rb, text="Made", variable=free_throw3, value="made",
                                            command=lambda: (clear_rows_after(r), add_next_question())).grid(row=0,
                                                                                                             column=0,
                                                                                                             padx=10)
                            ttk.Radiobutton(ft3_rb, text="Missed", variable=free_throw3, value="missed",
                                            command=lambda: (clear_rows_after(r), add_next_question())).grid(row=0,
                                                                                                             column=1,
                                                                                                             padx=10)
                    else:
                        add_next_question()
                    update_submit_if_allowed()

                # --- Row 4: Next Branch ---
                def add_next_question():
                    clear_rows_after(next_row() - 1)
                    if shot_result.get() == "made":
                        add_assist_question()
                    elif shot_result.get() == "missed":
                        if foul_choice.get() == "yes":
                            add_rebound_question()
                        else:
                            add_block_question()
                    else:
                        update_submit_if_allowed()

                # --- Row 5: Assist Question (for made shots) ---
                def add_assist_question():
                    r = next_row()
                    a_frame = ttk.Frame(self.stat_detail_frame)
                    a_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(a_frame, text="Was it assisted?").grid(row=0, column=0, padx=5, pady=5)
                    a_rb = ttk.Frame(a_frame)
                    a_rb.grid(row=0, column=1, padx=5, pady=5)
                    ttk.Radiobutton(a_rb, text="Yes", variable=assist_choice, value="yes",
                                    command=lambda: (clear_rows_after(r), add_assist_player_selection())).grid(row=0,
                                                                                                               column=0,
                                                                                                               padx=10)
                    ttk.Radiobutton(a_rb, text="No", variable=assist_choice, value="no",
                                    command=lambda: (clear_rows_after(r), update_submit_if_allowed())).grid(row=0,
                                                                                                            column=1,
                                                                                                            padx=10)

                def add_assist_player_selection():
                    r = next_row()
                    ap_frame = ttk.Frame(self.stat_detail_frame)
                    ap_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(ap_frame, text="Select assisting player:").grid(row=0, column=0, columnspan=4, padx=5,
                                                                              pady=5)
                    btn_frame = ttk.Frame(ap_frame)
                    btn_frame.grid(row=1, column=0, columnspan=4)
                    teammates = [p for p in self.test_data.db["Players"]
                                 if p["PlayerID"] in self.currentLineup and p.get("TeamID") == player.get("TeamID")
                                 and p["PlayerID"] != player["PlayerID"]][:4]
                    col = 0
                    for tm in teammates:
                        img = self.generate_jersey_image(tm["Jersey_Number"])
                        bg = "lightblue" if tm.get("TeamID") == home_team_id else "lightpink"
                        cur_btn = tk.Button(btn_frame, image=img, relief="raised", borderwidth=2, bg=bg)
                        cur_btn.image = img
                        cur_btn.grid(row=0, column=col, padx=5, pady=2)
                        cur_btn.config(command=lambda pid=tm["PlayerID"], btn=cur_btn: make_assist_select(pid, btn))
                        col += 1
                    update_submit_if_allowed()

                def make_assist_select(pid, btn):
                    if selected_assist_btn[0] is not None and selected_assist_btn[0].winfo_exists():
                        selected_assist_btn[0].config(relief="raised")
                    assist_player.set(pid)
                    selected_assist_btn[0] = btn
                    btn.config(relief="sunken")
                    update_submit_if_allowed()

                # --- Block Question (for missed shots without foul) ---
                def add_block_question():
                    r = next_row()
                    b_frame = ttk.Frame(self.stat_detail_frame)
                    b_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(b_frame, text="Was it blocked?").grid(row=0, column=0, padx=5, pady=5)
                    b_rb = ttk.Frame(b_frame)
                    b_rb.grid(row=0, column=1, padx=5, pady=5)
                    ttk.Radiobutton(b_rb, text="Yes", variable=block_choice, value="yes",
                                    command=lambda: (clear_rows_after(r), add_block_player_selection())).grid(row=0,
                                                                                                              column=0,
                                                                                                              padx=10)
                    ttk.Radiobutton(b_rb, text="No", variable=block_choice, value="no",
                                    command=lambda: (clear_rows_after(r), add_rebound_question())).grid(row=0, column=1,
                                                                                                        padx=10)
                    update_submit_if_allowed()

                def add_block_player_selection():
                    r = next_row()
                    bp_frame = ttk.Frame(self.stat_detail_frame)
                    bp_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(bp_frame, text="Select blocking player:").grid(row=0, column=0, columnspan=5, padx=5,
                                                                             pady=5)
                    btn_frame = ttk.Frame(bp_frame)
                    btn_frame.grid(row=1, column=0, columnspan=5)
                    shooter_team = player.get("TeamID")
                    opposing_team = home_team_id if game_rec["HomeTeamID"] != shooter_team else game_rec["AwayTeamID"]
                    opponents = [p for p in self.test_data.db["Players"]
                                 if p["PlayerID"] in self.currentLineup and p.get("TeamID") == opposing_team][:5]
                    col = 0
                    for opp in opponents:
                        img = self.generate_jersey_image(opp["Jersey_Number"])
                        bg = "lightblue" if opp.get("TeamID") == home_team_id else "lightpink"
                        cur_btn = tk.Button(btn_frame, image=img, relief="raised", borderwidth=2, bg=bg)
                        cur_btn.image = img
                        cur_btn.grid(row=0, column=col, padx=5, pady=2)
                        cur_btn.config(command=lambda pid=opp["PlayerID"], btn=cur_btn: make_block_select(pid, btn))
                        col += 1
                    add_rebound_question()

                def make_block_select(pid, btn):
                    if selected_block_btn[0] is not None and selected_block_btn[0].winfo_exists():
                        selected_block_btn[0].config(relief="raised")
                    block_player.set(pid)
                    selected_block_btn[0] = btn
                    btn.config(relief="sunken")
                    update_submit_if_allowed()

                # --- Rebound Question ---
                def add_rebound_question():
                    r = next_row()
                    r_frame = ttk.Frame(self.stat_detail_frame)
                    r_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(r_frame, text="Was it rebounded?").grid(row=0, column=0, padx=5, pady=5)
                    r_rb = ttk.Frame(r_frame)
                    r_rb.grid(row=0, column=1, padx=5, pady=5)
                    ttk.Radiobutton(r_rb, text="Yes", variable=rebound_choice, value="yes",
                                    command=lambda: (clear_rows_after(r), add_rebound_player_selection())).grid(row=0,
                                                                                                                column=0,
                                                                                                                padx=10)
                    ttk.Radiobutton(r_rb, text="No", variable=rebound_choice, value="no",
                                    command=lambda: (clear_rows_after(r), update_submit_if_allowed())).grid(row=0,
                                                                                                            column=1,
                                                                                                            padx=10)
                    update_submit_if_allowed()

                def add_rebound_player_selection():
                    r = next_row()
                    rp_frame = ttk.Frame(self.stat_detail_frame)
                    rp_frame.grid(row=r, column=0, pady=5)
                    ttk.Label(rp_frame, text="Select rebounder:").grid(row=0, column=0, columnspan=10, padx=5, pady=5)
                    btn_frame = ttk.Frame(rp_frame)
                    btn_frame.grid(row=1, column=0, columnspan=10)
                    rebounders = [p for p in self.test_data.db["Players"] if p["PlayerID"] in self.currentLineup][:10]
                    col = 0
                    for rp in rebounders:
                        img = self.generate_jersey_image(rp["Jersey_Number"])
                        bg = "lightblue" if rp.get("TeamID") == home_team_id else "lightpink"
                        cur_btn = tk.Button(btn_frame, image=img, relief="raised", borderwidth=2, bg=bg)
                        cur_btn.image = img
                        cur_btn.grid(row=0, column=col, padx=5, pady=2)
                        cur_btn.config(command=lambda pid=rp["PlayerID"], btn=cur_btn: make_rebound_select(pid, btn))
                        col += 1
                    update_submit_if_allowed()

                def make_rebound_select(pid, btn):
                    if selected_rebound_btn[0] is not None and selected_rebound_btn[0].winfo_exists():
                        selected_rebound_btn[0].config(relief="raised")
                    rebound_player.set(pid)
                    selected_rebound_btn[0] = btn
                    btn.config(relief="sunken")
                    update_submit_if_allowed()

                # --- Submit Section ---
                def update_submit_if_allowed():
                    complete = True
                    if shot_result.get() not in ["made", "missed"]:
                        complete = False
                    if foul_choice.get() not in ["yes", "no"]:
                        complete = False
                    if foul_choice.get() == "yes" and foul_player.get() == 0:
                        complete = False
                    if foul_choice.get() == "yes":
                        if shot_result.get() == "made":
                            if free_throw1.get() not in ["made", "missed"]:
                                complete = False
                        elif shot_result.get() == "missed":
                            if free_throw1.get() not in ["made", "missed"]:
                                complete = False
                            if free_throw2.get() not in ["made", "missed"]:
                                complete = False
                            if free_throw3.get() not in ["made", "missed"]:
                                complete = False
                    if shot_result.get() == "made":
                        if assist_choice.get() not in ["yes", "no"]:
                            complete = False
                        if assist_choice.get() == "yes" and assist_player.get() == 0:
                            complete = False
                    if shot_result.get() == "missed" and foul_choice.get() == "no":
                        if block_choice.get() not in ["yes", "no"]:
                            complete = False
                    if shot_result.get() == "missed":
                        if rebound_choice.get() not in ["yes", "no"]:
                            complete = False
                        if rebound_choice.get() == "yes" and rebound_player.get() == 0:
                            complete = False

                    nonlocal submit_btn
                    if complete:
                        if submit_btn is None:
                            s_frame = ttk.Frame(self.stat_detail_frame)
                            s_frame.grid(row=next_row(), column=0, pady=5)
                            submit_btn = ttk.Button(s_frame, text="Submit", command=submit_all)
                            submit_btn.grid(row=0, column=0, padx=5, pady=5)
                    else:
                        if submit_btn is not None:
                            submit_btn.master.destroy()
                            submit_btn = None

                def submit_all():
                    game_id = self.selected_game_id
                    shooter_id = player["PlayerID"]
                    if shot_result.get() == "made":
                        self.update_player_stats(game_id, shooter_id, "3pt_make")
                        if foul_choice.get() == "yes":
                            if free_throw1.get() == "made":
                                self.update_player_stats(game_id, shooter_id, "ft_make")
                            elif free_throw1.get() == "missed":
                                self.update_player_stats(game_id, shooter_id, "ft_miss")
                    elif shot_result.get() == "missed":
                        self.update_player_stats(game_id, shooter_id, "3pt_miss")
                        if foul_choice.get() == "yes":
                            if free_throw1.get() == "made":
                                self.update_player_stats(game_id, shooter_id, "ft_make")
                            elif free_throw1.get() == "missed":
                                self.update_player_stats(game_id, shooter_id, "ft_miss")
                            if free_throw2.get() == "made":
                                self.update_player_stats(game_id, shooter_id, "ft_make")
                            elif free_throw2.get() == "missed":
                                self.update_player_stats(game_id, shooter_id, "ft_miss")
                            if free_throw3.get() == "made":
                                self.update_player_stats(game_id, shooter_id, "ft_make")
                            elif free_throw3.get() == "missed":
                                self.update_player_stats(game_id, shooter_id, "ft_miss")
                        else:
                            if block_choice.get() == "yes" and block_player.get() != 0:
                                self.update_player_stats(game_id, block_player.get(), "block")
                    if assist_choice.get() == "yes" and assist_player.get() != 0:
                        self.update_player_stats(game_id, assist_player.get(), "assist")
                    if rebound_choice.get() == "yes" and rebound_player.get() != 0:
                        self.update_player_stats(game_id, rebound_player.get(), "rebound")
                    clear_rows_after(0)
                    final_frame = ttk.Frame(self.stat_detail_frame)
                    final_frame.grid(row=next_row(), column=0, pady=5)
                    ttk.Label(final_frame, text="Stat(s) updated.").grid(row=0, column=0, padx=5, pady=5)

                update_submit_if_allowed()

            case "Stl":
                self.stat_detail_frame.config(text=f"Steal by {player['Last_Name']}")
                for widget in self.stat_detail_frame.winfo_children():
                    widget.destroy()

                # Center the content.
                self.stat_detail_frame.grid_columnconfigure(0, weight=1)

                # Retrieve the game record so we can color code based on team.
                game_rec = next((g for g in self.test_data.db["Games"] if g["GameID"] == self.selected_game_id), {})
                home_team_id = game_rec.get("HomeTeamID", None)
                away_team_id = game_rec.get("AwayTeamID", None)

                # Create persistent frames.
                steal_frame = ttk.Frame(self.stat_detail_frame)
                steal_frame.grid(row=0, column=0, pady=5)
                steal_target_frame = ttk.Frame(self.stat_detail_frame)
                steal_target_frame.grid(row=1, column=0, pady=5)
                submit_frame = ttk.Frame(self.stat_detail_frame)
                submit_frame.grid(row=2, column=0, pady=5)

                # Control variable for the opponent from whom the steal occurred.
                steal_target = tk.IntVar(value=0)

                # For tracking selected jersey button.
                selected_steal_btn = [None]

                # Row 0: Display a message.
                ttk.Label(steal_frame, text="Steal recorded. Who did they steal from?").grid(row=0, column=0, padx=5,
                                                                                            pady=5)

                # Row 1: Create jersey buttons for the opposing team.
                # Determine which team is opposing the stealing player's team.
                shooter_team = player.get("TeamID")
                if shooter_team == home_team_id:
                    opposing_team = away_team_id
                else:
                    opposing_team = home_team_id

                # Filter players from the opposing team that are currently on court.
                opponents = [p for p in self.test_data.db["Players"]
                             if p["PlayerID"] in self.currentLineup and p.get("TeamID") == opposing_team][:5]

                btn_frame = ttk.Frame(steal_target_frame)
                btn_frame.grid(row=0, column=0)
                col = 0
                for opp in opponents:
                    img = self.generate_jersey_image(opp["Jersey_Number"])
                    # Color code: lightblue for home, lightpink for away.
                    bg_color = "lightblue" if opp.get("TeamID") == home_team_id else "lightpink"
                    btn = tk.Button(btn_frame, image=img, relief="raised", borderwidth=2, bg=bg_color)
                    btn.image = img
                    btn.config(command=lambda pid=opp["PlayerID"], b=btn: make_steal_select(pid, b))
                    btn.grid(row=0, column=col, padx=5, pady=2)
                    col += 1

                def make_steal_select(pid, btn):
                    # If a previously selected button exists and still exists, reset its appearance.
                    if selected_steal_btn[0] is not None and selected_steal_btn[0].winfo_exists():
                        selected_steal_btn[0].config(relief="raised", padx=5)
                    steal_target.set(pid)
                    selected_steal_btn[0] = btn
                    btn.config(relief="sunken", padx=15)
                    update_submit()

                def update_submit():
                    for widget in submit_frame.winfo_children():
                        widget.destroy()
                    submit_btn = ttk.Button(submit_frame, text="Submit", command=submit_all)
                    submit_btn.grid(row=0, column=0, padx=5, pady=5)

                def submit_all():
                    game_id = self.selected_game_id
                    # Record the steal for the stealing player.
                    self.update_player_stats(game_id, player["PlayerID"], "steal")
                    # And record that the steal was a turnover from the selected opponent.
                    if steal_target.get() != 0:
                        self.update_player_stats(game_id, steal_target.get(), "TO")
                    for widget in submit_frame.winfo_children():
                        widget.destroy()
                    ttk.Label(submit_frame, text="Steal recorded.").grid(row=0, column=0, padx=5, pady=5)

                update_submit()
            case "TO":
                self.stat_detail_frame.config(text=f"Turnover by {player['Last_Name']}")
                for widget in self.stat_detail_frame.winfo_children():
                    widget.destroy()

                # Center the content.
                self.stat_detail_frame.grid_columnconfigure(0, weight=1)

                # Retrieve game record for team info.
                game_rec = next((g for g in self.test_data.db["Games"] if g["GameID"] == self.selected_game_id), {})
                home_team_id = game_rec.get("HomeTeamID", None)
                away_team_id = game_rec.get("AwayTeamID", None)

                # Create frames.
                to_frame = ttk.Frame(self.stat_detail_frame)
                to_frame.grid(row=0, column=0, pady=5)
                stolen_frame = ttk.Frame(self.stat_detail_frame)
                stolen_frame.grid(row=1, column=0, pady=5)
                stolen_target_frame = ttk.Frame(self.stat_detail_frame)
                stolen_target_frame.grid(row=2, column=0, pady=5)
                submit_frame = ttk.Frame(self.stat_detail_frame)
                submit_frame.grid(row=3, column=0, pady=5)

                # Control variable for whether turnover was stolen.
                stolen_choice = tk.StringVar(value="")  # "yes" or "no"
                # Control variable for the opponent who stole it.
                stolen_by = tk.IntVar(value=0)
                selected_stolen_btn = [None]

                # Row 0: Display turnover message.
                ttk.Label(to_frame, text=f"Turnover by {player['Last_Name']}").pack(padx=5, pady=5)

                # Row 1: Ask if the turnover was stolen.
                stolen_q_frame = ttk.Frame(stolen_frame)
                stolen_q_frame.pack(padx=5, pady=5)
                ttk.Label(stolen_q_frame, text="Was it stolen?").pack(side="left", padx=5)
                ttk.Radiobutton(stolen_q_frame, text="Yes", variable=stolen_choice, value="yes",
                                command=lambda: update_stolen_target()).pack(side="left", padx=10)
                ttk.Radiobutton(stolen_q_frame, text="No", variable=stolen_choice, value="no",
                                command=lambda: clear_frame(stolen_target_frame) or update_submit()).pack(side="left",
                                                                                                          padx=10)

                # Row 2: If stolen, show jersey selection.
                def update_stolen_target():
                    stolen_target_frame.grid(row=2, column=0, pady=5)
                    for widget in stolen_target_frame.winfo_children():
                        widget.destroy()
                    ttk.Label(stolen_target_frame, text="Select the player who stole the ball:").pack(padx=5, pady=5)
                    btn_frame = ttk.Frame(stolen_target_frame)
                    btn_frame.pack()
                    # Determine opposing team: if turnover by a home player then opponents are from away, else home.
                    turnover_team = player.get("TeamID")
                    opposing_team = away_team_id if turnover_team == home_team_id else home_team_id
                    # Filter opponents among on-court players.
                    opponents = [p for p in self.test_data.db["Players"]
                                 if p["PlayerID"] in self.currentLineup and p.get("TeamID") == opposing_team][:5]
                    col = 0
                    for opp in opponents:
                        img = self.generate_jersey_image(opp["Jersey_Number"])
                        bg_color = "lightblue" if opp.get("TeamID") == home_team_id else "lightpink"
                        btn = tk.Button(btn_frame, image=img, relief="raised", borderwidth=2, bg=bg_color)
                        btn.image = img
                        btn.config(command=lambda pid=opp["PlayerID"], b=btn: make_stolen_select(pid, b))
                        btn.grid(row=0, column=col, padx=5, pady=2)
                        col += 1
                    update_submit()

                def make_stolen_select(pid, btn):
                    if selected_stolen_btn[0] is not None and selected_stolen_btn[0].winfo_exists():
                        selected_stolen_btn[0].config(relief="raised", padx=5)
                    stolen_by.set(pid)
                    selected_stolen_btn[0] = btn
                    btn.config(relief="sunken", padx=15)
                    update_submit()

                # Helper function to clear a frame.
                def clear_frame(frm):
                    for widget in frm.winfo_children():
                        widget.destroy()

                # Row 3: Submit button.
                def update_submit():
                    for widget in submit_frame.winfo_children():
                        widget.destroy()
                    ttk.Button(submit_frame, text="Submit", command=lambda: submit_turnover()).grid(row=0, column=0,
                                                                                                    padx=5, pady=5)

                def submit_turnover():
                    game_id = self.selected_game_id
                    # Record the turnover for the player (they turned the ball over).
                    self.update_player_stats(game_id, player["PlayerID"], "TO")
                    # If the turnover was stolen, record a steal for the selected opponent.
                    if stolen_choice.get() == "yes" and stolen_by.get() != 0:
                        self.update_player_stats(game_id, stolen_by.get(), "steal")
                    for widget in submit_frame.winfo_children():
                        widget.destroy()
                    ttk.Label(submit_frame, text="Turnover recorded.").grid(row=0, column=0, padx=5, pady=5)

                update_submit()

            case "Ast":
                self.stat_detail_frame.config(text=f"Assist by {player['Last_Name']}")
                for widget in self.stat_detail_frame.winfo_children():
                    widget.destroy()
                self.stat_detail_frame.grid_columnconfigure(0, weight=1)

                # Row counter for dynamic placement.
                row_counter = [0]

                def next_row():
                    r = row_counter[0]
                    row_counter[0] += 1
                    return r

                # Control variables.
                assisted_player = tk.IntVar(value=0)
                shot_type_choice = tk.StringVar(value="")  # "2" or "3"
                foul_choice = tk.StringVar(value="")  # "yes" or "no"
                free_throw_result = tk.StringVar(value="")  # "made" or "missed"
                selected_assist_btn = [None]

                # Row for assist prompt.
                assist_prompt_frame = ttk.Frame(self.stat_detail_frame)
                assist_prompt_frame.grid(row=next_row(), column=0, pady=5)
                ttk.Label(assist_prompt_frame, text="Who did they assist?").pack(padx=5, pady=5)

                # Row for teammate selection.
                assisted_frame = ttk.Frame(self.stat_detail_frame)
                assisted_frame.grid(row=next_row(), column=0, pady=5)
                btn_frame = ttk.Frame(assisted_frame)
                btn_frame.pack(padx=5, pady=5)
                teammates = [p for p in self.test_data.db["Players"]
                             if p["PlayerID"] in self.currentLineup and p.get("TeamID") == player.get("TeamID")
                             and p["PlayerID"] != player["PlayerID"]][:4]
                for col, mate in enumerate(teammates):
                    img = self.generate_jersey_image(mate["Jersey_Number"])
                    bg_color = "lightblue" if mate.get("TeamID") == player.get("TeamID") else "lightpink"
                    btn = tk.Button(btn_frame, image=img, relief="raised", borderwidth=2, bg=bg_color)
                    btn.image = img
                    btn.config(command=lambda pid=mate["PlayerID"], b=btn: make_assist_select(pid, b))
                    btn.grid(row=0, column=col, padx=5, pady=2)

                def make_assist_select(pid, btn):
                    if selected_assist_btn[0] is not None and selected_assist_btn[0].winfo_exists():
                        selected_assist_btn[0].config(relief="raised", padx=5)
                    assisted_player.set(pid)
                    selected_assist_btn[0] = btn
                    btn.config(relief="sunken", padx=15)
                    update_shot_type()

                # Row for shot type selection.
                shot_type_frame = ttk.Frame(self.stat_detail_frame)
                shot_type_frame.grid(row=next_row(), column=0, pady=5)

                def update_shot_type():
                    for widget in shot_type_frame.winfo_children():
                        widget.destroy()
                    ttk.Label(shot_type_frame, text="Was the assisted shot a 2 or a 3 pointer?").pack(padx=5, pady=5)
                    shot_rb_frame = ttk.Frame(shot_type_frame)
                    shot_rb_frame.pack(padx=5, pady=5)
                    ttk.Radiobutton(shot_rb_frame, text="2 Pointer", variable=shot_type_choice, value="2",
                                    command=update_foul_section).pack(side="left", padx=10)
                    ttk.Radiobutton(shot_rb_frame, text="3 Pointer", variable=shot_type_choice, value="3",
                                    command=update_foul_section).pack(side="left", padx=10)
                    update_foul_section()

                # Row for foul question – only shown once shot type is selected.
                foul_frame = ttk.Frame(self.stat_detail_frame)

                def update_foul_section():
                    for widget in foul_frame.winfo_children():
                        widget.destroy()
                    if shot_type_choice.get() in ["2", "3"]:
                        ttk.Label(foul_frame, text="Was the shooter fouled?").pack(padx=5, pady=5)
                        f_rb = ttk.Frame(foul_frame)
                        f_rb.pack(padx=5, pady=5)
                        ttk.Radiobutton(f_rb, text="Yes", variable=foul_choice, value="yes",
                                        command=update_free_throw_section).pack(side="left", padx=10)
                        ttk.Radiobutton(f_rb, text="No", variable=foul_choice, value="no",
                                        command=lambda: (clear_free_throw_frame(), update_submit())).pack(side="left",
                                                                                                          padx=10)
                        # Grid foul_frame in the next available row.
                        foul_frame.grid(row=next_row(), column=0, pady=5)
                    else:
                        foul_frame.grid_forget()
                    update_submit()

                # Row for free throw result – only appears if shooter was fouled.
                free_throw_frame = ttk.Frame(self.stat_detail_frame)

                def update_free_throw_section():
                    for widget in free_throw_frame.winfo_children():
                        widget.destroy()
                    if foul_choice.get() == "yes":
                        ttk.Label(free_throw_frame, text="Did the shooter make the free throw?").pack(padx=5, pady=5)
                        ft_rb = ttk.Frame(free_throw_frame)
                        ft_rb.pack(padx=5, pady=5)
                        ttk.Radiobutton(ft_rb, text="Made", variable=free_throw_result, value="made",
                                        command=update_submit).pack(side="left", padx=10)
                        ttk.Radiobutton(ft_rb, text="Missed", variable=free_throw_result, value="missed",
                                        command=update_submit).pack(side="left", padx=10)
                        # Instead of calling next_row(), place free_throw_frame directly beneath foul_frame.
                        row_of_foul = int(foul_frame.grid_info().get("row", 0))
                        free_throw_frame.grid(row=row_of_foul + 1, column=0, pady=5)
                    else:
                        free_throw_frame.grid_forget()
                    update_submit()

                def clear_free_throw_frame():
                    for widget in free_throw_frame.winfo_children():
                        widget.destroy()
                    free_throw_frame.grid_forget()

                # Row for submit button – placed relative to the last visible question.
                submit_frame = ttk.Frame(self.stat_detail_frame)

                def update_submit():
                    for widget in submit_frame.winfo_children():
                        widget.destroy()
                    if shot_type_choice.get() in ["2", "3"] and foul_choice.get() in ["yes", "no"]:
                        # If fouled, ensure free throw answer is given.
                        if foul_choice.get() == "yes" and free_throw_result.get() not in ["made", "missed"]:
                            submit_frame.grid_forget()
                            return
                        # Determine the base row: if free_throw_frame is visible, use its row; otherwise use foul_frame.
                        if foul_choice.get() == "yes" and free_throw_frame.winfo_ismapped():
                            base_row = int(free_throw_frame.grid_info().get("row", 0))
                        else:
                            base_row = int(foul_frame.grid_info().get("row", 0))
                        submit_frame.grid(row=base_row + 1, column=0, pady=5)
                        ttk.Button(submit_frame, text="Submit", command=submit_assist).grid(row=0, column=0, padx=5,
                                                                                            pady=5)

                def submit_assist():
                    game_id = self.selected_game_id
                    self.update_player_stats(game_id, player["PlayerID"], "assist")
                    if shot_type_choice.get() == "2":
                        self.update_player_stats(game_id, assisted_player.get(), "2pt_make")
                    elif shot_type_choice.get() == "3":
                        self.update_player_stats(game_id, assisted_player.get(), "3pt_make")
                    if foul_choice.get() == "yes":
                        if free_throw_result.get() == "made":
                            self.update_player_stats(game_id, assisted_player.get(), "ft_make")
                        elif free_throw_result.get() == "missed":
                            self.update_player_stats(game_id, assisted_player.get(), "ft_miss")
                    for widget in submit_frame.winfo_children():
                        widget.destroy()
                    ttk.Label(submit_frame, text="Assist recorded.").grid(row=0, column=0, padx=5, pady=5)
                    update_submit()

                update_submit()

            case "Blk":
                self.stat_detail_frame.config(text=f"Block by {player['Last_Name']}")
                for widget in self.stat_detail_frame.winfo_children():
                    widget.destroy()

                # Center content.
                self.stat_detail_frame.grid_columnconfigure(0, weight=1)

                # Retrieve game record for team info.
                game_rec = next((g for g in self.test_data.db["Games"] if g["GameID"] == self.selected_game_id), {})
                home_team_id = game_rec.get("HomeTeamID", None)
                away_team_id = game_rec.get("AwayTeamID", None)

                # Create persistent frames.
                block_prompt_frame = ttk.Frame(self.stat_detail_frame)
                block_prompt_frame.grid(row=0, column=0, pady=5)
                target_frame = ttk.Frame(self.stat_detail_frame)
                target_frame.grid(row=1, column=0, pady=5)
                shot_type_frame = ttk.Frame(self.stat_detail_frame)
                shot_type_frame.grid(row=2, column=0, pady=5)
                submit_frame = ttk.Frame(self.stat_detail_frame)
                submit_frame.grid(row=3, column=0, pady=5)

                # Control variables.
                blocked_player = tk.IntVar(value=0)
                shot_type_choice = tk.StringVar(value="")  # will be "2" or "3"
                selected_blocked_btn = [None]

                # Row 0: Header.
                ttk.Label(block_prompt_frame, text=f"Block by {player['Last_Name']}").pack(padx=5, pady=5)

                # Row 1: Ask which opponent was blocked.
                ttk.Label(target_frame, text="Who did you block?").pack(padx=5, pady=5)
                btn_frame = ttk.Frame(target_frame)
                btn_frame.pack(padx=5, pady=5)
                # Determine opposing team: if defender's team is home, then opposing team is away; else home.
                defender_team = player.get("TeamID")
                opposing_team = away_team_id if defender_team == home_team_id else home_team_id
                # Get up to five opponents from current on‑court players.
                opponents = [p for p in self.test_data.db["Players"]
                             if p["PlayerID"] in self.currentLineup and p.get("TeamID") == opposing_team][:5]
                col = 0
                for opp in opponents:
                    img = self.generate_jersey_image(opp["Jersey_Number"])
                    # Color-code: use lightblue if opponent is on the home team; otherwise lightpink.
                    bg_color = "lightblue" if opp.get("TeamID") == home_team_id else "lightpink"
                    btn = tk.Button(btn_frame, image=img, relief="raised", borderwidth=2, bg=bg_color)
                    btn.image = img
                    btn.config(command=lambda pid=opp["PlayerID"], b=btn: make_blocked_select(pid, b))
                    btn.grid(row=0, column=col, padx=5, pady=2)
                    col += 1

                def make_blocked_select(pid, btn):
                    if selected_blocked_btn[0] is not None and selected_blocked_btn[0].winfo_exists():
                        selected_blocked_btn[0].config(relief="raised", padx=5)
                    blocked_player.set(pid)
                    selected_blocked_btn[0] = btn
                    btn.config(relief="sunken", padx=15)
                    update_shot_type()

                # Row 2: Only display shot type selection after a blocked player is chosen.
                def update_shot_type():
                    for widget in shot_type_frame.winfo_children():
                        widget.destroy()
                    ttk.Label(shot_type_frame, text="Was the blocked shot a 2 or a 3 pointer?").pack(padx=5, pady=5)
                    shot_rb_frame = ttk.Frame(shot_type_frame)
                    shot_rb_frame.pack(padx=5, pady=5)
                    ttk.Radiobutton(shot_rb_frame, text="2 Pointer", variable=shot_type_choice, value="2",
                                    command=update_submit).pack(side="left", padx=10)
                    ttk.Radiobutton(shot_rb_frame, text="3 Pointer", variable=shot_type_choice, value="3",
                                    command=update_submit).pack(side="left", padx=10)
                    update_submit()

                # Row 3: Submit button.
                def update_submit():
                    for widget in submit_frame.winfo_children():
                        widget.destroy()
                    ttk.Button(submit_frame, text="Submit", command=lambda: submit_block()).grid(row=0, column=0,
                                                                                                 padx=5, pady=5)

                def submit_block():
                    game_id = self.selected_game_id
                    # Record the block for the defending player.
                    self.update_player_stats(game_id, player["PlayerID"], "block")
                    # If an opponent was selected and shot type is chosen, update that opponent's stat with a missed shot.
                    if blocked_player.get() != 0:
                        if shot_type_choice.get() == "2":
                            self.update_player_stats(game_id, blocked_player.get(), "2pt_miss")
                        elif shot_type_choice.get() == "3":
                            self.update_player_stats(game_id, blocked_player.get(), "3pt_miss")
                    for widget in submit_frame.winfo_children():
                        widget.destroy()
                    ttk.Label(submit_frame, text="Block recorded.").grid(row=0, column=0, padx=5, pady=5)

                update_submit()

            case "Foul":
                self.stat_detail_frame.config(text=f"Foul for {player['Last_Name']}")
                for widget in self.stat_detail_frame.winfo_children():
                    widget.destroy()
                self.stat_detail_frame.grid_columnconfigure(0, weight=1)

                # Fixed row indices for each section
                row_opp = 0
                row_shooting = 1
                row_shot_type = 2
                row_shot_made = 3
                row_free_throw = 4
                row_submit_yes = 5  # if shooting foul = "yes"
                row_submit_no = 2  # if shooting foul = "no" (submit appears immediately after shooting foul)

                # Control variables for answers.
                fouled_player = tk.IntVar(value=0)  # Selected opposing player.
                shooting_foul = tk.StringVar(value="")  # "yes" or "no"
                shot_type = tk.StringVar(value="")  # "2" or "3" (if shooting foul)
                shot_made = tk.StringVar(value="")  # "made" or "missed"
                free_throw_made = tk.StringVar(value="")  # For made shot branch.
                free_throws_made = tk.StringVar(value="")  # For missed shot branch.

                # Helper: Reset lower sections and clear their variables.
                # Level 1: Clear shot_type, shot_made, free throw answers.
                # Level 2: Clear shot_made and free throw answers.
                # Level 3: Clear free throw answers.
                def reset_from(level):
                    if level <= 1:
                        shot_type.set("")
                        shot_made.set("")
                        free_throw_made.set("")
                        free_throws_made.set("")
                        frame_shot_type.grid_forget()
                        frame_shot_made.grid_forget()
                        frame_free_throw.grid_forget()
                        frame_submit.grid_forget()
                        for f in (frame_shot_type, frame_shot_made, frame_free_throw, frame_submit):
                            for w in f.winfo_children():
                                w.destroy()
                    elif level <= 2:
                        shot_made.set("")
                        free_throw_made.set("")
                        free_throws_made.set("")
                        frame_shot_made.grid_forget()
                        frame_free_throw.grid_forget()
                        frame_submit.grid_forget()
                        for f in (frame_shot_made, frame_free_throw, frame_submit):
                            for w in f.winfo_children():
                                w.destroy()
                    elif level <= 3:
                        free_throw_made.set("")
                        free_throws_made.set("")
                        frame_free_throw.grid_forget()
                        frame_submit.grid_forget()
                        for f in (frame_free_throw, frame_submit):
                            for w in f.winfo_children():
                                w.destroy()

                # ------------------------------
                # Step 1: Opponent Selection (Row 0)
                # ------------------------------
                frame_opp = ttk.Frame(self.stat_detail_frame)
                frame_opp.grid(row=row_opp, column=0, pady=5)
                ttk.Label(frame_opp, text="Select the opposing player who was fouled:").pack(padx=5, pady=5)
                frame_opp_btn = ttk.Frame(frame_opp)
                frame_opp_btn.pack(padx=5, pady=5)
                selected_opp_btn = [None]
                shooter_team = player.get("TeamID")
                game_rec = next((g for g in self.test_data.db["Games"] if g["GameID"] == self.selected_game_id), {})
                home_team = game_rec.get("HomeTeamID")
                away_team = game_rec.get("AwayTeamID")
                opposing_team = away_team if shooter_team == home_team else home_team
                opponents = [p for p in self.test_data.db["Players"]
                             if p["PlayerID"] in self.currentLineup and p.get("TeamID") == opposing_team][:5]
                for col, opp in enumerate(opponents):
                    img = self.generate_jersey_image(opp["Jersey_Number"])
                    bg = "lightblue" if opp.get("TeamID") == home_team else "lightpink"
                    btn = tk.Button(frame_opp_btn, image=img, relief="raised", borderwidth=2, bg=bg)
                    btn.image = img
                    btn.config(command=lambda pid=opp["PlayerID"], b=btn: select_opp(pid, b))
                    btn.grid(row=0, column=col, padx=5, pady=2)

                def select_opp(pid, btn):
                    if selected_opp_btn[0] is not None and selected_opp_btn[0].winfo_exists():
                        selected_opp_btn[0].config(relief="raised", padx=5)
                    fouled_player.set(pid)
                    selected_opp_btn[0] = btn
                    btn.config(relief="sunken", padx=15)
                    # Reset lower sections when opponent changes.
                    shooting_foul.set("")
                    shot_type.set("")
                    shot_made.set("")
                    free_throw_made.set("")
                    free_throws_made.set("")
                    frame_shooting.grid_forget()
                    frame_shot_type.grid_forget()
                    frame_shot_made.grid_forget()
                    frame_free_throw.grid_forget()
                    frame_submit.grid_forget()
                    update_shooting_foul()

                # ------------------------------
                # Step 2: Shooting Foul Question (Row 1)
                # ------------------------------
                frame_shooting = ttk.Frame(self.stat_detail_frame)

                def update_shooting_foul():
                    for widget in frame_shooting.winfo_children():
                        widget.destroy()
                    ttk.Label(frame_shooting, text="Was it a shooting foul?").pack(padx=5, pady=5)
                    rb = ttk.Frame(frame_shooting)
                    rb.pack(padx=5, pady=5)
                    ttk.Radiobutton(rb, text="Yes", variable=shooting_foul, value="yes",
                                    command=lambda: [reset_from(2), update_shot_type()]).pack(side="left", padx=10)
                    ttk.Radiobutton(rb, text="No", variable=shooting_foul, value="no",
                                    command=lambda: [reset_from(1), update_submit()]).pack(side="left", padx=10)
                    frame_shooting.grid(row=row_shooting, column=0, pady=5)
                    update_submit()

                # ------------------------------
                # Step 3: Shot Type Question (if shooting foul) (Row 2)
                # ------------------------------
                frame_shot_type = ttk.Frame(self.stat_detail_frame)

                def update_shot_type():
                    for widget in frame_shot_type.winfo_children():
                        widget.destroy()
                    if shooting_foul.get() == "yes":
                        ttk.Label(frame_shot_type, text="Was it a 2 or 3 point shot?").pack(padx=5, pady=5)
                        rb = ttk.Frame(frame_shot_type)
                        rb.pack(padx=5, pady=5)
                        ttk.Radiobutton(rb, text="2 Pointer", variable=shot_type, value="2",
                                        command=lambda: [reset_from(3), update_shot_made()]).pack(side="left", padx=10)
                        ttk.Radiobutton(rb, text="3 Pointer", variable=shot_type, value="3",
                                        command=lambda: [reset_from(3), update_shot_made()]).pack(side="left", padx=10)
                        frame_shot_type.grid(row=row_shot_type, column=0, pady=5)
                    else:
                        frame_shot_type.grid_forget()
                    update_submit()

                # ------------------------------
                # Step 4: Shot Made Question (if shooting foul) (Row 3)
                # ------------------------------
                frame_shot_made = ttk.Frame(self.stat_detail_frame)

                def update_shot_made():
                    for widget in frame_shot_made.winfo_children():
                        widget.destroy()
                    if shooting_foul.get() == "yes" and shot_type.get() in ["2", "3"]:
                        ttk.Label(frame_shot_made, text="Did they make the shot?").pack(padx=5, pady=5)
                        rb = ttk.Frame(frame_shot_made)
                        rb.pack(padx=5, pady=5)
                        ttk.Radiobutton(rb, text="Made", variable=shot_made, value="made",
                                        command=update_free_throw).pack(side="left", padx=10)
                        ttk.Radiobutton(rb, text="Missed", variable=shot_made, value="missed",
                                        command=update_free_throw).pack(side="left", padx=10)
                        frame_shot_made.grid(row=row_shot_made, column=0, pady=5)
                    else:
                        frame_shot_made.grid_forget()
                    update_submit()

                # ------------------------------
                # Step 5: Free Throw Question (if shooting foul) (Row 4)
                # ------------------------------
                frame_free_throw = ttk.Frame(self.stat_detail_frame)

                def update_free_throw():
                    for widget in frame_free_throw.winfo_children():
                        widget.destroy()
                    if shooting_foul.get() == "yes" and shot_type.get() in ["2", "3"] and shot_made.get() in ["made",
                                                                                                              "missed"]:
                        if shot_made.get() == "made":
                            ttk.Label(frame_free_throw, text="Did they make their 1 free throw?").pack(padx=5, pady=5)
                            rb = ttk.Frame(frame_free_throw)
                            rb.pack(padx=5, pady=5)
                            ttk.Radiobutton(rb, text="Made", variable=free_throw_made, value="made",
                                            command=update_submit).pack(side="left", padx=10)
                            ttk.Radiobutton(rb, text="Missed", variable=free_throw_made, value="missed",
                                            command=update_submit).pack(side="left", padx=10)
                        elif shot_made.get() == "missed":
                            ttk.Label(frame_free_throw, text="How many free throws did they make?").pack(padx=5, pady=5)
                            rb = ttk.Frame(frame_free_throw)
                            rb.pack(padx=5, pady=5)
                            if shot_type.get() == "2":
                                for val in ["0", "1", "2"]:
                                    ttk.Radiobutton(rb, text=val, variable=free_throws_made, value=val,
                                                    command=update_submit).pack(side="left", padx=10)
                            elif shot_type.get() == "3":
                                for val in ["0", "1", "2", "3"]:
                                    ttk.Radiobutton(rb, text=val, variable=free_throws_made, value=val,
                                                    command=update_submit).pack(side="left", padx=10)
                        frame_free_throw.grid(row=row_free_throw, column=0, pady=5)
                    else:
                        frame_free_throw.grid_forget()
                    update_submit()

                # ------------------------------
                # Step 6: Submit Button
                # ------------------------------
                frame_submit = ttk.Frame(self.stat_detail_frame)

                def update_submit():
                    for widget in frame_submit.winfo_children():
                        widget.destroy()
                    # Conditions: Opponent selected and shooting foul answered.
                    if fouled_player.get() != 0 and shooting_foul.get() in ["yes", "no"]:
                        if shooting_foul.get() == "yes":
                            if shot_type.get() in ["2", "3"] and shot_made.get() in ["made", "missed"]:
                                if shot_made.get() == "made" and free_throw_made.get() in ["made", "missed"]:
                                    frame_submit.grid(row=row_submit_yes, column=0, pady=5)
                                    ttk.Button(frame_submit, text="Submit", command=submit_foul).grid(row=0, column=0,
                                                                                                      padx=5, pady=5)
                                elif shot_made.get() == "missed" and free_throws_made.get() in ["0", "1", "2", "3"]:
                                    frame_submit.grid(row=row_submit_yes, column=0, pady=5)
                                    ttk.Button(frame_submit, text="Submit", command=submit_foul).grid(row=0, column=0,
                                                                                                      padx=5, pady=5)
                        elif shooting_foul.get() == "no":
                            frame_submit.grid(row=row_shooting + 1, column=0, pady=5)
                            ttk.Button(frame_submit, text="Submit", command=submit_foul).grid(row=0, column=0, padx=5,
                                                                                              pady=5)

                def submit_foul():
                    game_id = self.selected_game_id
                    self.update_player_stats(game_id, player["PlayerID"], "foul")
                    if fouled_player.get() != 0:
                        self.update_player_stats(game_id, fouled_player.get(), "fouled")
                    if shooting_foul.get() == "yes":
                        if shot_made.get() == "made":
                            if free_throw_made.get() == "made":
                                self.update_player_stats(game_id, fouled_player.get(), "ft_make")
                            elif free_throw_made.get() == "missed":
                                self.update_player_stats(game_id, fouled_player.get(), "ft_miss")
                        elif shot_made.get() == "missed":
                            made_ft = int(free_throws_made.get())
                            self.update_player_stats(game_id, fouled_player.get(), f"ft_make_{made_ft}")
                    for widget in frame_submit.winfo_children():
                        widget.destroy()
                    ttk.Label(frame_submit, text="Foul recorded.").grid(row=0, column=0, padx=5, pady=5)
                    update_submit()

                # Start the flow by printing the shooting foul question.
                update_shooting_foul()

            case "Reb":
                self.stat_detail_frame.config(text=f"Rebound for {player['Last_Name']}")
                for widget in self.stat_detail_frame.winfo_children():
                    widget.destroy()
                self.stat_detail_frame.grid_columnconfigure(0, weight=1)

                prompt_frame = ttk.Frame(self.stat_detail_frame)
                prompt_frame.grid(row=0, column=0, pady=5)
                ttk.Label(prompt_frame, text="Confirm rebound:").pack(padx=5, pady=5)

                confirm_frame = ttk.Frame(self.stat_detail_frame)
                confirm_frame.grid(row=1, column=0, pady=5)
                ttk.Button(confirm_frame, text="Record Rebound",
                           command=lambda: record_rebound(player)).pack(padx=5, pady=5)

                def record_rebound(p):
                    game_id = self.selected_game_id
                    self.update_player_stats(game_id, p["PlayerID"], "rebound")
                    for widget in self.stat_detail_frame.winfo_children():
                        widget.destroy()
                    ttk.Label(self.stat_detail_frame, text="Rebound recorded.").pack(padx=5, pady=5)

            case "FT":
                self.stat_detail_frame.config(text=f"Free Throw for {player['Last_Name']}")
                for widget in self.stat_detail_frame.winfo_children():
                    widget.destroy()
                self.stat_detail_frame.grid_columnconfigure(0, weight=1)

                # Define functions first
                def update_ft_submit():
                    for widget in ft_submit_frame.winfo_children():
                        widget.destroy()
                    if ft_choice.get() in ["made", "missed"]:
                        ttk.Button(ft_submit_frame, text="Record Free Throw",
                                   command=lambda: record_free_throw(player, ft_choice.get())).pack(padx=5, pady=5)

                def record_free_throw(p, result):
                    game_id = self.selected_game_id
                    if result == "made":
                        self.update_player_stats(game_id, p["PlayerID"], "ft_make")
                    else:
                        self.update_player_stats(game_id, p["PlayerID"], "ft_miss")
                    for widget in self.stat_detail_frame.winfo_children():
                        widget.destroy()
                    ttk.Label(self.stat_detail_frame, text="Free throw recorded.").pack(padx=5, pady=5)

                # Now build the UI.
                prompt_frame = ttk.Frame(self.stat_detail_frame)
                prompt_frame.grid(row=0, column=0, pady=5)
                ttk.Label(prompt_frame, text="Did you make the free throw?").pack(padx=5, pady=5)

                ft_choice = tk.StringVar(value="")
                options_frame = ttk.Frame(self.stat_detail_frame)
                options_frame.grid(row=1, column=0, pady=5)
                ttk.Radiobutton(options_frame, text="Made", variable=ft_choice, value="made",
                                command=update_ft_submit).pack(side="left", padx=10)
                ttk.Radiobutton(options_frame, text="Missed", variable=ft_choice, value="missed",
                                command=update_ft_submit).pack(side="left", padx=10)

                ft_submit_frame = ttk.Frame(self.stat_detail_frame)
                ft_submit_frame.grid(row=2, column=0, pady=5)

            case "jersey":
                self.stat_detail_frame.config(text=f"Substitution for {player['Last_Name']}")
                for widget in self.stat_detail_frame.winfo_children():
                    widget.destroy()

                # Retrieve the game record for team info.
                game_rec = next((g for g in self.test_data.db["Games"] if g["GameID"] == self.selected_game_id), {})
                home_team_id = game_rec.get("HomeTeamID", None)
                away_team_id = game_rec.get("AwayTeamID", None)
                _htid = home_team_id  # capture locally for lambda use

                # Determine the team of the current on-court player (being substituted out).
                team_id = player.get("TeamID")
                # Get bench players for that team.
                bench_list = self.bench.get(team_id, [])
                bench_players = [p for p in self.test_data.db["Players"] if p["PlayerID"] in bench_list]
                if not bench_players:
                    ttk.Label(self.stat_detail_frame, text="No bench players available for substitution.").pack(padx=5, pady=5)
                    return

                # Create a frame to list bench players in a grid (2 per row).
                bench_frame = ttk.Frame(self.stat_detail_frame)
                bench_frame.pack(padx=5, pady=5)
                ttk.Label(bench_frame, text="Select a bench player to substitute in:").grid(row=0, column=0, columnspan=2, padx=5, pady=5)

                # Control variable for the selected substitution.
                selected_sub_player = tk.IntVar(value=0)
                # For tracking which bench jersey button is selected.
                selected_sub_btn = [None]

                def make_sub_select(pid, btn):
                    if selected_sub_btn[0] is not None and selected_sub_btn[0].winfo_exists():
                        selected_sub_btn[0].config(relief="raised")
                    selected_sub_player.set(pid)
                    selected_sub_btn[0] = btn
                    btn.config(relief="sunken")

                # Display bench players in a grid with 2 columns.
                for index, bench_player in enumerate(bench_players):
                    row = index // 2 + 1  # starting at row 1 (row 0 is header)
                    col = index % 2
                    bp_frame = ttk.Frame(bench_frame)
                    bp_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
                    img = self.generate_jersey_image(bench_player["Jersey_Number"])
                    # Color code background: lightblue for home, lightpink for away.
                    bg_color = "lightblue" if bench_player.get("TeamID") == team_id and team_id == _htid else "lightpink"
                    btn = tk.Button(bp_frame, image=img, relief="raised", borderwidth=2, bg=bg_color)
                    btn.image = img
                    btn.config(command=lambda pid=bench_player["PlayerID"], b=btn: make_sub_select(pid, b))
                    btn.pack(side="left", padx=5)
                    info = f"{bench_player['Last_Name']}\n({bench_player['Position']})"
                    ttk.Label(bp_frame, text=info).pack(side="left", padx=5)

                # Create a submit button.
                submit_frame = ttk.Frame(self.stat_detail_frame)
                submit_frame.pack(padx=5, pady=5)
                ttk.Button(submit_frame, text="Submit Substitution", command=lambda: submit_substitution()).pack(padx=5, pady=5)

                def submit_substitution():
                    sub_in_id = selected_sub_player.get()
                    if sub_in_id == 0:
                        ttk.Label(self.stat_detail_frame, text="Please select a bench player.").pack(padx=5, pady=5)
                        return

                    # Swap the on-court player with the selected bench player in self.currentLineup.
                    try:
                        idx = self.currentLineup.index(player["PlayerID"])
                        self.currentLineup[idx] = sub_in_id
                    except ValueError:
                        self.currentLineup.append(sub_in_id)

                    # Update the bench array: remove the incoming player and add the outgoing one.
                    if team_id in self.bench:
                        if sub_in_id in self.bench[team_id]:
                            self.bench[team_id].remove(sub_in_id)
                        if player["PlayerID"] not in self.bench[team_id]:
                            self.bench[team_id].append(player["PlayerID"])

                    # Now, instead of updating only the affected row,
                    # refresh the game UI using the new update_game_ui_with_lineup method.
                    self.update_game_ui_with_lineup(self.currentLineup, self.bench)

                # End of substitution case (no break statement)

            case _:
                self.stat_detail_frame.config(text=f"Stat '{stat}' for {player['Last_Name']}")
                ttk.Label(self.stat_detail_frame, text=f"Form placeholder for {stat}").pack(padx=5, pady=5)


if __name__ == '__main__':
    app = MainMenu()
    app.mainloop()
