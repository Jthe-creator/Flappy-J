import pygame
import random
import sys


pygame.init()


SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60


COLOR_SKY = (113, 197, 207)
COLOR_BIRD = (247, 212, 34)
COLOR_PIPE = (115, 191, 46)
COLOR_GROUND = (222, 216, 149)
COLOR_TEXT = (255, 255, 255)


GRAVITY = 0.4
FLAP_STRENGTH = -7
MAX_FALL_SPEED = 10
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY = 1500


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy J")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32, bold=True)


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


def reset_game():
    global bird, pipes, score, game_over, last_pipe_time
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH + 100)]
    score = 0
    game_over = False
    last_pipe_time = pygame.time.get_ticks()



reset_game()


while True:
    dt = clock.tick(FPS)
    current_time = pygame.time.get_ticks()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


        if event.type == pygame.MOUSEBUTTONDOWN:
            if not game_over:
                bird.flap()
            else:
                reset_game()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE and not game_over:
                bird.flap()
            if event.key == pygame.K_r and game_over:
                reset_game()

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    if not game_over:

        bird.update()


        if current_time - last_pipe_time > PIPE_FREQUENCY:
            pipes.append(Pipe(SCREEN_WIDTH))
            last_pipe_time = current_time

        for pipe in pipes[:]:
            pipe.update()

            if not pipe.passed and pipe.x + pipe.width < bird.x:
                pipe.passed = True
                score += 1

            if pipe.x + pipe.width < 0:
                pipes.remove(pipe)

        if bird.y + bird.radius >= SCREEN_HEIGHT - 50:
            game_over = True

        for pipe in pipes:
            if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                game_over = True

    screen.fill(COLOR_SKY)

    for pipe in pipes:
        pipe.draw(screen)

    pygame.draw.rect(screen, COLOR_GROUND, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    pygame.draw.line(screen, (115, 110, 75), (0, SCREEN_HEIGHT - 50), (SCREEN_WIDTH, SCREEN_HEIGHT - 50), 3)

    bird.draw(screen)

    score_surface = font.render(str(score), True, COLOR_TEXT)
    score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))
    screen.blit(score_surface, score_rect)

    if game_over:
        over_surface = font.render("GAME OVER", True, (200, 30, 30))
        over_rect = over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))

        retry_font = pygame.font.SysFont("Arial", 20, bold=False)
        retry_surface = retry_font.render("Tap Screen to Restart", True, (50, 50, 50))
        retry_rect = retry_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 15))

        screen.blit(over_surface, over_rect)
        screen.blit(retry_surface, retry_rect)

    pygame.display.flip()
