import sys
import pickle
import pygame
import random
import time
from pygame import mixer

pygame.font.init() #initialisiert das Schriftmodul in pygame

# Globale Variablen
lautstärke = 0.01
screen_breite = 600
screen_höhe = screen_breite
spiel_breite = screen_breite / 2
spiel_höhe = screen_breite
block_größe = spiel_höhe / 20
oben_links_x = screen_breite - spiel_breite #x-Position der oberen linken Ecke des Spielfeldes
oben_links_y = screen_höhe - spiel_höhe #y-Position der oberen linken Ecke des Spielfeldes

MENÜ_eventtype = pygame.event.custom_type()
PAUSE_eventtype = pygame.event.custom_type()
QUIT_eventtype = pygame.event.custom_type()


# Tetrominos
#Definition der Formen der Tetrominos

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
tetromino_farben = [(0, 110, 176), (255, 125, 0), (255, 201, 0), (48, 3, 156), (128, 207, 255), (255, 190, 128), (167, 130, 255)] #Definition der Farben der Tetrominos
schrift = pygame.font.Font('Roboto-Medium.ttf', int(screen_breite / 20)) #Definition der Schriftart und -größe

class Stück(object):
    def __init__(self, spalte, reihe, tetromino):
        self.shape = tetromino
        self.farbe = tetromino_farben[tetrominos.index(tetromino)]
        self.rotation = 0
        self.x = spalte
        self.y = reihe

def erstelle_grid(gesperrte_positionen={}): #Erstellt ein Raster (Grid)
    grid = [[(30,30,30) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j,i) in gesperrte_positionen:
                c = gesperrte_positionen[(j,i)]
                grid[i][j] = c
    return grid

def convertiere_tetromino_format(tetromino): #Konvertiert die From des Tetrominos in eine Liste von Positionen
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

def platz_gültig(tetromino, grid): #Überprüft, ob der gegebene Tetromino an einer gültigen Position ist
    akzeptierte_positionen = [[(j, i) for j in range(10) if grid[i][j] == (30,30,30)] for i in range(20)]
    akzeptierte_positionen = [j for sub in akzeptierte_positionen for j in sub]
    formatiert = convertiere_tetromino_format(tetromino)

    for position in formatiert:
        if position not in akzeptierte_positionen:
            if position[1] > -1:
                return False
    return True

def überprüfe_verloren(positionen): #Überprüft, ob das Spiel verloren ist (ein Tetromino hat die oberste Reihe erreicht)
    for position in positionen:
        x, y = position
        if y < 1:
            return True
    return False


def tetromino_erzeugen(aktuelles_tetromino = None): #Gibt ein neues Tetromino zurück, das nicht die gleiche Form wie das aktuelle hat
    global tetrominos, tetromino_farben
    neues_stück = Stück(5, 0, random.choice(tetrominos))
    if aktuelles_tetromino is not None:
        while aktuelles_tetromino.shape == neues_stück.shape:
            neues_stück = Stück(5, 0, random.choice(tetrominos))
    return neues_stück

def grid_zeichnen(oberfläche, anzahl_reihen, spalten): #Zeichnet das Raster (Grid)
    start_x = oben_links_x
    start_y = oben_links_y

    for i in range(anzahl_reihen):
        pygame.draw.line(oberfläche, (128,128,128), (start_x, start_y + i * block_größe), (start_x + spiel_breite, start_y + i * block_größe))  # horizontal lines
        for j in range(spalten):
            pygame.draw.line(oberfläche, (128,128,128), (start_x + j * block_größe, start_y), (start_x + j * block_größe, start_y + spiel_höhe))  # vertical lines

def reihen_leeren(grid, gesperrt): #Entfernt alle vollen Reihen aus dem Raster und verschiebt die darüberliegenden Reihen nach unten
    zu_leerende_reihen = []
    for reihe_index in range(len(grid) - 1, -1, -1):
        reihe = grid[reihe_index]
        if (30, 30, 30) not in reihe:
            zu_leerende_reihen.append(reihe_index)
            for spalten_index in range(len(reihe)):
                try:
                    del gesperrt[(spalten_index, reihe_index)]
                except:
                    continue
    if zu_leerende_reihen:
        for key in sorted(list(gesperrt), key=lambda x: x[1])[::-1]:
            x, y = key
            zeilen_unterhalb = 0
            for reihe in zu_leerende_reihen:
                if reihe > y:
                    zeilen_unterhalb += 1
            neuer_Schlüssel = (x, y + zeilen_unterhalb)
            gesperrt[neuer_Schlüssel] = gesperrt.pop(key)
    return len(zu_leerende_reihen)

def nächstes_tetromino_zeichnen(tetromino, oberfläche): #Zeichnet das nächste Tetromino
    erster_index = 2
    letzter_index = 2
    for reihe_index, reihe in enumerate(tetromino.shape):
        for spalten_index, spalte in enumerate(reihe):
            if spalte == 'X':
                if erster_index > spalten_index:
                    erster_index = spalten_index
                if letzter_index < spalten_index:
                    letzter_index = spalten_index
    max_länge = letzter_index - erster_index + 1
    start_x = (screen_breite - spiel_breite) // 2 - 2.5 * block_größe
    if max_länge  == 2:
        start_x += block_größe / 2
    start_y = screen_höhe * 2 // 5

    for reihe_index, reihe in enumerate(tetromino.shape):
        aktuelle_reihe = list(reihe)
        for spalten_index, spalte in enumerate(aktuelle_reihe):
            if spalte == 'X':
                pygame.draw.rect(oberfläche, tetromino.farbe, (start_x + spalten_index * block_größe, start_y +  reihe_index * block_größe, block_größe, block_größe), 0)

def spielfenster_erzeugen(oberfläche): #Zeichnet das Fenster des Spiels
    oberfläche.fill((255,255,255))

    logo = pygame.image.load('logo_ba.jpg')
    logo = pygame.transform.scale(logo, (screen_breite - spiel_breite - spiel_breite/6, (screen_breite - spiel_breite - spiel_breite/6)/5))  # Adjust the size of the logo as needed
    oberfläche.blit(logo, (spiel_breite/12, spiel_breite/18))

    links_breite = screen_breite - spiel_breite
    button("Menü (m)", links_breite // 30, screen_höhe - 3 * screen_höhe // 15 - 3 * links_breite // 30, screen_breite - spiel_breite - links_breite // 15, screen_höhe // 15, (0, 63, 115), (0, 0, 0), MENÜ_eventtype, screen_breite // 35)
    button("Pause (p)", links_breite // 30, screen_höhe - 2 * screen_höhe // 15 - 2 * links_breite // 30, screen_breite - spiel_breite - links_breite // 15, screen_höhe // 15, (0, 63, 115), (0, 0, 0), PAUSE_eventtype, screen_breite // 35)
    button("Schließen (q)", links_breite // 30, screen_höhe - screen_höhe // 15 - links_breite // 30, screen_breite - spiel_breite - links_breite // 15, screen_höhe // 15, (0, 63, 115), (0, 0, 0), QUIT_eventtype, screen_breite // 35)

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(oberfläche, grid[i][j], (oben_links_x + j* block_größe, oben_links_y + i * block_größe, block_größe, block_größe), 0)

    # draw grid and border
    grid_zeichnen(oberfläche, 20, 10)
    pygame.draw.rect(oberfläche, (189, 199, 192), (oben_links_x, oben_links_y, spiel_breite, spiel_höhe), int(spiel_breite / 120))

def score_zeichnen(oberfläche, score): #Zeichnet den aktuellen Score (Spielstand)
    schrift = pygame.font.Font('Roboto-Medium.ttf', int(screen_breite / 9))
    punktzahl_label = schrift.render(str(score), 1, (255, 255, 255))

    x_punktzahl = (screen_breite - spiel_breite) / 2 - punktzahl_label.get_width() / 2
    y_punktzahl = (screen_höhe / 4) - punktzahl_label.get_height() // 2

    pygame.draw.circle(oberfläche, (9, 59, 128), ((screen_breite - spiel_breite) // 2, screen_höhe / 4), screen_breite / 10)
    oberfläche.blit(punktzahl_label, (x_punktzahl, y_punktzahl))

def main():
    global grid, lautstärke
    gesperrte_positionen = {}  # (x,y):(255,0,0)
    grid = erstelle_grid(gesperrte_positionen)
    tetromino_wechsel = False
    run = True
    aktuelles_tetromino = tetromino_erzeugen()
    nächstes_tetromino = tetromino_erzeugen(aktuelles_tetromino)
    uhr = pygame.time.Clock()
    Fallzeit = 0
    Fallgeschwindigkeit = 0.27
    score = 0

    hauptmenü()

    while run:
        war_in_menü = False
        grid = erstelle_grid(gesperrte_positionen)
        Fallzeit += uhr.get_rawtime()
        uhr.tick()

        # PIECE FALLING CODE
        if Fallzeit/1000 >= Fallgeschwindigkeit:
            Fallzeit = 0
            aktuelles_tetromino.y += 1
            if not (platz_gültig(aktuelles_tetromino, grid)) and aktuelles_tetromino.y > 0:
                aktuelles_tetromino.y -= 1
                tetromino_wechsel = True

        for event in pygame.event.get():
            if event.type == QUIT_eventtype or event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()
            elif event.type == PAUSE_eventtype:
                    mixer.music.set_volume(0)
                    pausenmenü(win)
                    mixer.music.set_volume(lautstärke)
            elif event.type == MENÜ_eventtype:
                war_in_menü = True
                hauptmenü()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    aktuelles_tetromino.x -= 1
                    if not platz_gültig(aktuelles_tetromino, grid):
                        aktuelles_tetromino.x += 1
                elif event.key == pygame.K_RIGHT:
                    aktuelles_tetromino.x += 1
                    if not platz_gültig(aktuelles_tetromino, grid):
                        aktuelles_tetromino.x -= 1
                elif event.key == pygame.K_UP:
                    # rotate shape
                    aktuelles_tetromino.rotation = aktuelles_tetromino.rotation + 1 % len(aktuelles_tetromino.shape)
                    if not platz_gültig(aktuelles_tetromino, grid):
                        aktuelles_tetromino.rotation = aktuelles_tetromino.rotation - 1 % len(aktuelles_tetromino.shape)
                elif event.key == pygame.K_DOWN:
                    # move shape down
                    aktuelles_tetromino.y += 1
                    if not platz_gültig(aktuelles_tetromino, grid):
                        aktuelles_tetromino.y -= 1

        #if war_in_menü == False:
        tetromino_position = convertiere_tetromino_format(aktuelles_tetromino)

        # add piece to the grid for drawing
        for tetromino_index in range(len(tetromino_position)):
            x, y = tetromino_position[tetromino_index]
            if y > -1:
                grid[y][x] = aktuelles_tetromino.farbe

        # Wenn das Tetromino den Grund berührt
        if tetromino_wechsel:
            for position in tetromino_position:
                p = (position[0], position[1])
                gesperrte_positionen[p] = aktuelles_tetromino.farbe
            aktuelles_tetromino = nächstes_tetromino
            nächstes_tetromino = tetromino_erzeugen(aktuelles_tetromino)
            tetromino_wechsel = False

            # call four times to check for multiple clear reihes
            reihen_geleert = reihen_leeren(grid, gesperrte_positionen)
            if reihen_geleert > 0:
                score += reihen_geleert * 1

        spielfenster_erzeugen(win)
        nächstes_tetromino_zeichnen(nächstes_tetromino, win)
        score_zeichnen(win, score)
        pygame.display.update()

        if überprüfe_verloren(gesperrte_positionen):
            run = False

    schrift = pygame.font.Font('Roboto-Medium.ttf', int(screen_breite / 20))
    text_verloren = schrift.render('Verloren!', True, (255, 255, 255))
    rect_verloren = text_verloren.get_rect(center=(screen_breite - spiel_breite // 2, screen_höhe // 2))
    win.blit(text_verloren, rect_verloren)

    score_speichern(benutzer, score)
    score_zeichnen(win, score)
    pygame.display.update()
    pygame.time.delay(2000)
    main()

def wait(key):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                return

def quit():
    pygame.quit() #Beendet alle PyGame-Module
    sys.exit() #Beendet das Python-Skript

def hauptmenü():
    global benutzer
    run = True
    überschrift = pygame.font.Font('Roboto-Bold.ttf', int(screen_breite / 10))
    schrift = pygame.font.Font('Roboto-Medium.ttf', int(screen_breite / 20))
    schrift_dünn = pygame.font.Font('Roboto-Light.ttf', int(screen_breite / 20))
    K_Return = pygame.event.Event(pygame.KEYDOWN, unicode="m", key=pygame.K_RETURN, mod=pygame.KMOD_NONE)
    benutzername = benutzer


    #while run:
    win.fill((255, 255, 255))
    menü_text = überschrift.render('Tetris', True, (0, 63, 115))
    menü_rect = menü_text.get_rect(center=(screen_breite // 2, screen_höhe // 8))


    while run:
        win.fill((255, 255, 255))
        win.blit(menü_text, menü_rect)

        button("Neues Spiel", screen_breite // 3, screen_höhe * 7 // 8, screen_breite // 3, screen_höhe // 15, (0, 63, 115), (0, 0, 0), MENÜ_eventtype)

        # Scoreboards
        top_scores = lade_top_scores()
        titel_text = schrift.render('Top 3 Scores', True, (0, 63, 115))
        titel_rect = titel_text.get_rect(center=(screen_breite // 2, screen_höhe // 4))
        win.blit(titel_text, titel_rect)

        for i, (name, score) in enumerate(top_scores):
            score_text = schrift_dünn.render(f"{i + 1}. {name} : {score}", True, (0, 63, 115))
            score_rect = score_text.get_rect(center=(screen_breite // 2, screen_höhe // 4 + (i + 1) * screen_höhe // 15))
            win.blit(score_text, score_rect)

        prompt_text = schrift.render('Gib deinen Benutzernamen ein:', True, (0, 63, 115))
        prompt_rect = prompt_text.get_rect(center=(screen_breite // 2, screen_höhe * 11 // 16))
        win.blit(prompt_text, prompt_rect)

        eingabe_text = schrift_dünn.render(benutzername, True, (0, 63, 115))
        eingabe_rect = eingabe_text.get_rect(center=(screen_breite // 2, screen_höhe * 6 // 8))
        win.blit(eingabe_text, eingabe_rect)

        

        pygame.display.update() #Aktualisiert das Fenster
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit() #Beendet alle PyGame-Module
                sys.exit() #Beendet das Python-Skript
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                benutzername = benutzername[:-1]
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                run = False
                benutzer = benutzername
            elif event.type == pygame.KEYDOWN:
                benutzername += event.unicode
            elif event.type == MENÜ_eventtype:
                run = False


def pausenmenü(oberfläche):
    pausiert = True
    pause = pygame.event.Event(pygame.KEYDOWN, unicode="p", key=pygame.K_p, mod=pygame.KMOD_NONE) #create the event
    while pausiert:

        pygame.draw.rect(oberfläche, (30, 30, 30), (screen_breite - spiel_breite + spiel_breite / 240, screen_höhe - spiel_höhe + spiel_breite / 240, spiel_breite - 2 * spiel_breite / 240, spiel_höhe - 2 * spiel_breite / 240), 0)
        button("Fortsetzen", screen_breite - spiel_breite // 2 - spiel_breite // 4, screen_höhe // 2 - spiel_höhe // 40, spiel_breite // 2, spiel_höhe // 20, (0, 63, 115), (26, 99, 201), PAUSE_eventtype, int(spiel_breite // 20))
        pygame.display.update() #Aktualisiert das Fenster

        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit() #Beendet alle PyGame-Module
            sys.exit() #Beendet das Python-Skript
        elif event.type == PAUSE_eventtype:
            pausiert = False


def button(text, x, y, breite, höhe, inactive_farbe, active_farbe, aktion=None, schriftgröße = 20):
    mausposition = pygame.mouse.get_pos() #Position der Maus
    mausklick = pygame.mouse.get_pressed() #Ob die Maustaste gedrückt wurde

    if x < mausposition[0] < x + breite and y < mausposition[1] < y + höhe:
        pygame.draw.rect(win, active_farbe, (x, y, breite, höhe))
        if mausklick[0] == 1 and aktion is not None:
            pygame.event.post(pygame.event.Event(aktion))
    else:
        pygame.draw.rect(win, inactive_farbe, (x, y, breite, höhe))

    schrift = pygame.font.Font('Roboto-Medium.ttf', int(screen_breite / 24))
    text_oberfläche, text_rect = text_objekte(text, schrift)
    text_rect.center = (x + breite / 2, y + höhe / 2)
    win.blit(text_oberfläche, text_rect)

def text_objekte(text, schrift):
    text_oberfläche = schrift.render(text, True, (255, 255, 255))
    return text_oberfläche, text_oberfläche.get_rect()


def score_speichern(benutzername, score): #Speichert den Score in einer Datei
    try:
        scores = pickle.load(open('benutzer_score.pkl', 'rb')) #Versucht die gespeicherten Punktestände zu laden
    except (FileNotFoundError, EOFError): #Wenn keine gefunden werden wird eine leere Liste erstellt
        scores = []

    scores.append((benutzername, score))
    scores.sort(key=lambda x: x[1], reverse=True)  #Sortiet die Liste in absteigender Reihenfolge

    with open('benutzer_score.pkl', 'wb') as datei:
        pickle.dump(scores, datei)

def lade_top_scores(): #Gibt die besten 3 Scores zurück
    try:
        scores = pickle.load(open('benutzer_score.pkl', 'rb'))
        return scores[:3]  # Return top 3 scores
    except (FileNotFoundError, EOFError):
        return []




mixer.init()
mixer.music.load('Soundtrack.mp3') #Läd die Hintergrundmusik
mixer.music.set_volume(lautstärke) #Setzt die Lautstärke der Musik fest
mixer.music.play(100)
win = pygame.display.set_mode((screen_breite, screen_höhe))
pygame.display.set_caption('Tetris Game')

global benutzer
benutzer = "anonym"

main()

#hauptmenü()





