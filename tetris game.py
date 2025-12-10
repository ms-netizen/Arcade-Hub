import pygame
from copy import deepcopy
from random import choice, randrange

W, H = 10, 15
TILE = 30
GAME_RES = W * TILE, H * TILE
RES = 600, 540
FPS = 70

pygame.init() #initiates pygame
sc = pygame.display.set_mode(RES)  #creates pygame window
game_sc = pygame.Surface(GAME_RES)
clock = pygame.time.Clock() #creates clock object

#clockobject- controls framerate

grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

#this defines class rect (rectangular space) and used to define positions of the object

figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)], #each inner list= tetris figure
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]

#coordinates for the random tetris blocks

figures = [[pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]
figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
field = [[0 for i in range(W)] for j in range(H)] #game grid, tracks occupied positions


anim_count, anim_speed, anim_limit = 0, 60, 2000

bg = pygame.image.load(r"c:\Users\matha\Downloads\project\project\pic1.jpeg").convert()
game_bg = pygame.image.load(r"c:\Users\matha\Downloads\project\project\pic2.jpg").convert()
#loads background image- inner and outer bg

main_font = pygame.font.Font(r"c:\Users\matha\Downloads\project\project\font1.otf", 65)
font = pygame.font.Font(r"c:\Users\matha\Downloads\project\project\font2.otf", 45)
#loads font from folder

title_tetris = main_font.render('TETRIS', True, pygame.Color('gray'))
title_score = font.render('score:', True, pygame.Color('beige'))
title_record = font.render('record:', True, pygame.Color('white'))
#colours of the text

get_color = lambda : (randrange(30, 256), randrange(30, 256), randrange(30, 256))
#creates random colour for the tetris blocks

figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()
#next_figure respresents the next tetris piece and keeps it ready
#deepcopy copies the format of the tetris pieces

score, lines = 0, 0

scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}
#defines score value for clearing the line

def check_borders():
    if figure[i].x < 0 or figure[i].x > W - 1:
        #0,W-1 represents range for the inner grid
        return False
    elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True
#checks if figure is within game border


def get_record():
    try:
        with open('record') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record', 'w') as f:
            f.write('0')
#the above function tracks the record value


def set_record(record, score):
    rec = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(rec))
#above function sets the record in a file
        

while True: #main game loop
    record = get_record()#gets the current record
    dx, rotate = 0, False
    sc.blit(bg, (0, 0))#joins(blits)
    sc.blit(game_sc, (20, 20))
    game_sc.blit(game_bg, (0, 0))
    #draws bg images
    
    # delay for full lines
    for i in range(lines):
        pygame.time.wait(200)
        
    # control
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                anim_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True
    # move horizontally
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break
    # move vertically
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if not check_borders():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                anim_limit = 2000
                break
            
    # rotate the piece
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
            if not check_borders():
                figure = deepcopy(figure_old)
                break
    # checks for completed lines
    line, lines = H - 1, 0
    for row in range(H - 1, -1, -1):
        count = 0
        for i in range(W):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < W:
            line -= 1
        else:
            anim_speed += 3
            lines += 1
    # increments score
    score += scores[lines]
    # draw grid
    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]
    # draw figure
    for i in range(4):
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        pygame.draw.rect(game_sc, color, figure_rect)
    # draw field
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figure_rect)
    # draw next figure
    for i in range(4):
        figure_rect.x = next_figure[i].x * TILE + 380
        figure_rect.y = next_figure[i].y * TILE + 185
        pygame.draw.rect(sc, next_color, figure_rect)
    # draw titles
    sc.blit(title_tetris, (350, -10))
    sc.blit(title_score, (300, 600))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (400, 700))
    sc.blit(title_record, (350, 420))
    sc.blit(font.render(record, True, pygame.Color('gold')), (350, 450))
    # game over
    for i in range(W):
        if field[0][i]:
            set_record(record, score)
            field = [[0 for i in range(W)] for i in range(H)]
            anim_count, anim_speed, anim_limit = 0, 60, 2000
            score = 0
            for i_rect in grid:
                pygame.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (20, 20))
                pygame.display.flip()
                clock.tick(200)

    pygame.display.flip()
    clock.tick(FPS)      