
import pygame
import heapq
import random
import math
import sys

# ============================================================
# AI TREASURE HUNT
# Classical AI Game
# No Machine Learning
# ============================================================

pygame.init()

# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

CELL = 40
COLS = 20
ROWS = 15
HUD_HEIGHT = 70

WIDTH = COLS * CELL
HEIGHT = HUD_HEIGHT + ROWS * CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Treasure Hunt - A* Artificial Intelligence")

clock = pygame.time.Clock()

# ------------------------------------------------------------
# COLORS
# ------------------------------------------------------------

BLACK = (10, 12, 20)
WHITE = (245, 245, 245)
GRAY = (80, 85, 100)
DARK_GRAY = (30, 34, 45)

BLUE = (50, 150, 255)
LIGHT_BLUE = (120, 210, 255)

RED = (235, 60, 70)
LIGHT_RED = (255, 110, 110)

GOLD = (255, 210, 50)
YELLOW = (255, 240, 100)

GREEN = (60, 220, 120)
DARK_GREEN = (30, 130, 70)

PURPLE = (180, 90, 255)
CYAN = (60, 230, 240)

ORANGE = (255, 150, 50)

# ------------------------------------------------------------
# FONTS
# ------------------------------------------------------------

font_small = pygame.font.Font(None, 24)
font = pygame.font.Font(None, 30)
font_big = pygame.font.Font(None, 50)
font_title = pygame.font.Font(None, 72)

# ------------------------------------------------------------
# MAP
# 0 = open
# 1 = wall
# ------------------------------------------------------------

MAP = [
    "00000000000000000000",
    "00111100001111000000",
    "00000000000000000000",
    "00000111100001111000",
    "00000000000000000000",
    "00111100001111000000",
    "00000000000000000000",
    "00001111000011110000",
    "00000000000000000000",
    "00111100001111000000",
    "00000000000000000000",
    "00000111100001111000",
    "00000000000000000000",
    "00111100001111000000",
    "00000000000000000000",
]

# ------------------------------------------------------------
# GAME VARIABLES
# ------------------------------------------------------------

MAX_LEVEL = 5

level = 1
score = 0
lives = 3
high_score = 0

game_time = 60
level_time = 60

player_pos = (1, 0)
ai_pos = (18, 14)

treasures = []

particles = []

game_state = "menu"

show_path = True

ai_move_timer = 0
ai_recalculate_timer = 0

safe_timer = 0
speed_boost_timer = 0
shield_timer = 0

combo = 0
combo_timer = 0

level_message_timer = 0

total_treasures_collected = 0
total_ai_moves = 0
total_path_calculations = 0

# ------------------------------------------------------------
# AI DIFFICULTY
# ------------------------------------------------------------

AI_SETTINGS = {
    1: {
        "delay": 0.65,
        "detection": 8,
        "color": RED,
    },
    2: {
        "delay": 0.55,
        "detection": 10,
        "color": RED,
    },
    3: {
        "delay": 0.45,
        "detection": 12,
        "color": ORANGE,
    },
    4: {
        "delay": 0.35,
        "detection": 15,
        "color": ORANGE,
    },
    5: {
        "delay": 0.25,
        "detection": 20,
        "color": PURPLE,
    },
}

# ------------------------------------------------------------
# SOUND EFFECTS
# ------------------------------------------------------------

sound_available = False

try:
    pygame.mixer.init()

    def make_sound(frequency, duration=0.08):
        sample_rate = 44100
        samples = int(sample_rate * duration)

        buffer = bytearray()

        for i in range(samples):
            value = int(
                127
                * math.sin(
                    2 * math.pi * frequency * i / sample_rate
                )
            )

            buffer.append(value + 128)

        return pygame.mixer.Sound(buffer=bytes(buffer))

    sound_collect = make_sound(800, 0.08)
    sound_hit = make_sound(180, 0.15)
    sound_level = make_sound(1000, 0.18)
    sound_win = make_sound(1400, 0.3)

    sound_available = True

except Exception:
    sound_available = False


def play_sound(sound):
    if sound_available:
        try:
            sound.play()
        except Exception:
            pass


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def is_walkable(pos):
    x, y = pos

    if x < 0 or x >= COLS:
        return False

    if y < 0 or y >= ROWS:
        return False

    return MAP[y][x] == "0"


def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def cell_rect(pos, padding=4):
    x, y = pos

    return pygame.Rect(
        x * CELL + padding,
        HUD_HEIGHT + y * CELL + padding,
        CELL - padding * 2,
        CELL - padding * 2,
    )


def draw_text(text, font_obj, color, x, y, center=False):
    surface = font_obj.render(text, True, color)

    if center:
        rect = surface.get_rect(center=(x, y))
    else:
        rect = surface.get_rect(topleft=(x, y))

    screen.blit(surface, rect)


# ------------------------------------------------------------
# A* PATHFINDING
# ------------------------------------------------------------

def get_neighbors(pos):
    x, y = pos

    possible = [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),
    ]

    return [p for p in possible if is_walkable(p)]


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(start, goal):
    global total_path_calculations

    total_path_calculations += 1

    open_set = []

    heapq.heappush(
        open_set,
        (0, start)
    )

    came_from = {}

    g_score = {
        start: 0
    }

    f_score = {
        start: heuristic(start, goal)
    }

    while open_set:

        _, current = heapq.heappop(open_set)

        if current == goal:

            path = []

            while current in came_from:
                path.append(current)
                current = came_from[current]

            path.append(start)

            path.reverse()

            return path

        for neighbor in get_neighbors(current):

            tentative_g = g_score[current] + 1

            if (
                neighbor not in g_score
                or tentative_g < g_score[neighbor]
            ):

                came_from[neighbor] = current

                g_score[neighbor] = tentative_g

                f = tentative_g + heuristic(
                    neighbor,
                    goal
                )

                f_score[neighbor] = f

                heapq.heappush(
                    open_set,
                    (f, neighbor)
                )

    return []


# ------------------------------------------------------------
# TREASURE SYSTEM
# ------------------------------------------------------------

TREASURE_VALUES = [
    10,
    15,
    20,
    25,
    30,
    40,
]

TREASURE_CANDIDATES = [
    (4, 0),
    (8, 2),
    (15, 2),
    (2, 4),
    (10, 4),
    (18, 6),
    (6, 6),
    (13, 8),
    (3, 8),
    (17, 10),
    (8, 10),
    (1, 12),
    (11, 12),
    (18, 14),
]


def spawn_treasures():
    global treasures

    valid = []

    for pos in TREASURE_CANDIDATES:

        if not is_walkable(pos):
            continue

        if pos == player_pos:
            continue

        if pos == ai_pos:
            continue

        valid.append(pos)

    random.shuffle(valid)

    count = min(4 + level, len(valid))

    treasures = []

    for i in range(count):

        treasures.append(
            {
                "pos": valid[i],
                "value": TREASURE_VALUES[
                    min(i, len(TREASURE_VALUES) - 1)
                ],
                "type": "gold",
            }
        )

    # Add special treasure at higher levels

    if level >= 3 and len(valid) > count:

        special_pos = valid[count]

        treasures.append(
            {
                "pos": special_pos,
                "value": 75,
                "type": "diamond",
            }
        )


# ------------------------------------------------------------
# PARTICLES
# ------------------------------------------------------------

def create_particles(pos, color, amount=12):

    x = pos[0] * CELL + CELL // 2

    y = HUD_HEIGHT + pos[1] * CELL + CELL // 2

    for _ in range(amount):

        particles.append(
            {
                "x": x,
                "y": y,
                "vx": random.uniform(-2.5, 2.5),
                "vy": random.uniform(-2.5, 2.5),
                "life": random.uniform(0.4, 0.9),
                "color": color,
            }
        )


def update_particles(dt):

    for particle in particles[:]:

        particle["x"] += particle["vx"]

        particle["y"] += particle["vy"]

        particle["life"] -= dt

        if particle["life"] <= 0:
            particles.remove(particle)


def draw_particles():

    for particle in particles:

        radius = max(
            1,
            int(4 * particle["life"])
        )

        pygame.draw.circle(
            screen,
            particle["color"],
            (
                int(particle["x"]),
                int(particle["y"]),
            ),
            radius,
        )


# ------------------------------------------------------------
# PLAYER
# ------------------------------------------------------------

def reset_positions():

    global player_pos
    global ai_pos

    player_pos = (1, 0)

    ai_pos = (18, 14)


def move_player(dx, dy):

    global player_pos

    new_pos = (
        player_pos[0] + dx,
        player_pos[1] + dy,
    )

    if is_walkable(new_pos):

        player_pos = new_pos

        create_particles(
            player_pos,
            LIGHT_BLUE,
            3
        )

        check_treasure()

        check_collision()


# ------------------------------------------------------------
# TREASURE COLLECTION
# ------------------------------------------------------------

def check_treasure():

    global score
    global combo
    global combo_timer
    global total_treasures_collected

    for treasure in treasures[:]:

        if treasure["pos"] == player_pos:

            value = treasure["value"]

            combo += 1

            combo_timer = 3

            bonus = combo * 5

            score += value + bonus

            total_treasures_collected += 1

            high_score_update()

            create_particles(
                player_pos,
                GOLD,
                20
            )

            play_sound(sound_collect)

            treasures.remove(treasure)


# ------------------------------------------------------------
# SCORE
# ------------------------------------------------------------

def high_score_update():

    global high_score

    if score > high_score:

        high_score = score


# ------------------------------------------------------------
# COLLISION
# ------------------------------------------------------------

def check_collision():

    global lives
    global score
    global safe_timer

    if safe_timer > 0:
        return

    if player_pos == ai_pos:

        if shield_timer > 0:

            create_particles(
                player_pos,
                CYAN,
                25
            )

            safe_timer = 1.5

            return

        lives -= 1

        score = max(
            0,
            score - 20
        )

        create_particles(
            player_pos,
            RED,
            30
        )

        play_sound(sound_hit)

        safe_timer = 2

        reset_positions()

        if lives <= 0:

            end_game()


# ------------------------------------------------------------
# AI
# ------------------------------------------------------------

def move_ai(path):

    global ai_pos
    global total_ai_moves

    if not path:
        return

    if len(path) < 2:
        return

    next_pos = path[1]

    if is_walkable(next_pos):

        ai_pos = next_pos

        total_ai_moves += 1

        check_collision()


# ------------------------------------------------------------
# GAME SETUP
# ------------------------------------------------------------

def setup_level():

    global level_time
    global game_time
    global ai_move_timer
    global ai_recalculate_timer
    global safe_timer
    global speed_boost_timer
    global shield_timer
    global combo
    global combo_timer

    reset_positions()

    level_time = 60 - (level - 1) * 5

    game_time = level_time

    ai_move_timer = 0

    ai_recalculate_timer = 0

    safe_timer = 1.5

    speed_boost_timer = 0

    shield_timer = 0

    combo = 0

    combo_timer = 0

    spawn_treasures()


def start_game():

    global level
    global score
    global lives
    global total_treasures_collected
    global total_ai_moves
    global total_path_calculations
    global game_state

    level = 1

    score = 0

    lives = 3

    total_treasures_collected = 0

    total_ai_moves = 0

    total_path_calculations = 0

    particles.clear()

    setup_level()

    game_state = "playing"


def next_level():

    global level
    global game_state
    global level_message_timer

    if level >= MAX_LEVEL:

        game_state = "won"

        play_sound(sound_win)

        return

    level += 1

    setup_level()

    level_message_timer = 2

    play_sound(sound_level)


def end_game():

    global game_state

    game_state = "gameover"


# ------------------------------------------------------------
# DRAW MAP
# ------------------------------------------------------------

def draw_map():

    for y in range(ROWS):

        for x in range(COLS):

            rect = cell_rect(
                (x, y),
                1
            )

            if MAP[y][x] == "1":

                pygame.draw.rect(
                    screen,
                    DARK_GRAY,
                    rect,
                    border_radius=6
                )

                pygame.draw.rect(
                    screen,
                    GRAY,
                    rect,
                    2,
                    border_radius=6
                )

            else:

                pygame.draw.rect(
                    screen,
                    (18, 22, 32),
                    rect
                )

                pygame.draw.rect(
                    screen,
                    (28, 33, 45),
                    rect,
                    1
                )


# ------------------------------------------------------------
# DRAW PLAYER
# ------------------------------------------------------------

def draw_player():

    rect = cell_rect(
        player_pos,
        6
    )

    # blinking when protected

    if safe_timer > 0:

        if int(
            pygame.time.get_ticks() / 100
        ) % 2 == 0:

            return

    pygame.draw.rect(
        screen,
        BLUE,
        rect,
        border_radius=10
    )

    # speed boost effect

    if speed_boost_timer > 0:

        pygame.draw.circle(
            screen,
            CYAN,
            rect.center,
            CELL // 2 - 2,
            2
        )

    # shield

    if shield_timer > 0:

        pygame.draw.circle(
            screen,
            CYAN,
            rect.center,
            CELL // 2,
            3
        )

    # eyes

    eye_y = rect.y + 11

    pygame.draw.circle(
        screen,
        WHITE,
        (rect.x + 12, eye_y),
        4
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (rect.x + 25, eye_y),
        4
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (rect.x + 12, eye_y),
        2
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (rect.x + 25, eye_y),
        2
    )


# ------------------------------------------------------------
# DRAW AI
# ------------------------------------------------------------

def draw_ai():

    settings = AI_SETTINGS[level]

    rect = cell_rect(
        ai_pos,
        6
    )

    center = rect.center

    pulse = int(
        3 * math.sin(
            pygame.time.get_ticks() / 150
        )
    )

    pygame.draw.circle(
        screen,
        settings["color"],
        center,
        CELL // 2 - 7 + pulse
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (center[0] - 7, center[1] - 5),
        4
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (center[0] + 7, center[1] - 5),
        4
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (center[0] - 7, center[1] - 5),
        2
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (center[0] + 7, center[1] - 5),
        2
    )


# ------------------------------------------------------------
# DRAW TREASURES
# ------------------------------------------------------------

def draw_treasures():

    pulse = math.sin(
        pygame.time.get_ticks() / 180
    )

    for treasure in treasures:

        x, y = treasure["pos"]

        cx = x * CELL + CELL // 2

        cy = HUD_HEIGHT + y * CELL + CELL // 2

        size = int(
            9 + pulse * 2
        )

        if treasure["type"] == "diamond":

            points = [
                (cx, cy - size - 3),
                (cx + size, cy),
                (cx, cy + size + 3),
                (cx - size, cy),
            ]

            pygame.draw.polygon(
                screen,
                PURPLE,
                points
            )

            pygame.draw.polygon(
                screen,
                WHITE,
                points,
                2
            )

        else:

            pygame.draw.circle(
                screen,
                GOLD,
                (cx, cy),
                size
            )

            pygame.draw.circle(
                screen,
                YELLOW,
                (cx, cy),
                size - 3
            )


# ------------------------------------------------------------
# DRAW A* PATH
# ------------------------------------------------------------

def draw_path(path):

    if not show_path:
        return

    if not path:
        return

    for pos in path:

        x = pos[0] * CELL + CELL // 2

        y = HUD_HEIGHT + pos[1] * CELL + CELL // 2

        pygame.draw.circle(
            screen,
            (40, 120, 150),
            (x, y),
            3
        )


# ------------------------------------------------------------
# HUD
# ------------------------------------------------------------

def draw_hud():

    pygame.draw.rect(
        screen,
        (15, 18, 28),
        (0, 0, WIDTH, HUD_HEIGHT)
    )

    pygame.draw.line(
        screen,
        CYAN,
        (0, HUD_HEIGHT - 1),
        (WIDTH, HUD_HEIGHT - 1),
        2
    )

    draw_text(
        f"SCORE: {score}",
        font_small,
        WHITE,
        15,
        8
    )

    draw_text(
        f"HIGH: {high_score}",
        font_small,
        GOLD,
        15,
        38
    )

    draw_text(
        f"LIVES: {'❤️' * lives}",
        font_small,
        WHITE,
        150,
        8
    )

    draw_text(
        f"LEVEL: {level}/{MAX_LEVEL}",
        font_small,
        GREEN,
        150,
        38
    )

    timer_color = (
        RED
        if game_time < 10
        else WHITE
    )

    draw_text(
        f"TIME: {int(max(0, game_time))}",
        font_small,
        timer_color,
        300,
        8
    )

    draw_text(
        f"TREASURE: {len(treasures)}",
        font_small,
        GOLD,
        300,
        38
    )

    ai_name = [
        "EASY",
        "NORMAL",
        "FAST",
        "HARD",
        "EXPERT",
    ][level - 1]

    draw_text(
        f"AI: {ai_name}",
        font_small,
        RED,
        455,
        8
    )

    draw_text(
        f"A* PATH: {'ON' if show_path else 'OFF'}",
        font_small,
        CYAN,
        455,
        38
    )

    if shield_timer > 0:

        draw_text(
            f"SHIELD: {shield_timer:.1f}",
            font_small,
            CYAN,
            620,
            8
        )

    if speed_boost_timer > 0:

        draw_text(
            f"SPEED: {speed_boost_timer:.1f}",
            font_small,
            ORANGE,
            620,
            38
        )


# ------------------------------------------------------------
# START MENU
# ------------------------------------------------------------

def draw_menu():

    screen.fill(BLACK)

    # animated background stars

    for i in range(40):

        x = (i * 97) % WIDTH

        y = (
            i * 53
            + int(
                pygame.time.get_ticks() / 30
            )
        ) % HEIGHT

        pygame.draw.circle(
            screen,
            (40, 55, 80),
            (x, y),
            2
        )

    draw_text(
        "AI TREASURE HUNT",
        font_title,
        CYAN,
        WIDTH // 2,
        90,
        True
    )

    draw_text(
        "CLASSICAL ARTIFICIAL INTELLIGENCE",
        font,
        WHITE,
        WIDTH // 2,
        145,
        True
    )

    draw_text(
        "A* PATHFINDING • DECISION MAKING • SEARCH",
        font_small,
        GREEN,
        WIDTH // 2,
        180,
        True
    )

    # Game rules box

    box = pygame.Rect(
        180,
        215,
        WIDTH - 360,
        250
    )

    pygame.draw.rect(
        screen,
        (20, 25, 40),
        box,
        border_radius=15
    )

    pygame.draw.rect(
        screen,
        CYAN,
        box,
        2,
        border_radius=15
    )

    draw_text(
        "HOW TO PLAY",
        font_big,
        GOLD,
        WIDTH // 2,
        245,
        True
    )

    instructions = [
        "Arrow Keys  - Move your player",
        "Collect treasures to increase your score",
        "Avoid the red AI enemy",
        "The AI uses A* shortest-path search",
        "P - Pause     H - Show/Hide AI path",
        "R - Restart",
    ]

    y = 290

    for text in instructions:

        draw_text(
            text,
            font_small,
            WHITE,
            WIDTH // 2,
            y,
            True
        )

        y += 28

    draw_text(
        "PRESS ENTER TO START",
        font_big,
        GREEN,
        WIDTH // 2,
        510,
        True
    )

    draw_text(
        "No Machine Learning Used",
        font_small,
        GRAY,
        WIDTH // 2,
        550,
        True
    )


# ------------------------------------------------------------
# PAUSE
# ------------------------------------------------------------

def draw_pause():

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 180)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    draw_text(
        "PAUSED",
        font_title,
        YELLOW,
        WIDTH // 2,
        HEIGHT // 2 - 50,
        True
    )

    draw_text(
        "Press P to Continue",
        font,
        WHITE,
        WIDTH // 2,
        HEIGHT // 2 + 25,
        True
    )


# ------------------------------------------------------------
# END SCREEN
# ------------------------------------------------------------

def draw_end_screen(won):

    screen.fill(BLACK)

    if won:

        title = "🏆 YOU WIN!"

        color = GOLD

        message = (
            "You completed all AI Treasure Hunt levels!"
        )

    else:

        title = "GAME OVER"

        color = RED

        message = (
            "The AI caught you too many times."
        )

    draw_text(
        title,
        font_title,
        color,
        WIDTH // 2,
        100,
        True
    )

    draw_text(
        message,
        font,
        WHITE,
        WIDTH // 2,
        165,
        True
    )

    # Statistics box

    box = pygame.Rect(
        220,
        220,
        WIDTH - 440,
        240
    )

    pygame.draw.rect(
        screen,
        (20, 25, 40),
        box,
        border_radius=15
    )

    pygame.draw.rect(
        screen,
        color,
        box,
        2,
        border_radius=15
    )

    stats = [
        f"Final Score: {score}",
        f"High Score: {high_score}",
        f"Level Reached: {level}",
        f"Treasures Collected: {total_treasures_collected}",
        f"AI Moves: {total_ai_moves}",
        f"A* Searches: {total_path_calculations}",
    ]

    y = 250

    for item in stats:

        draw_text(
            item,
            font,
            WHITE,
            WIDTH // 2,
            y,
            True
        )

        y += 32

    draw_text(
        "Press R to Restart",
        font_big,
        GREEN,
        WIDTH // 2,
        500,
        True
    )

    draw_text(
        "Press ESC for Menu",
        font,
        GRAY,
        WIDTH // 2,
        550,
        True
    )


# ------------------------------------------------------------
# LEVEL COMPLETE MESSAGE
# ------------------------------------------------------------

def draw_level_message():

    if level_message_timer <= 0:
        return

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 100)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    draw_text(
        f"LEVEL {level}",
        font_title,
        GOLD,
        WIDTH // 2,
        HEIGHT // 2 - 40,
        True
    )

    draw_text(
        "AI DIFFICULTY INCREASED!",
        font_big,
        RED,
        WIDTH // 2,
        HEIGHT // 2 + 30,
        True
    )


# ------------------------------------------------------------
# GAME DRAW
# ------------------------------------------------------------

def draw_game(path):

    screen.fill(BLACK)

    draw_hud()

    draw_map()

    draw_path(path)

    draw_treasures()

    draw_player()

    draw_ai()

    draw_particles()

    draw_level_message()


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

running = True

while running:

    dt = clock.tick(60) / 1000.0

    # ----------------------------------------
    # EVENTS
    # ----------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            # MENU

            if game_state == "menu":

                if event.key == pygame.K_RETURN:

                    start_game()

                elif event.key == pygame.K_ESCAPE:

                    running = False

            # PLAYING

            elif game_state == "playing":

                if event.key == pygame.K_UP:

                    move_player(0, -1)

                elif event.key == pygame.K_DOWN:

                    move_player(0, 1)

                elif event.key == pygame.K_LEFT:

                    move_player(-1, 0)

                elif event.key == pygame.K_RIGHT:

                    move_player(1, 0)

                elif event.key == pygame.K_p:

                    game_state = "paused"

                elif event.key == pygame.K_h:

                    show_path = not show_path

                elif event.key == pygame.K_r:

                    start_game()

                elif event.key == pygame.K_ESCAPE:

                    game_state = "menu"

            # PAUSED

            elif game_state == "paused":

                if event.key == pygame.K_p:

                    game_state = "playing"

                elif event.key == pygame.K_r:

                    start_game()

                elif event.key == pygame.K_ESCAPE:

                    game_state = "menu"

            # END STATES

            elif (
                game_state == "gameover"
                or game_state == "won"
            ):

                if event.key == pygame.K_r:

                    start_game()

                elif event.key == pygame.K_ESCAPE:

                    game_state = "menu"

    # ----------------------------------------
    # PLAYING LOGIC
    # ----------------------------------------

    if game_state == "playing":

        # Timer

        game_time -= dt

        # Protection timers

        if safe_timer > 0:

            safe_timer -= dt

        if speed_boost_timer > 0:

            speed_boost_timer -= dt

        if shield_timer > 0:

            shield_timer -= dt

        if combo_timer > 0:

            combo_timer -= dt

        else:

            combo = 0

        if level_message_timer > 0:

            level_message_timer -= dt

        # Timer reaches zero

        if game_time <= 0:

            lives -= 1

            create_particles(
                player_pos,
                RED,
                25
            )

            play_sound(sound_hit)

            if lives <= 0:

                end_game()

            else:

                setup_level()

        # ------------------------------------
        # AI PATH
        # ------------------------------------

        path = a_star(
            ai_pos,
            player_pos
        )

        # AI only chases when player is in range

        settings = AI_SETTINGS[level]

        player_distance = distance(
            ai_pos,
            player_pos
        )

        ai_recalculate_timer += dt

        if (
            player_distance
            <= settings["detection"]
        ):

            ai_move_timer += dt

            ai_delay = settings["delay"]

            # Speed boost makes player harder to catch

            if speed_boost_timer > 0:

                ai_delay *= 1.25

            if ai_move_timer >= ai_delay:

                ai_move_timer = 0

                move_ai(path)

        else:

            # AI waits when player is outside detection range

            ai_move_timer = 0

        # Check collision

        check_collision()

        # All treasures collected

        if len(treasures) == 0:

            next_level()

    else:

        path = []

    # ----------------------------------------
    # PARTICLES
    # ----------------------------------------

    update_particles(dt)

    # ----------------------------------------
    # DRAW
    # ----------------------------------------

    if game_state == "menu":

        draw_menu()

    elif game_state == "playing":

        draw_game(path)

    elif game_state == "paused":

        draw_game(path)

        draw_pause()

    elif game_state == "gameover":

        draw_end_screen(False)

    elif game_state == "won":

        draw_end_screen(True)

    pygame.display.flip()


pygame.quit()
sys.exit()