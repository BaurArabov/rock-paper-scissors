import pygame
from enum import Enum
import itertools
import random
import pygame.mixer

class ItemType(Enum):
    PAPER = "./paper.png"
    SCISSORS = "./scissors.png"
    ROCK = "./rock.png"


pygame.mixer.init()
rock_sound = pygame.mixer.Sound("rock.wav")
paper_sound = pygame.mixer.Sound("paper.wav")
scissors_sound = pygame.mixer.Sound("scissors.wav")
winning_sound = pygame.mixer.Sound("congrats.wav")

class Window():
    def __init__(self, width, heigth):
        self.width = width
        self.heigth = heigth
        self.left = 0
        self.right = width
        self.top = 0
        self.bot = heigth

class Item(pygame.sprite.Sprite):
    def __init__(self, type: ItemType, start_pos, velocity, start_dir, width=70):
        super().__init__()
        self.type = type
        self.pos = pygame.math.Vector2(start_pos)
        self.velocity = velocity
        self.dir = pygame.math.Vector2(start_dir).normalize()
        self.image = pygame.transform.scale(pygame.image.load(self.type.value).convert_alpha(), (width, width))
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
        self.radius = width / 2
        self.width = width

    def reflect(self, normal_vector):
        self.dir = self.dir.reflect(pygame.math.Vector2(normal_vector))

    def load_image(self):
        self.image = pygame.transform.scale(
            pygame.image.load(self.type.value).convert_alpha(), (self.width, self.width))

    def update(self):
        self.pos += self.dir * self.velocity
        self.rect.center = round(self.pos.x), round(self.pos.y)

    def item_win(self, other):
        if self.type == ItemType.PAPER:
            if other.type == ItemType.SCISSORS:
                self.type = ItemType.SCISSORS
                self.load_image()
                scissors_sound.play()
        elif self.type == ItemType.SCISSORS:
            if other.type == ItemType.ROCK:
                self.type = ItemType.ROCK
                self.load_image()
                rock_sound.play()
        elif self.type == ItemType.ROCK:
            if other.type == ItemType.PAPER:
                self.type = ItemType.PAPER
                self.load_image()
                paper_sound.play()

    def reflect_collided(self, window_size: Window):
        if self.rect.left <= window_size.left:
            self.reflect((1, 0))
        if self.rect.right >= window_size.right:
            self.reflect((-1, 0))
        if self.rect.top <= window_size.top:
            self.reflect((0, 1))
        if self.rect.bottom >= window_size.bot:
            self.reflect((0, -1))

def handle_collisions(all_groups, window_size: Window):
    for sprite in all_groups:
        sprite.reflect_collided(window_size)

        for other_sprite in all_groups:
            if sprite != other_sprite:
                if sprite.rect.colliderect(other_sprite.rect):
                    sprite.item_win(other_sprite)
                    sprite.reflect(pygame.math.Vector2(1, 1))

def main():
    ws = Window(800, 800)
    pygame.init()
    window = pygame.display.set_mode((ws.width, ws.heigth))
    screen = pygame.display.get_surface()
    frame = pygame.time.Clock()

    all_groups = pygame.sprite.Group()

    for i in range(random.randint(1, 5)):
        x = random.randint(200, 400)
        y = random.randint(100, 300)
        stone = Item(ItemType.ROCK, (x, y), 5, (random.random(), random.random()))
        all_groups.add(stone)

    for i in range(random.randint(1, 5)):
        x = random.randint(500, 700)
        y = random.randint(500, 700)
        scissor = Item(ItemType.SCISSORS, (x, y), 5, (random.random(), random.random()))
        all_groups.add(scissor)

    for i in range(random.randint(1, 5)):
        x = random.randint(100, 300)
        y = random.randint(500, 700)
        paper = Item(ItemType.PAPER, (x, y), 5, (random.random(), random.random()))
        all_groups.add(paper)

    while True:
        frame.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        all_groups.update()

        window.fill((255, 255, 255))
        all_groups.draw(window)

        handle_collisions(all_groups, ws)

        for a, b in itertools.combinations(all_groups, 2):
            if a.pos.distance_to(b.pos) < a.radius + b.radius - 2:
                a.item_win(b)

        if all(sprite.type.name == all_groups.sprites()[0].type.name for sprite in all_groups):
            winner = all_groups.sprites()[0].type.name

            screen.fill((255, 255, 255))

            font = pygame.font.SysFont(None, 48)
            text = font.render(winner + " won!", True, (0, 0, 0))
            screen.blit(text, (ws.width / 2 - text.get_width() / 2, ws.heigth / 2 - text.get_height() / 2))
            winner_image = pygame.image.load(winner + ".png")
            winner_image = pygame.transform.scale(winner_image, (200, 200))
            screen.blit(winner_image,
                        (ws.width / 2 - winner_image.get_width() / 2, ws.heigth / 2 + text.get_height() / 2 + 10))
            winning_sound.play()
            pygame.display.flip()

        pygame.display.flip()

main()
