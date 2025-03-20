import tkinter as tk
import os
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import date, timedelta
from config import UI_ELEMENTS
from tests_data import TestData


class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Basketball Manager")
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

        # I used a normal tk.Frame so bg="white" can be set
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

        # ---------- RIGHT 75%: Game Details UI ----------
        self.details_box = ttk.Frame(self.schedule_frame, relief="sunken", borderwidth=2)
        self.details_box.pack(side="left", fill="both", expand=True)

        # Container inside details box (centering contents)
        self.details_container = ttk.Frame(self.details_box)
        self.details_container.pack(expand=True)

        # Placeholder label before selection
        self.details_placeholder = ttk.Label(
            self.details_container,
            text="Click a game to view details",
            font=("Helvetica", 14, "italic")
        )
        self.details_placeholder.pack(anchor="center", expand=True)

        # Instantiate our fake data class
        self.test_data = TestData()

        self.selected_game_index = None
        self.game_buttons = []  # Store (button_widget, is_past, game_data)

        self.build_schedule_contents()

        self.bind("<Configure>", self._adjust_schedule_layout)

        # Additional tabs
        game_tab = ttk.Frame(self.notebook)
        self.notebook.add(game_tab, text='Game')
        ttk.Label(game_tab, text="No Game loaded.").pack(padx=10, pady=10)

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
                command=lambda idx=idx: self.select_game(idx)
            )
            btn.pack(padx=10, pady=5, fill="x")

            self.game_buttons.append((btn, is_past, game_data))

        if today_index is not None:
            self.after(100, lambda: self.scroll_near_today(today_index, offset=4))

    def select_game(self, index):
        """
        Called when the user selects a game. Updates the UI with detailed game stats.
        """
        # Reset the previously selected game button
        if self.selected_game_index is not None:
            old_btn, old_is_past, _ = self.game_buttons[self.selected_game_index]
            old_btn.configure(style='Past.TButton' if old_is_past else 'Default.TButton')

        # Set the new game as selected
        btn, is_past, game_data = self.game_buttons[index]
        btn.configure(style='Selected.TButton')
        self.selected_game_index = index

        # Fetch game details from TestData
        details = self.test_data.get_game_details(game_data)

        # Update the UI
        self.update_game_details_ui(game_data, details)

    def display_player_stats(self, parent, player, role="Starter"):
        """
        Displays an individual player's stats in the correct format.
        """
        info = (
            f"{role[:1]} #{player['number']:>2} {player['name']:<12} "
            f"Pts: {player['points']} | Ast: {player['assists']} | Reb: {player['rebounds']}"
        )
        ttk.Label(parent, text=info, font=("Helvetica", 10)).pack(anchor="w", padx=5, pady=2)

    def _adjust_schedule_layout(self, event=None):
        total_w = self.schedule_frame.winfo_width()
        if total_w > 0:
            self.schedule_list_frame.config(width=int(total_w * 0.25))
            self.details_box.config(width=int(total_w * 0.75))

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
        """Ensures the mouse wheel only works on the schedule tab."""
        tab_text = self.notebook.tab(self.notebook.select(), 'text')
        if tab_text == 'Schedule':
            self.bind_all("<MouseWheel>", self._on_mousewheel_global_win)
        else:
            self.unbind_all("<MouseWheel>")

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
        """
        # Clear the previous details
        for widget in self.details_container.winfo_children():
            widget.destroy()

        # Header with score
        score_label = ttk.Label(
            self.details_container,
            text=f"{game_data['home']} ({details['home_score']}) vs {game_data['away']} ({details['away_score']})",
            font=("Helvetica", 16, "bold")
        )
        score_label.pack(anchor="center", pady=10)

        # Create a frame to hold both teams' stats
        teams_frame = ttk.Frame(self.details_container)
        teams_frame.pack(expand=True, pady=10)

        # Create frames for Home & Away teams
        home_frame = ttk.Frame(teams_frame)
        home_frame.grid(row=0, column=0, padx=30, sticky="n")

        away_frame = ttk.Frame(teams_frame)
        away_frame.grid(row=0, column=1, padx=30, sticky="n")

        # Home team header
        ttk.Label(home_frame, text=f"{game_data['home']} (Home)", font=("Helvetica", 12, "bold")).pack()
        ttk.Label(home_frame, text="Starters:", font=("Helvetica", 10, "underline")).pack(pady=(10, 0))

        # Home Starters
        for p in details["home_players"][:5]:
            self.display_player_stats(home_frame, p, role="Starter")

        ttk.Label(home_frame, text="Bench:", font=("Helvetica", 10, "underline")).pack(pady=(10, 0))

        # Home Bench
        for p in details["home_players"][5:]:
            self.display_player_stats(home_frame, p, role="Bench")

        # Away team header
        ttk.Label(away_frame, text=f"{game_data['away']} (Away)", font=("Helvetica", 12, "bold")).pack()
        ttk.Label(away_frame, text="Starters:", font=("Helvetica", 10, "underline")).pack(pady=(10, 0))

        # Away Starters
        for p in details["away_players"][:5]:
            self.display_player_stats(away_frame, p, role="Starter")

        ttk.Label(away_frame, text="Bench:", font=("Helvetica", 10, "underline")).pack(pady=(10, 0))

        # Away Bench
        for p in details["away_players"][5:]:
            self.display_player_stats(away_frame, p, role="Bench")



if __name__ == '__main__':
    app = MainMenu()
    app.mainloop()
