import tkinter as tk
from tkinter import ttk, font
from datetime import date, timedelta

class BasketballManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Basketball Manager")
        self.geometry("1000x600")
        
        # Load Europe Underground Regular font
        self.load_custom_font()
        
        # colors for different game states
        self.colors = {
            'future': "#d0e8ff",  # light blue for games that haven't happened yet
            'won': "#c2ffc2",     # light green for games won
            'lost': "#ffcece",    # light red for games lost
            'selected': "#7aceff", # darker blue for the game you clicked on
        }
        
        # set up the visual styles
        self.configure_styles()
        
        # create the main tab system
        self.tab_control = ttk.Notebook(self)
        
        # make the individual tabs
        self.schedule_tab = ttk.Frame(self.tab_control)
        self.game_tab = ttk.Frame(self.tab_control)
        self.teams_tab = ttk.Frame(self.tab_control)
        self.players_tab = ttk.Frame(self.tab_control)
        
        # add the tabs to the main window
        self.tab_control.add(self.schedule_tab, text='Schedule')
        self.tab_control.add(self.game_tab, text='Game')
        self.tab_control.add(self.teams_tab, text='Teams')
        self.tab_control.add(self.players_tab, text='Players')
        
        self.tab_control.pack(expand=1, fill="both")
        
        # create the schedule view with game list and details
        self.setup_schedule_tab()
    
    def load_custom_font(self):
        """Load the Europe Underground Regular font from file"""
        try:
            # Specify the path to your font file
            font_path = "/fonts/europeunderground_black.ttf"  # Update this with your actual font filename
            
            # Register the font with Tkinter
            font_id = font.Font(font=font_path, family="Europe Underground Regular")
            
            # Set font name and sizes
            self.custom_font_name = "Europe Underground Regular"
            self.font_size_normal = 10
            self.font_size_title = 16
            self.font_size_subtitle = 14
            
            # Use the registered font
            self.custom_font = self.custom_font_name
            
            print(f"Successfully loaded '{self.custom_font_name}' font.")
        except Exception as e:
            print(f"Error loading custom font: {e}")
            print("Falling back to default font (Arial)")
            self.custom_font = "Arial"
            self.custom_font_name = "Arial"
            self.font_size_normal = 10
            self.font_size_title = 16
            self.font_size_subtitle = 14
    
    def configure_styles(self):
        """set up all the colors and fonts for the app"""
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Define fonts to use throughout the application
        self.normal_font = (self.custom_font, self.font_size_normal)
        self.title_font = (self.custom_font, self.font_size_title)
        self.subtitle_font = (self.custom_font, self.font_size_subtitle)
        
        # styles for different game outcomes
        style.configure('Won.TFrame', background=self.colors['won'])
        style.configure('Lost.TFrame', background=self.colors['lost'])
        style.configure('Future.TFrame', background=self.colors['future'])
        
        # matching text styles for each type of game
        style.configure('Won.TLabel', 
                        font=self.normal_font, 
                        background=self.colors['won'])
        
        style.configure('Lost.TLabel', 
                        font=self.normal_font, 
                        background=self.colors['lost'])
        
        style.configure('Future.TLabel', 
                        font=self.normal_font, 
                        background=self.colors['future'])
        
        # Configure notebook (tab) font
        style.configure('TNotebook.Tab', font=self.normal_font)
    
    def setup_schedule_tab(self):
        """create the two-panel view for the schedule tab"""
        # split the tab into two parts: game list (25% width) and game details (75% width)
        paned_window = ttk.PanedWindow(self.schedule_tab, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # left side - game list
        self.schedule_frame = ttk.Frame(paned_window)
        
        # right side - game details
        self.details_frame = ttk.Frame(paned_window)
        
        # add both panels to the window with proper sizes
        paned_window.add(self.schedule_frame, weight=25)
        paned_window.add(self.details_frame, weight=75)
        
        # create the scrollable game list
        self.setup_schedule_list()
        
        # set up the right panel that shows game info
        self.setup_details_area()
    
    def setup_details_area(self):
        """create the area that shows game details when you click a game"""
        # center everything in the details panel
        details_container = tk.Frame(self.details_frame)
        style = ttk.Style()
        bg_color = style.lookup('TFrame', 'background')
        details_container.configure(bg=bg_color)
        details_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # game title at the top
        self.game_title_label = tk.Label(
            details_container,
            text="Game Details: 2025-03-14",
            font=self.title_font,
            bg=details_container.cget("background")
        )
        self.game_title_label.pack(pady=(0, 10))
        
        # game status beneath the title
        self.game_status_label = tk.Label(
            details_container,
            text="Status: Lost",
            font=self.subtitle_font,
            bg=details_container.cget("background")
        )
        self.game_status_label.pack()
    
    def setup_schedule_list(self):
        """create the scrollable list of games with win/loss colors"""
        # container to hold everything
        container_frame = tk.Frame(self.schedule_frame)
        container_frame.pack(fill=tk.BOTH, expand=True)
        
        # canvas for smooth scrolling
        self.schedule_canvas = tk.Canvas(
            container_frame, 
            bg="#f5f5f5", 
            highlightthickness=0
        )
        
        # scrollbar on the right side
        self.scrollbar = ttk.Scrollbar(
            container_frame, 
            orient=tk.VERTICAL, 
            command=self.schedule_canvas.yview
        )
        
        # link the scrollbar to the canvas
        self.schedule_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # make sure the canvas shows all content when scrolling
        self.schedule_canvas.bind('<Configure>', 
                                 lambda e: self.schedule_canvas.configure(
                                     scrollregion=self.schedule_canvas.bbox("all")
                                 ))
        
        # position everything
        self.schedule_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # let users scroll with the mouse wheel
        self.schedule_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # frame inside the canvas that holds the actual game entries
        self.scrollable_frame = tk.Frame(self.schedule_canvas, bg="#f5f5f5")
        
        # put the frame in the canvas and make it fill the width
        self.canvas_window = self.schedule_canvas.create_window(
            (0, 0), 
            window=self.scrollable_frame, 
            anchor="nw",
            width=self.schedule_canvas.winfo_width()
        )
        
        # make sure the frame stays full width when window resizes
        self.schedule_canvas.bind("<Configure>", self._on_canvas_resize)
        
        # fill the list with games
        self.populate_schedule()
    
    def _on_canvas_resize(self, event):
        """make the scrollable content fit the width when window size changes"""
        # update the frame to match the canvas width
        self.schedule_canvas.itemconfig(self.canvas_window, width=event.width)
    
    def populate_schedule(self):
        """create all the game entries with proper colors based on win/loss/future"""
        # start with games from March 1, 2025
        start_date = date(2025, 3, 1)
        current_date = date(2025, 3, 20)  # today's date in the app
        
        # pre-set which games were wins and losses (just for demo purposes)
        win_loss_pattern = {
            1: 'lost', 2: 'lost', 3: 'won', 4: 'won', 5: 'won',
            6: 'won', 7: 'lost', 8: 'won', 9: 'won', 10: 'won',
            11: 'lost', 12: 'won', 13: 'lost', 14: 'won'
        }
        
        # create 40 days worth of games
        for i in range(40):
            game_date = start_date + timedelta(days=i)
            day_str = game_date.strftime("%Y-%m-%d")
            
            # make the team names
            if game_date.month == 3:
                team_num = game_date.day + 15
                game_text = f"{day_str} | Team{team_num} vs Team{team_num+1} @ Arena {team_num}"
            else:
                team_num = game_date.day
                game_text = f"{day_str} | Team{team_num} vs Team{team_num+1} @ Arena {team_num}"
            
            # figure out if this game is in the future, won, or lost
            if game_date > current_date:
                game_status = 'future'
                bg_color = self.colors['future']
            else:
                # for past games, check if it was a win or loss
                if game_date.day in win_loss_pattern:
                    game_status = win_loss_pattern[game_date.day]
                    bg_color = self.colors['won'] if game_status == 'won' else self.colors['lost']
                else:
                    game_status = 'lost'
                    bg_color = self.colors['lost']
            
            # create the row for this game
            game_frame = tk.Frame(
                self.scrollable_frame,
                bg=bg_color,
                height=30
            )
            game_frame.pack(fill=tk.X, padx=0, pady=1)
            
            # add the game text
            game_label = tk.Label(
                game_frame,
                text=game_text,
                font=self.normal_font,
                bg=bg_color,
                anchor='w',
                padx=5,
                pady=5
            )
            game_label.pack(fill=tk.X)
            
            # make both the row and text clickable
            game_frame.bind("<Button-1>", lambda e, d=day_str, s=game_status: self.select_game(d, s))
            game_label.bind("<Button-1>", lambda e, d=day_str, s=game_status: self.select_game(d, s))
    
    def select_game(self, date_str, status):
        """update the details panel when a game is clicked"""
        # update the details text
        self.game_title_label.config(text=f"Game Details: {date_str}")
        self.game_status_label.config(text=f"Status: {status.capitalize()}")
    
    def _on_mousewheel(self, event):
        """handle mouse wheel scrolling of the game list"""
        # scroll up or down based on wheel direction
        scroll_amount = -1 * (event.delta // 120)
        self.schedule_canvas.yview_scroll(scroll_amount, "units")

if __name__ == "__main__":
    app = BasketballManager()
    app.mainloop()
