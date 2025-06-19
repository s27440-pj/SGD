import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flip Cup")
big_font = pygame.font.SysFont("Century", 44, bold=True)
font = pygame.font.SysFont("Century", 28)
small_font = pygame.font.SysFont("Century", 18)
background_image = pygame.image.load("piwo.jpg").convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
flip_sound = pygame.mixer.Sound("flip.mp3")

WHITE = (255, 255, 255)
RED = (220, 50, 50)
BLUE = (50, 50, 220)
GREEN = (50, 200, 50)
YELLOW = (255, 223, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (181, 152, 127)
GRAY = (180, 180, 180)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

DRINK_REQUIRED_PRESSES = 20
FLIP_ZONE_WIDTH = 60
BAR_WIDTH = 300
BAR_HEIGHT = 20
BAR_Y = HEIGHT // 2 + 60
CUPS_PER_PLAYER = 4
FLIP_SPEED = 4

clock = pygame.time.Clock()

class Player:
    def __init__(self, key, side):
        self.key = key
        self.drinks_done = 0
        self.presses = 0
        self.flipping = False
        self.side = side

        self.bar_x = WIDTH // 4 - BAR_WIDTH // 2 if side == 'left' else WIDTH * 3 // 4 - BAR_WIDTH // 2
        self.bar_y = BAR_Y
        self.zone_center = self.bar_x + BAR_WIDTH // 2
        self.zone_start = self.zone_center - FLIP_ZONE_WIDTH // 2

        self.marker_pos = self.bar_x
        self.marker_dir = FLIP_SPEED

    def start_flipping(self):
        self.flipping = True
        self.marker_pos = self.bar_x
        self.marker_dir = min(FLIP_SPEED + 2 * self.drinks_done, 10)

    def update_flip(self):
        if self.flipping:
            self.marker_pos += self.marker_dir
            if self.marker_pos <= self.bar_x or self.marker_pos >= self.bar_x + BAR_WIDTH - 10:
                self.marker_dir *= -1

    def check_flip(self):
        return self.zone_start <= self.marker_pos <= self.zone_start + FLIP_ZONE_WIDTH

    def draw(self):
        # Pasek i strefa trafienia
        pygame.draw.rect(screen, GRAY, (self.bar_x, self.bar_y, BAR_WIDTH, BAR_HEIGHT))
        pygame.draw.rect(screen, GREEN, (self.zone_start, self.bar_y, FLIP_ZONE_WIDTH, BAR_HEIGHT))

        if self.flipping:
            color = RED if self.side == 'left' else BLUE
            pygame.draw.rect(screen, color, (self.marker_pos, self.bar_y, 10, BAR_HEIGHT))

        x_text = 50 if self.side == 'left' else WIDTH // 2 + 50
        label = f"{self.key}: {'Flip!' if self.flipping else f'Pij ({self.presses}/{DRINK_REQUIRED_PRESSES})'}"
        screen.blit(font.render(label, True, BLACK), (x_text, 100))

        cups = f"Gracz: {self.drinks_done}/{CUPS_PER_PLAYER}"
        screen.blit(font.render(cups, True, BLACK), (x_text, 140))

class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text

    def draw(self):
        pygame.draw.rect(screen, LIGHT_BROWN, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        txt = font.render(self.text, True, BLACK)
        txt_rect = txt.get_rect(center=self.rect.center)
        screen.blit(txt, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = LIGHT_BROWN
        self.text = text
        self.txt_surface = font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = font.render(self.text, True, self.color)

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))


def draw_end(winner_text):
    screen.blit(background_image, (0, 0))
    txt = big_font.render(winner_text, True, BLACK)
    rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(txt, rect)
    pygame.display.flip()
    pygame.time.delay(3000)

def draw_mug(x, y, sips_taken=0):
    width = 40
    height = 100
    thickness = 3
    pygame.draw.line(screen, BLACK, (x, y + height), (x + width, y + height), thickness)
    pygame.draw.line(screen, BLACK, (x, y), (x, y + height), thickness)
    pygame.draw.line(screen, BLACK, (x + width, y), (x + width, y + height), thickness)
    pygame.draw.arc(screen, BLACK, (x - 20, y + 20, 40, 60), 3.14 / 2, 3 * 3.14 / 2, thickness)

    # Beer
    beer_margin = 10
    max_beer_height = height - beer_margin
    sips_taken = min(sips_taken, DRINK_REQUIRED_PRESSES)
    current_beer_height = max_beer_height * (1 - sips_taken / DRINK_REQUIRED_PRESSES)
    beer_top = y + beer_margin + (max_beer_height - current_beer_height)
    pygame.draw.rect(
        screen,
        YELLOW,
        (x + thickness, beer_top, width - 2 * thickness, current_beer_height)
    )

def show_player_change_message(side):
    message = "Flip udany! Kolejny gracz!"
    message_surface = font.render(message, True, BLACK)
    message_rect = message_surface.get_rect()

    if side =="left":
        rect = pygame.Rect(0, 0, WIDTH //2, HEIGHT)
        message_rect.center = (WIDTH // 4, HEIGHT // 2)
    else:
        rect = pygame.Rect(WIDTH //2, 0, WIDTH // 2, HEIGHT)
        message_rect.center = (WIDTH*3 // 4, HEIGHT // 2)

    flip_sound.play()
    screen.fill(WHITE, rect)
    screen.blit(message_surface, message_rect)
    pygame.display.update(rect)
    pygame.time.delay(2000)  # 2 sekundy

def show_instruction_popup():
    popup = pygame.Rect(200, 150, 600, 300)
    ok_button = Button((popup.centerx - 50, popup.bottom - 60, 100, 40), "OK")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ok_button.is_clicked(event.pos):
                    running = False

        pygame.draw.rect(screen, WHITE, popup)
        pygame.draw.rect(screen, BLACK, popup, 2)
        instructions = [
            "Instrukcja:",
            "- Naciśnij A (drużyna po lewej) lub L (drużyna po prawej),",
            "  aby pić piwo."
            "- Po wypiciu traf w środek paska, aby flipnąć kubkiem",
            "  (wciskając odpowiednio a albo l).",
            "- Drużyna, która pierwsza flipnie wszystkie kubki – wygrywa!"
        ]
        for i, line in enumerate(instructions):
            txt = small_font.render(line, True, BLACK)
            screen.blit(txt, (popup.x + 20, popup.y + 20 + i * 30))
        ok_button.draw()
        pygame.display.flip()
        clock.tick(30)

def show_game_start():
    input_a = InputBox(350, 200, 300, 40)
    input_l = InputBox(350, 270, 300, 40)
    input_players_num = InputBox(350, 340, 300, 40)
    start_button = Button((450, 410, 100, 50), "Start")
    return_button = Button((450, 480, 100, 50), "Powrót")
    input_boxes = [input_a, input_l, input_players_num]
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for box in input_boxes:
                box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_clicked(event.pos):
                    try:
                        players_num = int(input_players_num.text)
                        if players_num < 1:
                            players_num = 4
                    except ValueError:
                        players_num = 4
                    return input_a.text, input_l.text, players_num
                elif return_button.is_clicked(event.pos):
                    main_menu()

        screen.blit(background_image, (0, 0))
        screen.blit(font.render("Podaj dane:", True, BLACK), (350, 150))
        screen.blit(small_font.render("Drużyna po lewej:", True, BLACK), (195, 210))
        screen.blit(small_font.render("Drużyna po prawej:", True, BLACK), (185, 280))
        screen.blit(small_font.render("Liczba graczy w drużynie:", True, BLACK), (130, 350))
        for box in input_boxes:
            box.draw()
        start_button.draw()
        return_button.draw()
        pygame.display.flip()
        clock.tick(30)

def main_menu():
    instruction_btn = Button((400, 250, 200, 50), "Instrukcja")
    new_game_btn = Button((400, 310, 200, 50), "Nowa gra")
    exit_btn = Button((400, 370, 200, 50), "Wyjście")
    running = True

    while running:
        screen.blit(background_image, (0, 0))
        screen.blit(big_font.render("Zapraszamy do gry Flip Cup!", True, BLACK), (230, 150))
        instruction_btn.draw()
        new_game_btn.draw()
        exit_btn.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if instruction_btn.is_clicked(event.pos):
                    show_instruction_popup()
                elif exit_btn.is_clicked(event.pos):
                    pygame.quit()
                elif new_game_btn.is_clicked(event.pos):
                    team_a, team_l, players_num = show_game_start()
                    main(team_a, team_l, players_num)

        pygame.display.flip()
        clock.tick(30)

def main(team_a_name="A", team_l_name="L", cups_per_player=4):
    global CUPS_PER_PLAYER
    CUPS_PER_PLAYER = cups_per_player
    sips = 0
    player_a = Player(team_a_name, "left")
    player_l = Player(team_l_name, "right")
    game_over = False

    while not game_over:
        screen.fill(WHITE)
        draw_mug(900, 100, player_l.presses)
        draw_mug(400, 100, player_a.presses)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Picie i flipowanie
            if event.type == pygame.KEYDOWN:
                # Gracz lewy (a)
                if event.key == pygame.K_a:
                    if not player_a.flipping:
                        player_a.presses += 1
                        if player_a.presses >= DRINK_REQUIRED_PRESSES:
                            player_a.start_flipping()
                    else:
                        if player_a.check_flip():
                            player_a.drinks_done += 1
                            player_a.flipping = False
                            player_a.presses = 0
                            if player_a.drinks_done < cups_per_player:
                                show_player_change_message("left")
                        else: # odbicie
                            player_a.marker_dir *= -1

                # Gracz prawy (l)
                if event.key == pygame.K_l:
                    if not player_l.flipping:
                        player_l.presses += 1
                        if player_l.presses >= DRINK_REQUIRED_PRESSES:
                            player_l.start_flipping()
                    else:
                        if player_l.check_flip():
                            player_l.drinks_done += 1
                            player_l.flipping = False
                            player_l.presses = 0
                            if player_l.drinks_done < cups_per_player:
                                show_player_change_message("right")
                        else:
                            player_l.marker_dir *= -1  # pudło

        player_a.update_flip()
        player_l.update_flip()

        # Rysowanie
        pygame.draw.line(screen, BLACK, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)
        player_a.draw()
        player_l.draw()

        # Sprawdzenie końca gry
        if player_a.drinks_done >= cups_per_player and player_l.drinks_done >= cups_per_player:
            draw_end("Remis!")
            game_over = True
        elif player_a.drinks_done >= cups_per_player:
            draw_end(f"Wygrała Drużyna {team_a_name} grająca po lewej!")
            game_over = True
        elif player_l.drinks_done >= cups_per_player:
            draw_end(f"Wygrała Drużyna {team_l_name} grająca po prawej!")
            game_over = True

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()
