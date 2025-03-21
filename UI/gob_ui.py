import random
import tkinter as tk
import os
from tkinter import ttk
from PIL import Image, ImageTk, ImageFont, ImageDraw
from datetime import date, timedelta
from config import UI_ELEMENTS
from tests_data import TestData


class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Basketball Manager")
        self.default_width = 1100
        self.default_height = 600
        self.geometry("1100x600")

        self.set_window_icon()

        # Configure styles
        style = ttk.Style(self)
        style.theme_use("clam")

        # Default button style
        style.configure('Default.TButton', background='#DDDDDD', foreground='black')

        # Past game style
        style.configure('Past.TButton', background='#AAAAAA', foreground='black')
        style.map('Past.TButton', background=[('active', '#999999')])

        # Selected game style
        style.configure('Selected.TButton', background='lightblue', foreground='black')
        style.map('Selected.TButton', background=[('active', '#87CEFA')])

        # Notebook tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        # ===================== Schedule Tab =====================
        self.schedule_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.schedule_tab, text='Schedule')
        self.bind("<Configure>", self._adjust_schedule_layout)

        # Main layout (25% schedule, 75% details)
        self.schedule_frame = ttk.Frame(self.schedule_tab)
        self.schedule_frame.pack(fill="both", expand=True)

        # ---------- LEFT 25%: Scrollable Schedule ----------
        self.schedule_list_frame = ttk.Frame(self.schedule_frame)
        self.schedule_list_frame.pack(side="left", fill="both")

        self.schedule_canvas = tk.Canvas(self.schedule_list_frame, bg="white")
        self.schedule_scrollbar = ttk.Scrollbar(
            self.schedule_list_frame, orient="vertical", command=self.schedule_canvas.yview
        )

        self.scrollable_schedule_frame = tk.Frame(self.schedule_canvas, bg="white")

        self.scrollable_schedule_frame.bind(
            "<Configure>",
            lambda e: self.schedule_canvas.configure(
                scrollregion=self.schedule_canvas.bbox("all")
            )
        )

        self.schedule_canvas.create_window((0, 0), window=self.scrollable_schedule_frame, anchor="nw")
        self.schedule_canvas.configure(yscrollcommand=self.schedule_scrollbar.set)

        self.schedule_canvas.pack(side="left", fill="both", expand=True)
        self.schedule_scrollbar.pack(side="right", fill="y")

        # ---------- RIGHT 75%: Game Details UI + Creator ----------
        self.details_box = ttk.Frame(self.schedule_frame, relief="sunken", borderwidth=2)
        self.details_box.pack(side="left", fill="both", expand=True)

        # Split vertically: top 75% for preview, bottom 25% for creator
        self.details_top = ttk.Frame(self.details_box)
        self.details_top.pack(fill="both", expand=True)

        self.details_bottom = ttk.Frame(self.details_box)
        self.details_bottom.pack(fill="x", pady=5)

        # ========== Top: Game Preview ==========
        self.details_container = ttk.Frame(self.details_top)
        self.details_container.pack(expand=True)

        self.details_placeholder = ttk.Label(
            self.details_container,
            text="Click a game to view details",
            font=("Helvetica", 14, "italic")
        )
        self.details_placeholder.pack(anchor="center", expand=True)

        # ========== Bottom: Game Creation UI ==========
        ttk.Label(self.details_bottom, text="Create New Game", font=("Helvetica", 12, "bold")).grid(
            row=0, column=0, columnspan=4, pady=(5, 5)
        )

        ttk.Label(self.details_bottom, text="Home Team:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.home_team_var = tk.StringVar()
        self.home_dropdown = ttk.Combobox(self.details_bottom, textvariable=self.home_team_var, state="readonly")
        self.home_dropdown.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(self.details_bottom, text="Away Team:").grid(row=1, column=2, sticky="e", padx=5, pady=2)
        self.away_team_var = tk.StringVar()
        self.away_dropdown = ttk.Combobox(self.details_bottom, textvariable=self.away_team_var, state="readonly")
        self.away_dropdown.grid(row=1, column=3, padx=5, pady=2)

        ttk.Label(self.details_bottom, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.date_entry = ttk.Entry(self.details_bottom)
        self.date_entry.insert(0, str(date.today() + timedelta(days=1)))
        self.date_entry.grid(row=2, column=1, padx=5, pady=2)

        self.create_button = ttk.Button(self.details_bottom, text="Create Game", command=self.create_new_game)
        self.create_button.grid(row=2, column=3, padx=5, pady=2)

        # Instantiate our fake data class
        self.test_data = TestData()

        self.selected_game_index = None
        self.game_buttons = []  # Store (button_widget, is_past, game_data)

        self.build_schedule_contents()

        self.bind("<Configure>", self._adjust_schedule_layout)

        # ===================== Game Tab =====================
        self.game_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.game_tab, text='Game')

        # GameID label (centered at the top)
        self.game_id_label = ttk.Label(self.game_tab, text="GameID: N/A", font=("Helvetica", 16, "bold"))
        self.game_id_label.pack(anchor="center", pady=10)

        # Jersey display placeholder (will be updated dynamically)
        style = ttk.Style()
        theme_bg = style.lookup('TFrame', 'background')
        self.jersey_canvas = tk.Canvas(self.game_tab, width=60, height=60, bg=theme_bg, highlightthickness=0, bd=0)

        self.jersey_canvas.pack(anchor="center", pady=20)

        teams_tab = ttk.Frame(self.notebook)
        self.notebook.add(teams_tab, text='Teams')
        ttk.Label(teams_tab, text="No Teams added.").pack(padx=10, pady=10)

        players_tab = ttk.Frame(self.notebook)
        self.notebook.add(players_tab, text='Players')
        ttk.Label(players_tab, text="No Players listed.").pack(padx=10, pady=10)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self._enable_scroll_wheel()

    # ======================================================
    #             BUILD SCHEDULE CONTENTS
    # ======================================================
    def build_schedule_contents(self):
        """ Builds the schedule buttons and stores references for resizing. """
        today = date.today()
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=50)

        games = self.test_data.get_schedule(start_date, end_date)

        line_inserted = False
        today_index = None

        for idx, game_data in enumerate(games):
            if today_index is None and game_data['date'] >= today:
                today_index = idx

            if not line_inserted and game_data['date'] >= today:
                line_frame = tk.Frame(self.scrollable_schedule_frame, bg='green', height=4)
                line_frame.pack(fill='x', pady=5)
                line_inserted = True

            day_str = game_data['date'].strftime("%Y-%m-%d")
            btn_text = f"{day_str} | {game_data['home']} vs {game_data['away']} @ {game_data['location']}"

            is_past = game_data['date'] < today
            style_to_use = 'Past.TButton' if is_past else 'Default.TButton'

            btn = ttk.Button(
                self.scrollable_schedule_frame,
                text=btn_text,
                style=style_to_use,
                width=40,  # Default width
                padding=(5, 5),  # Default padding
                command=lambda idx=idx: self.select_game(idx)
            )
            btn.pack(padx=10, pady=5, fill="x")

            self.game_buttons.append((btn, is_past, game_data))  # Store button reference

        if today_index is not None:
            self.after(100, lambda: self.scroll_near_today(today_index, offset=4))

    def select_game(self, index):
        """
        Called when the user selects a game.
        Fetches new data (including game_id) and updates the UI.
        """
        # Reset the previously selected game button
        if self.selected_game_index is not None:
            old_btn, old_is_past, _ = self.game_buttons[self.selected_game_index]
            old_btn.configure(style='Past.TButton' if old_is_past else 'Default.TButton')

        # Mark the new game as selected
        btn, is_past, game_data = self.game_buttons[index]
        btn.configure(style='Selected.TButton')
        self.selected_game_index = index

        # Fetch game details from TestData
        details = self.test_data.get_game_details(game_data)

        # 1) Store the game_id for other menus
        self.selected_game_id = details["game_id"]

        # 2) Update the UI with the scoreboard & players
        self.update_game_details_ui(game_data, details)

    def display_player_stats(self, parent, player, is_starter=False):
        """
        Shows:  Pos  |  #  | Last Name    | Pts | Ast | Reb | FG%
        - Uses only the player's last name
        - Truncates last names to 10 characters + "…"
        - Ensures monospaced columns line up properly
        - FG% displayed as a whole number with '%'
        """
        font_used = ("Consolas", 12, "bold") if is_starter else ("Consolas", 10)

        # Extract last name
        last_name = player["name"].split()[-1]  # Last word in name is assumed as last name
        if len(last_name) > 10:  # Truncate if longer than 10
            last_name = last_name[:9] + "…"  # Show first 9 characters + "…"

        pos = player.get("position", "???")
        fg_decimal = player.get("fg_pct", 0.0)
        fg_str = f"{int(fg_decimal * 100):}%"  # Convert decimal to percentage (e.g. 46%)

        # Ensure column alignment
        info = (
            f"{pos:<2} |"  # pos, left-just 2
            f"{player['number']:>2}|"  # #, right-just 2
            f"{last_name:<10}|"  # last name, left-just 10 max
            f"{player['points']:>2} |"  # points, right-just 2
            f"{player['assists']:>2} |"  # assists, right-just 2
            f"{player['rebounds']:>2} |"  # rebounds, right-just 2
            f"{fg_str:>3}"  # FG%, right-just 3
        )

        ttk.Label(parent, text=info, font=font_used).pack(anchor="w", padx=5)

    def _adjust_schedule_layout(self, event=None):
        """ Dynamically resizes the schedule buttons when the window size changes. """
        total_w = self.schedule_frame.winfo_width()
        total_h = self.schedule_frame.winfo_height()

        # Compute scaling factor based on window size vs default
        width_scale = total_w / self.default_width
        height_scale = total_h / self.default_height

        # Resize schedule frame proportions
        if total_w > 0:
            self.schedule_list_frame.config(width=int(total_w * 0.25))
            self.details_box.config(width=int(total_w * 0.75))

        # Resize buttons dynamically
        for btn, _, _ in self.game_buttons:
            new_width = max(20, int(40 * width_scale))  # Ensure min size
            new_padding_x = int(5 * width_scale)
            new_padding_y = int(5 * height_scale)

            btn.config(
                width=new_width,
                padding=(new_padding_x, new_padding_y)
            )

    def _enable_scroll_wheel(self):
        self.schedule_canvas.bind("<Enter>", lambda e: self.schedule_canvas.focus_set())

    def set_window_icon(self):
        ico_path = os.path.join(UI_ELEMENTS, "icon.ico")
        png_path = os.path.join(UI_ELEMENTS, "icon.png")
        if os.path.exists(ico_path):
            self.iconbitmap(ico_path)
        elif os.path.exists(png_path):
            img = Image.open(png_path).resize((32, 32), Image.Resampling.LANCZOS)
            icon_img = ImageTk.PhotoImage(img)
            self._icon_image = icon_img
            self.iconphoto(False, icon_img)

    def on_tab_changed(self, event):
        """Ensures the mouse wheel only works on the schedule tab and updates GameID when switching to the Game tab."""
        tab_text = self.notebook.tab(self.notebook.select(), 'text')

        if tab_text == 'Schedule':
            self.bind_all("<MouseWheel>", self._on_mousewheel_global_win)
        else:
            self.unbind_all("<MouseWheel>")

        if tab_text == 'Game':
            if hasattr(self, 'selected_game_id') and self.selected_game_id:
                self.game_id_label.config(text=f"GameID: {self.selected_game_id}")
                self.update_jersey_display()  # Generate jersey if game is selected
            else:
                self.game_id_label.config(text="GameID: No game selected")

    def _on_mousewheel_global_win(self, event):
        """Enable mouse wheel scrolling for the schedule canvas on Windows."""
        self.schedule_canvas.yview_scroll(int(-event.delta / 120), "units")

    def scroll_near_today(self, today_index, offset=4):
        """
        Scrolls the schedule so that 'today' is visible, with an offset of a few rows above.
        """
        if 0 <= today_index < len(self.game_buttons):
            adjusted_index = max(0, today_index - offset)
            self.scrollable_schedule_frame.update_idletasks()

            target_widget, _, _ = self.game_buttons[adjusted_index]
            y_coord = target_widget.winfo_y()
            total_height = self.scrollable_schedule_frame.winfo_height()

            fraction = y_coord / float(total_height)
            fraction = max(0.0, min(fraction, 1.0))
            self.schedule_canvas.yview_moveto(fraction)

    def update_game_details_ui(self, game_data, details):
        """
        Updates the game details panel with a clear, structured layout.
        Shows a scoreboard, then splits Home & Away teams.
        Starters get a larger/bold column header, and bench gets a normal header.
        """

        # 1) Clear the old details
        for widget in self.details_container.winfo_children():
            widget.destroy()

        # 2) Scoreboard label
        score_label = ttk.Label(
            self.details_container,
            text=f"{game_data['home']} ({details['home_score']}) vs {game_data['away']} ({details['away_score']})",
            font=("Helvetica", 16, "bold")
        )
        score_label.pack(anchor="center", pady=10)

        # 3) Container for Home & Away side-by-side
        teams_frame = ttk.Frame(self.details_container)
        teams_frame.pack(expand=True, pady=10)

        # --- Home Frame ---
        home_frame = ttk.Frame(teams_frame)
        home_frame.grid(row=0, column=0, padx=30, sticky="n")

        ttk.Label(home_frame, text=f"{game_data['home']} (Home)", font=("Helvetica", 12, "bold")).pack()

        # Starters
        ttk.Label(home_frame, text="Starters:", font=("Helvetica", 10, "underline")).pack(pady=(10, 0))
        self.display_column_headers(home_frame, is_starter=True)  # Bold/larger header
        for p in details["home_players"][:5]:
            self.display_player_stats(home_frame, p, is_starter=True)

        # Bench
        ttk.Label(home_frame, text="Bench:", font=("Helvetica", 10, "underline")).pack(pady=(10, 0))
        self.display_column_headers(home_frame, is_starter=False)  # Normal header
        for p in details["home_players"][5:]:
            self.display_player_stats(home_frame, p, is_starter=False)

        # --- Away Frame ---
        away_frame = ttk.Frame(teams_frame)
        away_frame.grid(row=0, column=1, padx=30, sticky="n")

        ttk.Label(away_frame, text=f"{game_data['away']} (Away)", font=("Helvetica", 12, "bold")).pack()

        # Starters
        ttk.Label(away_frame, text="Starters:", font=("Helvetica", 10, "underline")).pack(pady=(10, 0))
        self.display_column_headers(away_frame, is_starter=True)
        for p in details["away_players"][:5]:
            self.display_player_stats(away_frame, p, is_starter=True)

        # Bench
        ttk.Label(away_frame, text="Bench:", font=("Helvetica", 10, "underline")).pack(pady=(10, 0))
        self.display_column_headers(away_frame, is_starter=False)
        for p in details["away_players"][5:]:
            self.display_player_stats(away_frame, p, is_starter=False)

    def display_column_headers(self, parent, is_starter=False):
        """
        Renders:  Pos  |  #  | Name         | Pts | Ast | Reb | FG%
        Uses a bigger/bold monospaced font if is_starter=True,
        otherwise a smaller monospaced font.
        """
        # Monospaced font ensures columns line up
        font_used = ("Consolas", 12, "bold") if is_starter else ("Consolas", 10)
        # Must match the spacing in display_player_stats
        headers = "Pos|# | Name     |Pts|Ast|Reb|FG%"
        ttk.Label(parent, text=headers, font=font_used).pack(anchor="w", padx=5)

    def generate_jersey_image(self, number):
        """
        Loads Jersey.png, resizes to 60x60, and draws the player's number in the center.
        Ensures the background fully matches the Tkinter UI theme without borders.
        Returns a PhotoImage for Tkinter display.
        """
        jersey_path = os.path.join(UI_ELEMENTS, "Jersey.png")

        if not os.path.exists(jersey_path):
            print(f"Error: Jersey image not found at {jersey_path}")
            return None

        try:
            # ✅ Open the jersey image with RGBA mode (to preserve transparency)
            img = Image.open(jersey_path).convert("RGBA").resize((60, 60), Image.Resampling.LANCZOS)

            # ✅ Get the current theme background color
            style = ttk.Style()
            bg_color = style.lookup('TFrame', 'background')  # Dynamic theme color

            # ✅ Convert Tkinter theme color to RGB
            def tk_to_rgb(color):
                return self.winfo_rgb(color)[0] // 256, self.winfo_rgb(color)[1] // 256, self.winfo_rgb(color)[2] // 256

            bg_rgb = tk_to_rgb(bg_color)

            # ✅ FULLY REPLACE background (fills entire image)
            new_img = Image.new("RGBA", img.size, (*bg_rgb, 255))  # Fully solid background
            new_img.paste(img, (0, 0), img)  # Paste jersey while keeping its shape

            # ✅ Create a transparent overlay for text
            txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)

            # ✅ Use a basic default font
            font = ImageFont.load_default()
            text = str(number)

            # ✅ Get text size correctly
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (60 - text_width) // 2
            y = (60 - text_height) // 2

            # ✅ Draw number on transparent text layer
            draw.text((x, y), text, fill="black", font=font)

            # ✅ Merge text layer with the image
            final_image = Image.alpha_composite(new_img, txt_layer)

            return ImageTk.PhotoImage(final_image)

        except Exception as e:
            print(f"Error generating jersey image: {e}")
            return None

    def update_jersey_display(self):
        """ Updates the jersey display when switching to the Game tab. """
        if not hasattr(self, 'selected_game_id') or not self.selected_game_id:
            return  # Do nothing if no game is selected

        # Generate a random number for the jersey
        random_number = random.randint(1, 99)

        jersey_image = self.generate_jersey_image(random_number)
        if jersey_image:
            self.jersey_canvas.delete("all")  # Clear previous image
            self.jersey_canvas.create_image(30, 30, image=jersey_image)
            self.jersey_canvas.image = jersey_image  # Keep a reference to prevent garbage collection

    def create_new_game(self):
        home = self.home_team_var.get()
        away = self.away_team_var.get()
        date_str = self.date_entry.get()

        if not home or not away or home == away:
            print("Error: Teams must be selected and must be different.")
            return

        try:
            game_date = date.fromisoformat(date_str)
        except ValueError:
            print("Error: Invalid date format.")
            return

        new_game = {
            'date': game_date,
            'home': home,
            'away': away,
            'location': "Custom Arena"
        }

        # Insert into fake data and rebuild list
        self.test_data.manual_add_game(new_game)
        self.clear_schedule()
        self.build_schedule_contents()


if __name__ == '__main__':
    app = MainMenu()
    app.mainloop()
