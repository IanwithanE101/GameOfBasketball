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
        self.bind("<Configure>", self._adjust_schedule_layout)

        # Layout: left 25% (schedule), right 75% (details)
        self.schedule_frame = ttk.Frame(self.schedule_tab)
        self.schedule_frame.pack(fill="both", expand=True)

        # ---------- LEFT: Scrollable Schedule ----------
        self.schedule_list_frame = ttk.Frame(self.schedule_frame)
        self.schedule_list_frame.pack(side="left", fill="both")
        self.schedule_canvas = tk.Canvas(self.schedule_list_frame, bg="white")
        self.schedule_scrollbar = ttk.Scrollbar(self.schedule_list_frame, orient="vertical", command=self.schedule_canvas.yview)
        self.scrollable_schedule_frame = tk.Frame(self.schedule_canvas, bg="white")
        self.scrollable_schedule_frame.bind("<Configure>", lambda e: self.schedule_canvas.configure(scrollregion=self.schedule_canvas.bbox("all")))
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
        self.game_id_label = ttk.Label(self.game_tab, text="GameID: N/A", font=("Consolas", 16, "bold"))
        self.game_id_label.pack(anchor="center", pady=10)
        style = ttk.Style()
        theme_bg = style.lookup('TFrame', 'background')
        self.jersey_canvas = tk.Canvas(self.game_tab, width=60, height=60, bg=theme_bg, highlightthickness=0, bd=0)
        self.jersey_canvas.pack(anchor="center", pady=20)

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
        self.bind("<Configure>", self._adjust_schedule_layout)
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
        headers = f"{'Pos':<3}|{'#':<2}|{'Name':<15}|{'Pts':>3}|{'Ast':>3}|{'Reb':>3}|{'FG%':>3}"
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

    def _adjust_schedule_layout(self, event=None):
        total_w = self.schedule_frame.winfo_width()
        total_h = self.schedule_frame.winfo_height()
        if total_w > 0:
            self.schedule_list_frame.config(width=int(total_w * 0.25))
            self.details_box.config(width=int(total_w * 0.75))
        width_scale = total_w / self.default_width
        height_scale = total_h / self.default_height
        new_padding_x = int(5 * width_scale)
        new_padding_y = int(5 * height_scale)
        for btn, _, _ in self.game_buttons:
            btn.configure(padding=(new_padding_x, new_padding_y))

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
            if hasattr(self, 'selected_game_id') and self.selected_game_id:
                self.game_id_label.config(text=f"GameID: {self.selected_game_id}")
                self.update_jersey_display()
            else:
                self.game_id_label.config(text="GameID: No game selected")

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
        self.display_column_headers(home_frame, is_starter=True)
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
        self.display_column_headers(away_frame, is_starter=True)
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
            img = Image.open(jersey_path).convert("RGBA").resize((60, 60), Image.Resampling.LANCZOS)
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
            x = (60 - text_width) // 2
            y = (60 - text_height) // 2
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

if __name__ == '__main__':
    app = MainMenu()
    app.mainloop()
