import random
import tkinter as tk
from tkinter import simpledialog, messagebox

BG_COLOR = "#1B2430"
TEXT_COLOR = "#ECF0F1"
ACCENT_COLOR = "#E74C3C"

CARD_COLORS = {
    'Red': '#FF5252',
    'Yellow': '#FFD740',
    'Green': '#69F0AE',
    'Blue': '#448AFF',
    'Wild': '#7C4DFF',
    'Black': '#212121'
}

class UnoCard:
    def __init__(self, color, value):
        self.color = color
        self.value = value

    def is_playable_on(self, top):
        if self.color == "Wild":
            return True
        return (self.color == top.color) or (self.value == top.value)

class Player:
    def __init__(self, name, is_human=True):
        self.name = name
        self.hand = []
        self.is_human = is_human

    def draw_card(self, deck):
        if deck:
            c = deck.pop(0)
            self.hand.append(c)
            return c
        return None

def create_deck():
    colors = ['Red', 'Yellow', 'Green', 'Blue']
    values = [str(i) for i in range(10)] + ['Skip', 'Reverse', '+2']
    d = []
    for col in colors:
        d.append(UnoCard(col, '0'))
        for v in values[1:]:
            d.extend([UnoCard(col, v), UnoCard(col, v)])
    d.extend([UnoCard('Wild', 'Wild')] * 4)
    d.extend([UnoCard('Wild', '+4')] * 4)
    random.shuffle(d)
    return d

class UnoAI:
    @staticmethod
    def choose_move(hand, top):
        playable = [i for i, c in enumerate(hand) if c.is_playable_on(top)]
        if not playable:
            return None
        regular = [i for i in playable if hand[i].color != "Wild"]
        if regular:
            actions = [i for i in regular if hand[i].value in ['Skip', 'Reverse', '+2']]
            return random.choice(actions) if actions else random.choice(regular)
        return random.choice(playable)

    @staticmethod
    def pick_color(hand):
        count = {'Red': 0, 'Yellow': 0, 'Green': 0, 'Blue': 0}
        for c in hand:
            if c.color in count:
                count[c.color] += 1
        return max(count, key=count.get) if max(count.values()) > 0 else "Red"

class ModernUnoGame:
    AI_DELAY = 1000

    def __init__(self, master, names):
        self.master = master
        self.master.title("UNO - Python Arcade")
        self.master.geometry("1200x850")
        self.master.configure(bg=BG_COLOR)

        self.deck = create_deck()
        self.discard_pile = []

        self.players = [Player(names[0], True)] + [Player(n, False) for n in names[1:]]
        self.turn_idx = 0
        self.direction = 1
        self.current_color = None
        self.game_active = True
        self.uno_called = {p.name: False for p in self.players}

        self._init_ui()
        self._deal_cards()
        self._start_game()

    def _init_ui(self):
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=2)
        self.master.rowconfigure(2, weight=2)

        self.frame_opponents = tk.Frame(self.master, bg=BG_COLOR)
        self.frame_opponents.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        self.opponent_widgets = []
        for i in range(1, 4):
            f = tk.LabelFrame(
                self.frame_opponents,
                text="Waiting...",
                font=("Helvetica", 16, "bold"),
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                bd=2,
                relief="groove"
            )
            f.pack(side="left", expand=True, fill="both", padx=15)

            lbl = tk.Label(f, text="7 Cards", font=("Helvetica", 16), bg=BG_COLOR, fg="#AAB7C4")
            lbl.pack(expand=True)

            self.opponent_widgets.append({"frame": f, "label": lbl})

        self.frame_table = tk.Frame(self.master, bg=BG_COLOR)
        self.frame_table.grid(row=1, column=0, pady=40)

        self.btn_draw = tk.Button(
            self.frame_table,
            text="DRAW\nDECK",
            font=("Arial", 18, "bold"),
            bg=CARD_COLORS["Black"],
            fg="white",
            width=14,
            height=7,
            bd=6,
            command=self._human_draw
        )
        self.btn_draw.pack(side="left", padx=50)

        self.lbl_discard = tk.Label(
            self.frame_table,
            text="?",
            font=("Arial", 32, "bold"),
            width=10,
            height=5,
            bd=6,
            relief="solid",
        )
        self.lbl_discard.pack(side="left", padx=50)

        self.lbl_color_status = tk.Label(
            self.frame_table,
            text="",
            bg=BG_COLOR,
            fg="white",
            font=("Verdana", 14, "bold")
        )
        self.lbl_color_status.pack(side="bottom", pady=10)

        self.lbl_status = tk.Label(
            self.master,
            text="Welcome to UNO!",
            font=("Verdana", 18),
            bg=BG_COLOR,
            fg="#F1C40F"
        )
        self.lbl_status.place(relx=0.5, rely=0.52, anchor="center")

        self.frame_hand = tk.LabelFrame(
            self.master,
            text="Your Hand",
            font=("Verdana", 14),
            bg=BG_COLOR,
            fg="white",
            bd=0
        )
        self.frame_hand.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)

        self.btn_uno = tk.Button(
            self.master,
            text="UNO!",
            bg=ACCENT_COLOR,
            fg="white",
            font=("Arial", 18, "bold"),
            width=6,
            command=self._human_uno,
            state="disabled"
        )
        self.btn_uno.place(relx=0.9, rely=0.82)

    def _deal_cards(self):
        for _ in range(7):
            for p in self.players:
                p.draw_card(self.deck)

    def _start_game(self):
        while True:
            c = self.deck.pop(0)
            if c.color != "Wild":
                self.discard_pile.append(c)
                self.current_color = c.color
                break
            self.deck.append(c)

        self._update_ui()
        self._process_turn()

    def _update_ui(self):
        top = self.discard_pile[-1]
        use_color = self.current_color if top.color == "Wild" else top.color
        hex_col = CARD_COLORS.get(use_color, "#333")
        fg = "black" if use_color in ["Yellow", "Green"] else "white"

        self.lbl_discard.config(
            text=f"{top.value}\n{top.color}",
            bg=hex_col,
            fg=fg
        )

        for i, w in enumerate(self.opponent_widgets):
            idx = i + 1
            if idx < len(self.players):
                p = self.players[idx]
                w["label"].config(text=f"{len(p.hand)} Cards")
                if idx == self.turn_idx:
                    w["frame"].config(text=f"➤ {p.name}", fg="#F1C40F")
                else:
                    w["frame"].config(text=p.name, fg=TEXT_COLOR)

        if self.players[self.turn_idx].is_human:
            self.lbl_status.config(text="YOUR TURN!", fg="#69F0AE")
        else:
            self.lbl_status.config(text=f"{self.players[self.turn_idx].name}'s Turn...", fg="#F1C40F")

        for w in self.frame_hand.winfo_children():
            w.destroy()

        human = self.players[0]
        for idx, c in enumerate(human.hand):
            bg = CARD_COLORS.get(c.color, "#333")
            fg = "black" if c.color == "Yellow" else "white"

            b = tk.Button(
                self.frame_hand,
                text=f"{c.value}\n{c.color}",
                bg=bg,
                fg=fg,
                font=("Arial", 14, "bold"),
                width=9,
                height=4,
                bd=4,
                command=lambda i=idx: self._human_play(i)
            )
            b.pack(side="left", padx=8)

            if self.turn_idx != 0:
                b.config(state="disabled")

        if self.turn_idx == 0 and len(human.hand) <= 2:
            self.btn_uno.config(state="normal")
        else:
            self.btn_uno.config(state="disabled")

    def _process_turn(self):
        if not self.game_active:
            return

        p = self.players[self.turn_idx]

        if len(p.hand) == 0:
            self._game_over(p)
            return

        if p.is_human:
            self.btn_draw.config(state="normal")
        else:
            self.btn_draw.config(state="disabled")
            self.master.after(self.AI_DELAY, self._ai_move)

        self._update_ui()

    def _next_turn(self, skip=False):
        curr = self.players[self.turn_idx]
        if len(curr.hand) > 1:
            self.uno_called[curr.name] = False

        step = 2 if skip else 1
        self.turn_idx = (self.turn_idx + step * self.direction) % len(self.players)
        self._process_turn()

    def _play_card_logic(self, player, idx):
        card = player.hand.pop(idx)
        self.discard_pile.append(card)

        skip = False

        if card.value == "Reverse":
            self.direction *= -1
            self.lbl_status.config(text=f"{player.name}: Reverse!", fg="#FF9999")

        elif card.value == "Skip":
            skip = True
            self.lbl_status.config(text=f"{player.name}: Skip!", fg="#FF9999")

        elif card.value == "+2":
            nxt = (self.turn_idx + self.direction) % len(self.players)
            self.players[nxt].draw_card(self.deck)
            self.players[nxt].draw_card(self.deck)
            skip = True
            self.lbl_status.config(text=f"{player.name}: +2 Hit!", fg="#FF9999")

        elif card.value == "+4":
            nxt = (self.turn_idx + self.direction) % len(self.players)
            for _ in range(4):
                self.players[nxt].draw_card(self.deck)
            skip = True
            self.lbl_status.config(text=f"{player.name}: +4 Hit!", fg="#FF9999")

        if card.color == "Wild":
            if player.is_human:
                col = simpledialog.askstring("Wild", "Color (Red/Blue/Green/Yellow)?")
                col = col.capitalize() if col else "Red"
                if col not in ['Red', 'Blue', 'Green', 'Yellow']:
                    col = "Red"
            else:
                col = UnoAI.pick_color(player.hand)
            self.current_color = col
        else:
            self.current_color = card.color

        self._next_turn(skip)

    def _human_play(self, idx):
        if not self.game_active or self.turn_idx != 0:
            return

        card = self.players[0].hand[idx]
        top = self.discard_pile[-1]

        eff_color = self.current_color if top.color == "Wild" else top.color
        eff_val = top.value

        valid = (
            card.color == "Wild" or
            card.color == eff_color or
            card.value == eff_val
        )

        if valid:
            self._play_card_logic(self.players[0], idx)
        else:
            messagebox.showwarning("Invalid", "You can't play that card!")

    def _human_draw(self):
        if not self.game_active or self.turn_idx != 0:
            return
        self.players[0].draw_card(self.deck)
        self._update_ui()
        self.master.after(600, self._next_turn)

    def _human_uno(self):
        self.uno_called[self.players[0].name] = True
        self.btn_uno.config(state="disabled")
        messagebox.showinfo("UNO!", "You called UNO!")

    def _ai_move(self):
        p = self.players[self.turn_idx]
        top = self.discard_pile[-1]

        eff_top = UnoCard(self.current_color, top.value) if top.color == "Wild" else top

        choice = UnoAI.choose_move(p.hand, eff_top)

        if choice is not None:
            self._play_card_logic(p, choice)
        else:
            self.lbl_status.config(text=f"{p.name} draws...", fg="#BDC3C7")
            p.draw_card(self.deck)
            self.master.after(600, self._next_turn)

    def _replenish_deck(self):
        if len(self.deck) < 2:
            top = self.discard_pile.pop()
            self.deck.extend(self.discard_pile)
            random.shuffle(self.deck)
            self.discard_pile = [top]

    def _game_over(self, winner):
        self.game_active = False
        messagebox.showinfo("GAME OVER", f"{winner.name} WINS!")
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    ModernUnoGame(root, ["You", "Maximus", "Cassandra", "Turing"])
    root.mainloop()
