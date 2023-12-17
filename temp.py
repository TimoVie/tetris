def hauptmenü():
    run = True
    schrift = pygame.font.SysFont('couriernew', 30)

    while run:
        win.fill((255, 255, 255))
        titel_text = schrift.render('Willkommen bei Tetris', True, (0, 63, 115))
        titel_rect = titel_text.get_rect(center=(screen_breite // 2, 50))
        win.blit(titel_text, titel_rect)

        menü_text = schrift.render('Menü', True, (0, 63, 115))
        menü_rect = menü_text.get_rect(center=(screen_breite // 2, 100))
        win.blit(menü_text, menü_rect)

        # Scoreboards
        top_scores = lade_top_scores()
        titel_text = schrift.render('Top 3 Scores', True, (0, 63, 115))
        titel_rect = titel_text.get_rect(center=(screen_breite // 2, 200))
        win.blit(titel_text, titel_rect)

        for i, (benutzername, score) in enumerate(top_scores):
            score_text = schrift.render(f"{i + 1}. {benutzername} : {score}", True, (0, 63, 115))
            score_rect = score_text.get_rect(center=(screen_breite // 2, 250 + i * 50))
            win.blit(score_text, score_rect)


        button("Neues Spiel", screen_breite // 3, screen_höhe // 1.2, screen_breite // 3, screen_höhe // 15, (0, 63, 115), (0, 0, 0), benutzer_eingabe)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        pygame.display.update()
    pygame.quit()
    sys.exit()