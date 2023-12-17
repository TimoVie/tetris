import sys
import pickle
import pygame
import random

from pygame import mixer


"""
10 x 20 Grid
Formen / Blöcke: O, I, S, Z, L, J, T
"""

pygame.font.init()

# Globale Variablen
lautstärke = 0.01
screen_breite = 600
screen_höhe = screen_breite
spiel_breite = screen_breite / 2  # meaning 300 // 10 = 30 width per block
spiel_höhe = screen_breite  # meaning 600 // 20 = 20 height per blo ck
block_größe = spiel_höhe / 20

oben_links_x = screen_breite - spiel_breite
oben_links_y = screen_höhe - spiel_höhe


# Tetrominos

O = [
  ['-', '-', '-', '-', '-'],
  ['-', '-', '-', '-', '-'],
  ['-', 'X', 'X', '-', '-'],
  ['-', 'X', 'X', '-', '-'],
  ['-', '-', '-', '-', '-']
]

I = [
  ['-', '-', 'X', '-', '-'],
  ['-', '-', 'X', '-', '-'],
  ['-', '-', 'X', '-', '-'],
  ['-', '-', 'X', '-', '-'],
  ['-', '-', '-', '-', '-']
]

S = [
  ['-', '-', '-', '-', '-'],
  ['-', '-', '-', '-', '-'],
  ['-', '-', 'X', 'X', '-'],
  ['-', 'X', 'X', '-', '-'],
  ['-', '-', '-', '-', '-']
]

Z = [
  ['-', '-', '-', '-', '-'],
  ['-', '-', '-', '-', '-'],
  ['-', 'X', 'X', '-', '-'],
  ['-', '-', 'X', 'X', '-'],
  ['-', '-', '-', '-', '-']
]

L = [
  ['-', '-', '-', '-', '-'],
  ['-', '-', '-', 'X', '-'],
  ['-', 'X', 'X', 'X', '-'],
  ['-', '-', '-', '-', '-'],
  ['-', '-', '-', '-', '-']
]

J = [
  ['-', '-', '-', '-', '-'],
  ['-', 'X', '-', '-', '-'],
  ['-', 'X', 'X', 'X', '-'],
  ['-', '-', '-', '-', '-'],
  ['-', '-', '-', '-', '-']
]

T = [
  ['-', '-', '-', '-', '-'],
  ['-', '-', 'X', '-', '-'],
  ['-', 'X', 'X', 'X', '-'],
  ['-', '-', '-', '-', '-'],
  ['-', '-', '-', '-', '-']
]

tetrominos = [O, I, S, Z, L, J, T]
tetromino_farben = [(0, 110, 176), (255, 125, 0), (255, 201, 0), (48, 3, 156), (128, 207, 255), (255, 190, 128), (167, 130, 255)]
# index 0 - 6 repräsentiert die Tetrominos
font = pygame.font.SysFont('couriernew', int(screen_breite / 20))

class Piece(object):

    def __init__(self, spalte, reihe, tetromino):
        self.shape = tetromino
        self.color = tetromino_farben[tetrominos.index(tetromino)]
        self.rotation = 0  # Nummer von 0 bis 3
        self.x = spalte
        self.y = reihe


def erstelle_grid(gesperrte_positionen={}):
    grid = [[(30,30,30) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)): #jede Zeile durchgehen
        for j in range(len(grid[i])): #jede Spalte durchgehen
            if (j,i) in gesperrte_positionen:
                c = gesperrte_positionen[(j,i)]
                grid[i][j] = c
    return grid

def convertiere_tetromino_format(tetromino):
    positionen = []
    interne_positionen = tetromino.shape

    if tetromino.shape != O:
        for i in range(tetromino.rotation):
            interne_positionen = list(zip(*interne_positionen))[::-1]

    for i, reihe in enumerate(interne_positionen):
        for j, spalte in enumerate(reihe):
            if spalte == 'X':
                positionen.append((tetromino.x + j, tetromino.y + i))

    for i, pos in enumerate(positionen):
        positionen[i] = (pos[0] - 2, pos[1] - 4)

    return positionen


def valid_space(tetromino, grid):
    akzeptierte_positionen = [[(j, i) for j in range(10) if grid[i][j] == (30,30,30)] for i in range(20)]
    akzeptierte_positionen = [j for sub in akzeptierte_positionen for j in sub]
    formatted = convertiere_tetromino_format(tetromino)

    for pos in formatted:
        if pos not in akzeptierte_positionen:
            if pos[1] > -1:
                return False

    return True


def überprüfe_verloren(positionen):
    for pos in positionen:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape(current = None):
    global tetrominos, tetromino_farben
    new_piece = Piece(5, 0, random.choice(tetrominos))
    if current is not None:
        while current.shape == new_piece.shape:
            new_piece = Piece(5, 0, random.choice(tetrominos))

    return new_piece


def draw_text_mitte(text, size, color, surface):
    font = pygame.font.SysFont('couriernew', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (screen_breite / 2 - label.get_width() / 2 , screen_höhe / 2 - label.get_height() / 2))
#    surface.blit(label, (oben_links_x + spiel_breite/2 - (label.get_width() / 2), oben_links_y + spiel_höhe/2 - label.get_height()/2))


def draw_grid(surface, reihe, col):
    sx = oben_links_x
    sy = oben_links_y
    for i in range(reihe):
        pygame.draw.line(surface, (128,128,128), (sx, sy+ i*block_größe), (sx + spiel_breite, sy + i * block_größe))  # horizontal lines
        for j in range(col):
            pygame.draw.line(surface, (128,128,128), (sx + j * block_größe, sy), (sx + j * block_größe, sy + spiel_höhe))  # vertical lines


def reihen_leeren(grid, locked):
    # need to see if reihe is clear the shift every other reihe above down one
    zu_leerende_reihen = []

    for i in range(len(grid) - 1, -1, -1):
        reihe = grid[i]
        if (30, 30, 30) not in reihe:
            zu_leerende_reihen.append(i)
            # Füge Positionen hinzu, die nicht mehr gesperrt werden sollen
            ind = i
            for j in range(len(reihe)):
                try:
                    del locked[(j, i)]
                except:
                    continue

    if zu_leerende_reihen:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            zeilen_unterhalb = 0
            for reihe in zu_leerende_reihen:
                if reihe > y:
                    zeilen_unterhalb += 1

            # if y < min(zu_leerende_reihen):
            new_key = (x, y + zeilen_unterhalb)
            locked[new_key] = locked.pop(key)

    return len(zu_leerende_reihen)


def draw_nächstes_tetromino(tetromino, surface):
    font = pygame.font.SysFont('couriernew', 30)
    #label = font.render('Nächste Form:', 100 , (0,0,0))

    #form = tetromino.shape
    #rotated = list(zip(*tetromino.shape))[::-1]
    #format = tetromino.shape[tetromino.rotation % len(tetromino.shape)]

    first_idx = 2
    last_idx = 2
    for i, line in enumerate(tetromino.shape):
        for j, spalte in enumerate(line):
            if spalte == 'X':
                if first_idx > j:
                    first_idx = j
                if last_idx < j:
                    last_idx = j


    max_length = last_idx - first_idx + 1

    sx = (screen_breite - spiel_breite) // 2 - 2.5 * block_größe
    if max_length == 2:
        sx += block_größe / 2
    sy = screen_höhe * 2 // 5

    for i, line in enumerate(tetromino.shape):
        reihe = list(line)
        for j, spalte in enumerate(reihe):
            if spalte == 'X':
                pygame.draw.rect(surface, tetromino.color, (sx + j*block_größe, sy + i*block_größe, block_größe, block_größe), 0)

    #surface.blit(label, (sx + 15, sy))


def draw_window(surface):
    surface.fill((255,255,255))

    logo = pygame.image.load('logo_ba.jpg')  # Replace 'logo.jpg' with the actual filename of your logo image
    logo = pygame.transform.scale(logo, (screen_breite - spiel_breite - spiel_breite/6, (screen_breite - spiel_breite - spiel_breite/6)/5))  # Adjust the size of the logo as needed

    # Blit the logo and title
    surface.blit(logo, (spiel_breite/12, spiel_breite/18))

    # def button(text, x, y, width, height, inactive_color, active_color, action=None):
    links_breite = screen_breite - spiel_breite

    button("Neustart (n)", links_breite // 30, screen_höhe - 3 * screen_höhe // 15 - 3 * links_breite // 30, screen_breite - spiel_breite - links_breite // 15, screen_höhe // 15, (0, 63, 115), (0, 0, 0), simulate_restart, screen_breite // 35)
    button("Pause (p)", links_breite // 30, screen_höhe - 2 * screen_höhe // 15 - 2 * links_breite // 30, screen_breite - spiel_breite - links_breite // 15, screen_höhe // 15, (0, 63, 115), (0, 0, 0), simulate_pause, screen_breite // 35)
    button("Schließen (q)", links_breite // 30, screen_höhe - screen_höhe // 15 - links_breite // 30, screen_breite - spiel_breite - links_breite // 15, screen_höhe // 15, (0, 63, 115), (0, 0, 0), simulate_quit, screen_breite // 35)

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (oben_links_x + j* block_größe, oben_links_y + i * block_größe, block_größe, block_größe), 0)

    # draw grid and border
    draw_grid(surface, 20, 10)
    pygame.draw.rect(surface, (189, 199, 192), (oben_links_x, oben_links_y, spiel_breite, spiel_höhe), int(spiel_breite / 120))
    # pygame.display.update()



def draw_score(surface, score):
    font = pygame.font.SysFont('couriernew', int(screen_breite / 10))
    label = font.render(str(score), 1, (255, 255, 255))

    sx = (screen_breite - spiel_breite) / 2 - label.get_width() / 2
    sy = (screen_höhe / 4) - label.get_height() // 2

    pygame.draw.circle(surface, (9, 59, 128), ((screen_breite - spiel_breite) // 2, screen_höhe / 4), screen_breite / 10)
    surface.blit(label, (sx, sy))

def draw_instruction(surface):
    font = pygame.font.SysFont('couriernew', 15)
    label1 = font.render('p -> pause', 1, (0,0,0))
    label2 = font.render('q -> Spiel schließen', 1, (0,0,0))
    label3 = font.render('n -> Neues Spiel starten', 1, (0,0,0))

    sx = oben_links_x - 260
    sy = oben_links_y + 500

    surface.blit(label1, (sx, sy))
    surface.blit(label2, (sx, sy + 30))
    surface.blit(label3, (sx, sy + 60))

def main():
    global grid, lautstärke

    gesperrte_positionen = {}  # (x,y):(255,0,0)
    grid = erstelle_grid(gesperrte_positionen)

    change_piece = False
    run = True
    aktuelles_tetromino = get_shape()
    nächstes_tetromino = get_shape(aktuelles_tetromino)
    clock = pygame.time.Clock()
    Fallzeit = 0
    Fallgeschwindigkeit = 0.27
    score = 0

    while run:

        grid = erstelle_grid(gesperrte_positionen)
        Fallzeit += clock.get_rawtime()
        clock.tick()


        # PIECE FALLING CODE
        if Fallzeit/1000 >= Fallgeschwindigkeit:
            Fallzeit = 0
            aktuelles_tetromino.y += 1
            if not (valid_space(aktuelles_tetromino, grid)) and aktuelles_tetromino.y > 0:
                aktuelles_tetromino.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    aktuelles_tetromino.x -= 1
                    if not valid_space(aktuelles_tetromino, grid):
                        aktuelles_tetromino.x += 1

                elif event.key == pygame.K_RIGHT:
                    aktuelles_tetromino.x += 1
                    if not valid_space(aktuelles_tetromino, grid):
                        aktuelles_tetromino.x -= 1
                elif event.key == pygame.K_UP:
                    # rotate shape
                    aktuelles_tetromino.rotation = aktuelles_tetromino.rotation + 1 % len(aktuelles_tetromino.shape)
                    if not valid_space(aktuelles_tetromino, grid):
                        aktuelles_tetromino.rotation = aktuelles_tetromino.rotation - 1 % len(aktuelles_tetromino.shape)

                if event.key == pygame.K_DOWN:
                    # move shape down
                    aktuelles_tetromino.y += 1
                    if not valid_space(aktuelles_tetromino, grid):
                        aktuelles_tetromino.y -= 1

                '''if event.key == pygame.K_SPACE:
                    while valid_space(aktuelles_tetromino, grid):
                        aktuelles_tetromino.y += 1
                    aktuelles_tetromino.y -= 1
                    print(convertiere_tetromino_format(aktuelles_tetromino))'''  # todo fix

                if event.key == pygame.K_p:
                    # Toggle pause state
                    mixer.music.set_volume(0)
                    pausenmenü(win)
                    mixer.music.set_volume(lautstärke)
                    #mixer.music.play
                elif event.key == pygame.K_n:
                    hauptmenü()
                elif event.key == pygame.K_q:
                    quit()

        shape_pos = convertiere_tetromino_format(aktuelles_tetromino)

        # add piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = aktuelles_tetromino.color

        # Wenn das Tetromino den Grund berührt
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                gesperrte_positionen[p] = aktuelles_tetromino.color
            aktuelles_tetromino = nächstes_tetromino
            nächstes_tetromino = get_shape(aktuelles_tetromino)
            change_piece = False

            # call four times to check for multiple clear reihes
            reihen_geleert = reihen_leeren(grid, gesperrte_positionen)
            if reihen_geleert > 0:
                score += reihen_geleert * 1

        draw_window(win)
        draw_nächstes_tetromino(nächstes_tetromino, win)
        draw_score(win, score)  # Zeige den Punktestand an
        # draw_instruction(win)  # Zeige die Instruction an
        pygame.display.update()

        # Check if user lost
        if überprüfe_verloren(gesperrte_positionen):
            run = False

    label = pygame.font.SysFont('couriernew', int(screen_breite / 20), bold=True)
    prompt_text = label.render('Verloren!', True, (255, 255, 255))
    prompt_rect = prompt_text.get_rect(center=(screen_breite - spiel_breite // 2, screen_höhe // 2))
    win.blit(prompt_text, prompt_rect)

    speichere_score(user, score)
    draw_score(win, score)  # Zeige den Endpunktestand an
    pygame.display.update()
    pygame.time.delay(2000)

def quit():
    pygame.quit()
    sys.exit()

def hauptmenü():
    run = True

    while run:
        win.fill((255, 255, 255))

        font = pygame.font.SysFont('couriernew', 30)
        titel_text = font.render('Willkommen bei Tetris', True, (0, 63, 115))
        title_rect = titel_text.get_rect(center=(screen_breite // 2, 50))
        win.blit(titel_text, title_rect)

        menu_text = font.render('Menü', True, (0, 63, 115))
        menu_rect = menu_text.get_rect(center=(screen_breite // 2, 100))
        win.blit(menu_text, menu_rect)

        button("Neues Spiel", screen_breite // 3, screen_höhe // 2, screen_breite // 3, screen_höhe // 15, (0, 63, 115), (0, 0, 0), input_username)
        button("Scoreboard", screen_breite // 3, screen_höhe // 2 + 100, screen_breite // 3, screen_höhe // 15, (0, 63, 115), (0, 0, 0), display_scoreboard)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
    pygame.quit()

def pausenmenü(surface):
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    # Resume the game
                    return

        pygame.draw.rect(surface, (30, 30, 30), (screen_breite - spiel_breite + spiel_breite / 240, screen_höhe - spiel_höhe + spiel_breite / 240, spiel_breite - 2 * spiel_breite / 240, spiel_höhe - 2 * spiel_breite / 240), 0)

        #draw_text_mitte('Paused', 60, (255, 255, 255), win)
        button("Fortsetzen", screen_breite - spiel_breite // 2 - spiel_breite // 4, screen_höhe // 2 - spiel_höhe // 40, spiel_breite // 2, spiel_höhe // 20, (0, 63, 115), (26, 99, 201), simulate_pause, int(spiel_breite // 20))
        pygame.display.update()


def simulate_pause():
    newevent = pygame.event.Event(pygame.KEYDOWN, unicode="p", key=pygame.K_p, mod=pygame.KMOD_NONE) #create the event
    pygame.event.post(newevent)

def simulate_quit():
    newevent = pygame.event.Event(pygame.KEYDOWN, unicode="q", key=pygame.K_q, mod=pygame.KMOD_NONE) #create the event
    pygame.event.post(newevent)

def simulate_restart():
    newevent = pygame.event.Event(pygame.KEYDOWN, unicode="n", key=pygame.K_n, mod=pygame.KMOD_NONE) #create the event
    pygame.event.post(newevent)

def button(text, x, y, breite, höhe, inactive_color, active_color, action=None, fontsize = 20):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x < mouse[0] < x + breite and y < mouse[1] < y + höhe:
        pygame.draw.rect(win, active_color, (x, y, breite, höhe))

        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(win, inactive_color, (x, y, breite, höhe))

    small_text = pygame.font.SysFont('couriernew', fontsize)
    text_surf, text_rect = text_objekte(text, small_text)
    text_rect.center = (x + breite / 2, y + höhe / 2)
    win.blit(text_surf, text_rect)

def text_objekte(text, font):
    text_surface = font.render(text, True, (255, 255, 255))
    return text_surface, text_surface.get_rect()

def input_username():
    run = True
    username = ""
    global user

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main()
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode

        win.fill((255, 255, 255))

        # Display text in the center of the window
        label = pygame.font.SysFont('couriernew', int(screen_breite / 20), bold=True)
        prompt_text = label.render('Enter Your Username:', True, (0, 63, 115))
        prompt_rect = prompt_text.get_rect(center=(screen_breite // 2, screen_höhe // 2 - 50))
        win.blit(prompt_text, prompt_rect)

        input_text = font.render(username, True, (0, 63, 115))
        input_rect = input_text.get_rect(center=(screen_breite // 2, screen_höhe // 2))
        win.blit(input_text, input_rect)

        button("Start Game", screen_breite // 3, screen_höhe * 2 // 3 + screen_höhe // 8, screen_breite // 3, screen_höhe // 15,
               (0, 63, 115), (0, 0, 0), main)
        button("Zurück", screen_breite // 3, screen_höhe * 2 // 3 + screen_höhe // 5, screen_breite // 3, screen_höhe // 15,
               (0, 63, 115), (0, 0, 0), hauptmenü)


        pygame.display.update()
        user = username

    return username

def speichere_score(username, score):
    try:
        scores = pickle.load(open('scores.pkl', 'rb'))
    except (FileNotFoundError, EOFError):
        scores = []

    scores.append((username, score))
    scores.sort(key=lambda x: x[1], reverse=True)  # Sort scores in descending order

    with open('scores.pkl', 'wb') as file:
        pickle.dump(scores, file)

def lade_top_scores():
    try:
        scores = pickle.load(open('scores.pkl', 'rb'))
        return scores[:3]  # Return top 3 scores
    except (FileNotFoundError, EOFError):
        return []


def display_scoreboard():
    run = True

    while run:
        top_scores = lade_top_scores()

        win.fill((255, 255, 255))

        font = pygame.font.SysFont('couriernew', 30)
        titel_text = font.render('Top 3 Scores', True, (0, 63, 115))
        title_rect = titel_text.get_rect(center=(screen_breite // 2, 50))
        win.blit(titel_text, title_rect)

        for i, (username, score) in enumerate(top_scores):
            score_text = font.render(f"{i + 1}. {username} : {score}", True, (0, 63, 115))
            score_rect = score_text.get_rect(center=(screen_breite // 2, 100 + i * 50))
            win.blit(score_text, score_rect)


        button_breite = screen_breite - spiel_breite - 2 * (screen_breite // 30)
        button_höhe = screen_höhe // 15
        button_x = (screen_breite - button_breite) // 2
        button_y = screen_höhe - 3 * screen_höhe // 15 - 3 * (screen_breite // 30)

        button("Zurück", button_x, button_y, button_breite, button_höhe, (0, 63, 115), (0, 0, 0), hauptmenü, screen_breite // 35)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()



mixer.init()
mixer.music.load('Soundtrack.mp3')
mixer.music.set_volume(lautstärke)
mixer.music.play(100)
win = pygame.display.set_mode((screen_breite, screen_höhe))
pygame.display.set_caption('Tetris Game')

hauptmenü()  # start game






