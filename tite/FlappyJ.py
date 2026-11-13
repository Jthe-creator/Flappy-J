import pygame
import sys
import random

pygame.init()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

COLOR_SKY = (113, 197, 207)
COLOR_BIRD = (247, 212, 34)
COLOR_PIPE = (115, 191, 46)
COLOR_GROUND = (222, 216, 149)
COLOR_TEXT = (255, 255, 255)
COLOR_BUTTON = (52, 152, 219)
COLOR_BUTTON_HOVER = (41, 128, 185)

GRAVITY = 0.4
FLAP_STRENGTH = -7
MAX_FALL_SPEED = 10
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY = 1500

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy J")
clock = pygame.time.Clock()

font_large = pygame.font.SysFont("Arial", 36, bold=True)
font_medium = pygame.font.SysFont("Arial", 24, bold=True)
font_small = pygame.font.SysFont("Arial", 18, bold=False)

STATE_START = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color

        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=10)

        text_surf = font_medium.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False


class Bird:
    def __init__(self):
        self.x = 80
        self.y = SCREEN_HEIGHT // 4
        self.radius = 16
        self.velocity = 0
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)


        self.image_loaded = False
        try:

            raw_image = pygame.image.load("bird.png").convert_alpha()

            self.image = pygame.transform.scale(raw_image, (self.radius * 3, self.radius * 3))
            self.image_loaded = True
        except (pygame.error, FileNotFoundError):
            print("tite")

    def update(self):
        self.velocity += GRAVITY
        if self.velocity > MAX_FALL_SPEED:
            self.velocity = MAX_FALL_SPEED

        self.y += self.velocity

        if self.y < self.radius:
            self.y = self.radius
            self.velocity = 0

        self.rect.topleft = (self.x - self.radius, self.y - self.radius)

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def draw(self, surface):
        if self.image_loaded:

            angle = max(-45, min(30, self.velocity * -5))
            rotated_image = pygame.transform.rotate(self.image, angle)


            new_rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(rotated_image, new_rect.topleft)
        else:

            pygame.draw.circle(surface, COLOR_BIRD, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 6), int(self.y - 4)), 5)
            pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 7), int(self.y - 4)), 2)
            pygame.draw.polygon(surface, (247, 131, 34), [
                (self.x + self.radius - 2, self.y - 3),
                (self.x + self.radius + 8, self.y),
                (self.x + self.radius - 2, self.y + 5)
            ])


class Pipe:
    def __init__(self, x):
        self.x = x
        self.top_height = random.randint(50, SCREEN_HEIGHT - PIPE_GAP - 120)
        self.bottom_top = self.top_height + PIPE_GAP
        self.width = 60
        self.passed = False

        self.top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        self.bottom_rect = pygame.Rect(self.x, self.bottom_top, self.width, SCREEN_HEIGHT - self.bottom_top - 50)

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_PIPE, self.top_rect)
        pygame.draw.rect(surface, COLOR_PIPE, self.bottom_rect)
        pygame.draw.rect(surface, (90, 155, 35), (self.x - 4, self.top_height - 20, self.width + 8, 20))
        pygame.draw.rect(surface, (90, 155, 35), (self.x - 4, self.bottom_top, self.width + 8, 20))


game_state = STATE_START
score = 0
high_score = 0
bird = Bird()
pipes = []
last_pipe_time = 0

start_button = Button(100, 340, 200, 50, "PLAY GAME", COLOR_BUTTON, COLOR_BUTTON_HOVER)
restart_button = Button(100, 360, 200, 50, "PLAY AGAIN", COLOR_BUTTON, COLOR_BUTTON_HOVER)


def reset_game():
    global bird, pipes, score, last_pipe_time
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH + 100)]
    score = 0
    last_pipe_time = pygame.time.get_ticks()


while True:
    dt = clock.tick(FPS)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state == STATE_START:
            if start_button.is_clicked(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                reset_game()
                game_state = STATE_PLAYING

        elif game_state == STATE_PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                bird.flap()

        elif game_state == STATE_GAME_OVER:
            if restart_button.is_clicked(event) or (
                    event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_r)):
                reset_game()
                game_state = STATE_PLAYING

    if game_state == STATE_PLAYING:
        bird.update()

        if current_time - last_pipe_time > PIPE_FREQUENCY:
            pipes.append(Pipe(SCREEN_WIDTH))
            last_pipe_time = current_time

        for pipe in pipes[:]:
            pipe.update()

            if not pipe.passed and pipe.x + pipe.width < bird.x:
                pipe.passed = True
                score += 1
                if score > high_score:
                    high_score = score

            if pipe.x + pipe.width < 0:
                pipes.remove(pipe)

        if bird.y + bird.radius >= SCREEN_HEIGHT - 50:
            game_state = STATE_GAME_OVER

        for pipe in pipes:
            if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                game_state = STATE_GAME_OVER

    screen.fill(COLOR_SKY)

    for pipe in pipes:
        pipe.draw(screen)

    pygame.draw.rect(screen, COLOR_GROUND, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    pygame.draw.line(screen, (115, 110, 75), (0, SCREEN_HEIGHT - 50), (SCREEN_WIDTH, SCREEN_HEIGHT - 50), 3)

    bird.draw(screen)

    if game_state == STATE_PLAYING:
        score_surface = font_large.render(str(score), True, COLOR_TEXT)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(score_surface, score_rect)

    elif game_state == STATE_START:
        title_surf = font_large.render("FLAPPY J", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 180))
        screen.blit(title_surf, title_rect)

        sub_surf = font_small.render("Click or press Space to fly", True, (80, 80, 80))
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 230))
        screen.blit(sub_surf, sub_rect)

        start_button.draw(screen)

    elif game_state == STATE_GAME_OVER:
        over_surf = font_large.render("GAME OVER", True, (200, 30, 30))
        over_rect = over_surf.get_rect(center=(SCREEN_WIDTH // 2, 160))
        screen.blit(over_surf, over_rect)

        card_rect = pygame.Rect(80, 210, 240, 120)
        pygame.draw.rect(screen, (255, 255, 255), card_rect, border_radius=12)
        pygame.draw.rect(screen, (200, 200, 200), card_rect, 2, border_radius=12)

        score_text = font_medium.render(f"Score: {score}", True, (50, 50, 50))
        high_text = font_medium.render(f"Best: {high_score}", True, (50, 50, 50))

        screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, 245)))
        screen.blit(high_text, high_text.get_rect(center=(SCREEN_WIDTH // 2, 290)))

        restart_button.draw(screen)

    pygame.display.flip()