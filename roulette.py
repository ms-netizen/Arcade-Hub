import pygame
import sys
import math
import random

pygame.init()

# ---------- Window / fonts ----------
WIDTH, HEIGHT = 960, 760
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Roulette (Pygame)")

FONT_SMALL  = pygame.font.SysFont("segoeui", 18)
FONT_MEDIUM = pygame.font.SysFont("segoeui", 22)
FONT_BIG    = pygame.font.SysFont("segoeui", 44, bold=True)

clock = pygame.time.Clock()

# ---------- Roulette data ----------
WHEEL_NUMBERS = [
    0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6,
    27, 13, 36, 11, 30, 8, 23, 10, 5, 24,
    16, 33, 1, 20, 14, 31, 9, 22, 18, 29,
    7, 28, 12, 35, 3, 26
]
N = len(WHEEL_NUMBERS)

RED_NUMBERS = {
    1, 3, 5, 7, 9, 12, 14, 16, 18, 19,
    21, 23, 25, 27, 30, 32, 34, 36
}

def get_color_name(num):
    if num == 0:
        return "green"
    return "red" if num in RED_NUMBERS else "black"

def get_color_rgb(num):
    if num == 0:
        return (0, 150, 70)
    return (200, 40, 40) if num in RED_NUMBERS else (20, 20, 20)

# ---------- Game state ----------
balance = 1000
bet_amount = 100
bet_type = "color"      # "color" or "number"
bet_target_color = "red"
bet_target_number = 17

message = "Place your bet and press SPIN"
last_result = None      # dict with number, color, win, payout, delta, balance

# ---------- Wheel state ----------
wheel_center = (WIDTH // 2, 300)
WHEEL_RADIUS = 220

wheel_angle = 0.0       # radians, rotation offset for the whole wheel
spin_speed = 0.0        # radians per frame
spinning = False

SECTOR_ANGLE = 2 * math.pi / N
FRICTION = 0.985        # < 1 => slows down
STOP_THRESHOLD = 0.003  # when |spin_speed| < this, stop

# ---------- UI helpers ----------
class Button:
    def __init__(self, rect, text, bg, fg=(255, 255, 255)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg = bg
        self.fg = fg
        self.hover = False

    def draw(self, surf):
        base = self.bg
        if self.hover:
            base = (min(255, base[0]+25),
                    min(255, base[1]+25),
                    min(255, base[2]+25))
        pygame.draw.rect(surf, base, self.rect, border_radius=8)
        pygame.draw.rect(surf, (20, 20, 20), self.rect, 2, border_radius=8)
        label = FONT_MEDIUM.render(self.text, True, self.fg)
        surf.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, event, callback):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                callback()

# Buttons
buttons = []

btn_dec_bet = Button((40, 620, 52, 38), "-₹", (70, 70, 70))
btn_inc_bet = Button((110, 620, 52, 38), "+₹", (70, 70, 70))

btn_red   = Button((360, 610, 96, 44), "RED",   (170, 40, 40))
btn_black = Button((470, 610, 96, 44), "BLACK", (25, 25, 25))
btn_green = Button((580, 610, 96, 44), "GREEN", (20, 120, 50))

btn_num_mode = Button((360, 660, 160, 38), "Number Mode", (80, 70, 140))
btn_dec_num  = Button((530, 660, 38, 38), "-", (70, 70, 70))
btn_inc_num  = Button((578, 660, 38, 38), "+", (70, 70, 70))

btn_spin = Button((740, 590, 140, 120), "SPIN", (210, 130, 40))


# ---------- Utility: which index is at the pointer? ----------

def pointer_index_from_angle(angle):
    """
    Pointer is at top (12 o'clock) which is angle -pi/2.
    We draw segment i centered at: base = 2*pi*i/N - pi/2 + wheel_angle
    Solve for i whose center is closest to -pi/2.
    Result: i ≈ - wheel_angle * N / (2*pi)
    """
    idx_float = - angle * N / (2 * math.pi)
    return int(round(idx_float)) % N


# ---------- Drawing the wheel ----------

def draw_wheel(surface, center, radius, rotation):
    cx, cy = center
    # Background & rim
    pygame.draw.circle(surface, (8, 8, 12), (cx+5, cy+6), radius+16)
    pygame.draw.circle(surface, (32, 32, 40), center, radius+10)
    pygame.draw.circle(surface, (4, 4, 8), center, radius+10, 2)

    for i, num in enumerate(WHEEL_NUMBERS):
        # Each sector center angle:
        mid_angle = (2 * math.pi * i / N) - math.pi / 2 + rotation

        col = get_color_rgb(num)

        # draw radial block for the sector
        inner_r = radius - 40
        outer_r = radius - 8
        x1 = cx + inner_r * math.cos(mid_angle)
        y1 = cy + inner_r * math.sin(mid_angle)
        x2 = cx + outer_r * math.cos(mid_angle)
        y2 = cy + outer_r * math.sin(mid_angle)
        pygame.draw.line(surface, col, (x1, y1), (x2, y2), 22)

        # draw number text
        text_r = radius - 75
        tx = cx + text_r * math.cos(mid_angle)
        ty = cy + text_r * math.sin(mid_angle)
        label = FONT_SMALL.render(str(num), True, (255, 255, 255))
        surface.blit(label, label.get_rect(center=(tx, ty)))

    # inner disk
    pygame.draw.circle(surface, (225, 225, 225), center, 42)
    pygame.draw.circle(surface, (80, 80, 80), center, 42, 3)


def draw_pointer(surface, center, radius):
    cx, cy = center
    tip   = (cx, cy - radius - 12)
    left  = (cx - 16, cy - radius + 16)
    right = (cx + 16, cy - radius + 16)
    pygame.draw.polygon(surface, (245, 220, 40), [tip, left, right])
    pygame.draw.circle(surface, (20, 20, 20), (cx, cy - radius + 10), 6)


def evaluate_spin(idx):
    global balance, message
    num = WHEEL_NUMBERS[idx]
    col_name = get_color_name(num)

    win = False
    payout = 0

    if bet_type == "color":
        if bet_target_color == col_name:
            if col_name == "green":
                payout = bet_amount * 35
            else:
                payout = bet_amount
            win = True
    else:   # number bet
        if bet_target_number == num:
            payout = bet_amount * 35
            win = True

    delta = payout if win else -bet_amount
    balance += delta

    result = {
        "number": num,
        "color": col_name,
        "win": win,
        "payout": payout,
        "delta": delta,
        "balance": balance
    }

    if win:
        message = f"You WON! {num} ({col_name.upper()})  +₹{payout}"
    else:
        message = f"You lost! {num} ({col_name.upper()})  -₹{bet_amount}"

    return result


# ---------- Main loop ----------
running = True
while running:
    dt = clock.tick(60) / 1000.0  # seconds per frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle button clicks
        btn_dec_bet.handle_event(event, lambda: globals().__setitem__("bet_amount", max(50, bet_amount - 50)))
        btn_inc_bet.handle_event(event, lambda: globals().__setitem__("bet_amount", min(20000, bet_amount + 50)))

        btn_red.handle_event(event,   lambda: (globals().__setitem__("bet_type", "color"),  globals().__setitem__("bet_target_color", "red")))
        btn_black.handle_event(event, lambda: (globals().__setitem__("bet_type", "color"),  globals().__setitem__("bet_target_color", "black")))
        btn_green.handle_event(event, lambda: (globals().__setitem__("bet_type", "color"),  globals().__setitem__("bet_target_color", "green")))

        btn_num_mode.handle_event(event, lambda: globals().__setitem__("bet_type", "number"))
        btn_dec_num.handle_event(event,  lambda: globals().__setitem__("bet_target_number", (bet_target_number - 1) % 37))
        btn_inc_num.handle_event(event,  lambda: globals().__setitem__("bet_target_number", (bet_target_number + 1) % 37))

        def spin_callback():
            global spinning, spin_speed, message, last_result
            if spinning:
                return
            if bet_amount > balance:
                message = "Not enough balance!"
                return
            spinning = True
            # start with random speed
            spin_speed = random.uniform(0.25, 0.45)   # radians per frame
            last_result = None
            message = "Spinning..."

        btn_spin.handle_event(event, spin_callback)

    # ----- Update wheel rotation -----
    if spinning:
        wheel_angle += spin_speed
        spin_speed *= FRICTION

        if abs(spin_speed) < STOP_THRESHOLD:
            # stop and snap to nearest sector
            spinning = False
            # snap wheel_angle to exact multiple of sector angle
            k = round(wheel_angle / SECTOR_ANGLE)
            wheel_angle = k * SECTOR_ANGLE
            idx = pointer_index_from_angle(wheel_angle)
            last_result = evaluate_spin(idx)

    # ----- Draw -----
    screen.fill((10, 12, 18))

    # Title
    title = FONT_BIG.render("Roulette", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 40)))

    # Wheel and pointer
    draw_wheel(screen, wheel_center, WHEEL_RADIUS, wheel_angle)
    draw_pointer(screen, wheel_center, WHEEL_RADIUS)

    # Info & messages
    bal_txt = FONT_MEDIUM.render(f"Balance: ₹{balance}", True, (230, 230, 230))
    screen.blit(bal_txt, (40, 520))

    bet_txt = FONT_MEDIUM.render(f"Bet: ₹{bet_amount}", True, (230, 230, 230))
    screen.blit(bet_txt, (40, 550))

    if bet_type == "color":
        info = f"Betting on COLOR: {bet_target_color.upper()}"
    else:
        info = f"Betting on NUMBER: {bet_target_number}"
    info_txt = FONT_MEDIUM.render(info, True, (230, 230, 230))
    screen.blit(info_txt, (360, 560))

    y_msg = 430
    if last_result:
        last_line = f"Last: {last_result['number']} ({last_result['color'].upper()})  " \
                    f"{'WIN' if last_result['win'] else 'LOSE'}  Δ₹{last_result['delta']}"
        last_txt = FONT_MEDIUM.render(last_line, True, (200, 200, 200))
        screen.blit(last_txt, (40, y_msg))
        y_msg += 26

    msg_txt = FONT_MEDIUM.render(message, True, (200, 200, 200))
    screen.blit(msg_txt, (40, y_msg))

    # Buttons
    for b in [btn_dec_bet, btn_inc_bet,
              btn_red, btn_black, btn_green,
              btn_num_mode, btn_dec_num, btn_inc_num,
              btn_spin]:
        b.draw(screen)

    # Show current pointer number (for debugging / info)
    idx_now = pointer_index_from_angle(wheel_angle)
    num_now = WHEEL_NUMBERS[idx_now]
    ptr_txt = FONT_SMALL.render(f"Pointer: {num_now}", True, (230, 230, 230))
    screen.blit(ptr_txt, (WIDTH - 160, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
