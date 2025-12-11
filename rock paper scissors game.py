import tkinter as tk
import random
from tkinter import font as tkfont

class ArcadeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Rock Paper Scissors: Ultimate")
        self.root.geometry("760x520")
        self.root.configure(bg="#0f1720")

        self.game_mode = "computer"
        self.p1_score = 0
        self.p2_score = 0
        self.p1_move = None
        self.p2_move = None
        self.input_locked = False

        self.bg = "#0f1720"
        self.fg = "#E6EEF8"
        self.win_color = "#5DD39E"
        self.lose_color = "#FF6B6B"
        self.tie_color = "#9AA6B2"

        self.rainbow_colors = [
            "#FF6B6B", "#FFB86B", "#FFE66D",
            "#7BD389", "#6EC6FF", "#A58BFF", "#FF80BF"
        ]
        self.color_index = 0

        self.key_map = {
            'a': 'rock', 's': 'paper', 'd': 'scissors',
            'j': 'rock', 'k': 'paper', 'l': 'scissors'
        }

        self.font_title = tkfont.Font(family="Segoe UI", size=22, weight="bold")
        self.font_header = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        self.font_score = tkfont.Font(family="Segoe UI", size=26, weight="bold")
        self.font_medium = tkfont.Font(family="Segoe UI", size=14)
        self.font_small = tkfont.Font(family="Segoe UI", size=11)
        self.font_outcome = tkfont.Font(family="Segoe UI", size=20, weight="bold")

        self.create_widgets()
        self.root.bind("<Key>", self.on_key_press)

        self.animate_prompt()

    def create_widgets(self):
        self.title_label = tk.Label(
            self.root, text="Computer Mode (PvC)",
            bg=self.bg, fg=self.fg, font=self.font_title
        )
        self.title_label.pack(pady=10)

        self.btn_mode = tk.Button(
            self.root,
            text="Switch to 2-Player Mode",
            bg="#FFB86B", fg="#000",
            relief="flat", padx=10, pady=5,
            font=self.font_small,
            command=self.toggle_mode
        )
        self.btn_mode.pack(pady=5)

        tk.Label(
            self.root,
            text="P1: A / S / D    |    P2: J / K / L",
            bg=self.bg, fg="#9AA6B2",
            font=self.font_small
        ).pack()

        self.label_score = tk.Label(
            self.root, text="0  -  0",
            bg=self.bg, fg=self.fg, font=self.font_score
        )
        self.label_score.pack(pady=20)

        self.label_vs = tk.Label(
            self.root, text="---",
            bg=self.bg, fg="#9AA6B2", font=self.font_medium
        )
        self.label_vs.pack(pady=5)

        self.label_outcome = tk.Label(
            self.root, text="ENTER YOUR MOVE!",
            bg=self.bg, fg="#C46EFF", font=self.font_outcome
        )
        self.label_outcome.pack(pady=25)

        self.frame_status = tk.Frame(self.root, bg=self.bg)

        self.label_p1_status = tk.Label(
            self.frame_status,
            text="P1: Waiting...",
            bg=self.bg, fg="#98A0B3",
            font=self.font_small, width=20
        )
        self.label_p1_status.pack(side=tk.LEFT, padx=20)

        self.label_p2_status = tk.Label(
            self.frame_status,
            text="P2: Waiting...",
            bg=self.bg, fg="#98A0B3",
            font=self.font_small, width=20
        )
        self.label_p2_status.pack(side=tk.LEFT, padx=20)

    def on_key_press(self, event):
        if self.input_locked:
            return

        key = event.char.lower()
        if key not in self.key_map:
            return

        if self.game_mode == "computer":
            if key in ['a', 's', 'd']:
                self.p1_move = self.key_map[key]
                self.p2_move = random.choice(['rock', 'paper', 'scissors'])
                self.process_round("Player", "Computer")

        else:
            if key in ['a', 's', 'd']:
                self.p1_move = self.key_map[key]
                self.label_p1_status.config(text="P1: READY!", fg=self.win_color)

            elif key in ['j', 'k', 'l']:
                self.p2_move = self.key_map[key]
                self.label_p2_status.config(text="P2: READY!", fg=self.win_color)

            if self.p1_move and self.p2_move:
                self.process_round("Player 1", "Player 2")

    def process_round(self, name1, name2):
        self.input_locked = True

        if self.p1_move == self.p2_move:
            result_text = "It's a Tie!"
            result_color = self.tie_color
        elif (self.p1_move == 'rock' and self.p2_move == 'scissors') or \
             (self.p1_move == 'paper' and self.p2_move == 'rock') or \
             (self.p1_move == 'scissors' and self.p2_move == 'paper'):
            result_text = f"{name1} Wins!"
            result_color = self.win_color
            self.p1_score += 1
        else:
            result_text = f"{name2} Wins!"
            result_color = self.lose_color
            self.p2_score += 1

        self.label_vs.config(
            text=f"{self.p1_move.upper()}  vs  {self.p2_move.upper()}",
            fg="#C9D6E1"
        )
        self.label_outcome.config(text=result_text, fg=result_color)
        self.label_score.config(text=f"{self.p1_score}  -  {self.p2_score}")

        self.root.after(1500, self.start_next_round)

    def start_next_round(self):
        self.input_locked = False
        self.p1_move = None
        self.p2_move = None

        self.label_vs.config(text="---", fg="#9AA6B2")
        self.label_outcome.config(text="ENTER YOUR MOVE!", fg="#C46EFF")

        if self.game_mode == "pvp":
            self.label_p1_status.config(text="P1: Waiting...", fg="#98A0B3")
            self.label_p2_status.config(text="P2: Waiting...", fg="#98A0B3")

        self.animate_prompt()

    def animate_prompt(self):
        if self.input_locked:
            return

        color = self.rainbow_colors[self.color_index]
        self.label_outcome.config(fg=color)
        self.color_index = (self.color_index + 1) % len(self.rainbow_colors)

        self.root.after(250, self.animate_prompt)

    def toggle_mode(self):
        self.p1_score = 0
        self.p2_score = 0

        if self.game_mode == "computer":
            self.game_mode = "pvp"
            self.title_label.config(text="2-Player Mode (PvP)")
            self.btn_mode.config(text="Switch to Computer Mode", bg="#8BE28B")
            self.frame_status.pack(pady=5)

        else:
            self.game_mode = "computer"
            self.title_label.config(text="Computer Mode (PvC)")
            self.btn_mode.config(text="Switch to 2-Player Mode", bg="#FFB86B")
            self.frame_status.pack_forget()

        self.label_score.config(text="0  -  0")
        self.start_next_round()

if __name__ == "__main__":
    root = tk.Tk()
    app = ArcadeGame(root)
    root.mainloop()
