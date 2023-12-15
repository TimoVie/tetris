import sys

import pygame
import random

"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""

pygame.font.init()

# GLOBALS VARS
s_width = 880
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per blo ck
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height


# SHAPE FORMATS

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 represent shape


class Piece(object):
    rows = 20  # y
    columns = 10  # x

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # number from 0-3


def create_grid(locked_positions={}):
    grid = [[(0,0,0) for x in range(10)] for x in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j,i) in locked_positions:
                c = locked_positions[(j,i)]
                grid[i][j] = c
    return grid

def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False

    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape():
    global shapes, shape_colors

    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('couriernew', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2))


def draw_grid(surface, row, col):
    sx = top_left_x
    sy = top_left_y
    for i in range(row):
        pygame.draw.line(surface, (128,128,128), (sx, sy+ i*30), (sx + play_width, sy + i * 30))  # horizontal lines
        for j in range(col):
            pygame.draw.line(surface, (128,128,128), (sx + j * 30, sy), (sx + j * 30, sy + play_height))  # vertical lines


def clear_rows(grid, locked):
    # need to see if row is clear the shift every other row above down one
    rows_to_clear = []

    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            rows_to_clear.append(i)
            # add positions to remove from locked
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue

    if rows_to_clear:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < min(rows_to_clear):
                new_key = (x, y + len(rows_to_clear))
                locked[new_key] = locked.pop(key)

    return len(rows_to_clear)


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('couriernew', 30)
    label = font.render('Nächstes Form:', 100 , (0,0,0))

    sx = top_left_x + play_width + 10
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]


    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*30 +50, sy + i*30, 30, 30), 0)

    surface.blit(label, (sx + 15, sy - 70))


def draw_window(surface):
    surface.fill((255,255,255))

    # Load the Tetris logo image
    logo = pygame.image.load('logo_ba.png')  # Replace 'logo.png' with the actual filename of your logo image
    logo = pygame.transform.scale(logo, (240, 80))  # Adjust the size of the logo as needed


    # Tetris Title
    font = pygame.font.SysFont('couriernew', 60)
    label = font.render('TETRIS', 1, (0,0,0))

    # Adjust the padding values as needed
    padding_x = 20
    padding_y = 10

    # Blit the logo and title
    surface.blit(logo, (top_left_x - padding_x - logo.get_width(), padding_y - 10))
    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2) - padding_x + 20,
                         50 - padding_y))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j* 30, top_left_y + i * 30, 30, 30), 0)

    # draw grid and border
    draw_grid(surface, 20, 10)
    pygame.draw.rect(surface, (189, 199, 192), (top_left_x, top_left_y, play_width, play_height), 5)
    # pygame.display.update()



def draw_score(surface, score):
    font = pygame.font.SysFont('couriernew', 30)
    label = font.render('Score: ' + str(score), 1, (0,0,0))

    sx = top_left_x - 220
    sy = top_left_y + 200 - 70

    surface.blit(label, (sx, sy))

def draw_instruction(surface):
    font = pygame.font.SysFont('couriernew', 15)
    label1 = font.render('p -> pause', 1, (0,0,0))
    label2 = font.render('q -> Spiel schließen', 1, (0,0,0))
    label3 = font.render('n -> Neues Spiel starten', 1, (0,0,0))

    sx = top_left_x - 260
    sy = top_left_y + 500

    surface.blit(label1, (sx, sy))
    surface.blit(label2, (sx, sy + 30))
    surface.blit(label3, (sx, sy + 60))

def main():
    global grid

    locked_positions = {}  # (x,y):(255,0,0)
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    level_time = 0
    fall_speed = 0.27
    score = 0

    while run:

        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time/1000 > 4:
            level_time = 0
            if fall_speed > 0.15:
                fall_speed -= 0.005
            

        # PIECE FALLING CODE
        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_UP:
                    # rotate shape
                    current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)

                if event.key == pygame.K_DOWN:
                    # move shape down
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1

                '''if event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    print(convert_shape_format(current_piece))'''  # todo fix

                if event.key == pygame.K_p:
                    # Toggle pause state
                    pause_menu()
                elif event.key == pygame.K_n:
                    main()

        shape_pos = convert_shape_format(current_piece)

        # add piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        # IF PIECE HIT GROUND
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # call four times to check for multiple clear rows
            rows_cleared = clear_rows(grid, locked_positions)
            if rows_cleared > 0:
                score += rows_cleared * 1

        draw_window(win)
        draw_next_shape(next_piece, win)
        draw_score(win, score)  # Zeige den Punktestand an
        draw_instruction(win)  # Zeige die Instruction an
        pygame.display.update()

        # Check if user lost
        if check_lost(locked_positions):
            run = False

    draw_text_middle("You Lost", 40, (255,255,255), win)
    draw_score(win, score)  # Zeige den Endpunktestand an
    pygame.display.update()
    pygame.time.delay(2000)


def main_menu():
    run = True

    while run:
        win.fill((255, 255, 255))

        # Load and display the Tetris logo image above the text
        logo = pygame.image.load('logo_ba.png')  # Replace with the actual filename of your logo
        logo = pygame.transform.scale(logo, (400, 150))  # Adjust the size of the logo as needed
        win.blit(logo, (top_left_x + play_width / 2 - logo.get_width() / 2, 100))

        draw_text_middle('Drücke eine beliebige Taste, um zu beginnen...', 25, (0, 63, 115), win)


        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()

def pause_menu():
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    # Resume the game
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()



        win.fill((0, 0, 0))
        draw_text_middle('Paused', 60, (255, 255, 255), win)
        pygame.display.update()


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris Game')

main_menu()  # start game






