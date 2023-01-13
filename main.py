import pygame
import pyganim as pyganim
import pytmx
import csv

pygame.init()
clock = pygame.time.Clock()

SIZE = WIDTH, HEIGHT = 1024, 658
FPS = 60
TILE_SIZE = 64
SCREEN_COLOR = pygame.Color('black')

# Аниманция персонажа

PLAYER_ANIMATION_DELAY = 150  # скорость смены кадров
PLAYER_ANIMATION_DOWN = [
    'graphics/player/player_down.png',
    'graphics/player/player_walk_down_l.png',
    'graphics/player/player_walk_down_r.png'
]
PLAYER_ANIMATION_UP = [
    'graphics/player/player_up.png',
    'graphics/player/player_walk_up_r.png',
    'graphics/player/player_walk_up_l.png'
]
PLAYER_ANIMATION_RIGHT = [
    'graphics/player/player_right.png',
    'graphics/player/player_walk_right_r.png',
    'graphics/player/player_walk_right_l.png'
]
PLAYER_ANIMATION_LEFT = [
    'graphics/player/player_left.png',
    'graphics/player/player_walk_left_r.png',
    'graphics/player/player_walk_left_l.png'
]
PLAYER_ANIMATION_STAY = [('graphics/player/player_down.png', 2)]

# Анимация оружия

SWORD_ATTACK_ANIMATION = [
    'graphics\weapons\sword_up.png',
    'graphics\weapons\sword_right_up.png',
    'graphics\weapons\sword_right_down.png',
    'graphics\weapons\sword_down.png',
    'graphics\weapons\sword_left_up.png',
    'graphics\weapons\sword_left_down.png',
]

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
# screen = pygame.display.set_mode(SIZE)

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
collision_tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
weapon_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

all_collision = []
weapons = {}
weapon_attack = []

tile_images = {
    'spawn': ['40'],
    'weapons': ['39'],
    'npc': ['42'],
    'enemy': ['41'],
    'grass': ['3'],
    'collision_block': ['4', '5', '6', '7', '8', '9', '10', '11', '12', '16',
                        '17', '18', '19', '20', '21', '22', '23', '24', '25',
                        '29', '31', '32', '33', '34', '35', '36', '37', '38']
}

enemy_images = {
    'slime': 'graphics\enemy\slime.png'
}

weapons_images = {
    'sword': 'graphics\weapons\sword.png'
}

player_image = pygame.image.load('graphics/player/player_down.png')  # Изображение героя

# Enemies
slime = {
    'image': enemy_images['slime'],
    'hp': 10,
    'attack': 1
}


# Группа инструментархных функций
def load_level(file):
    with open(file) as csvf:
        reader = csv.reader(csvf, delimiter=',')
        level_map = [i for i in reader]

    return level_map


def generate_level(level_decor, level_creatures):
    new_player = None
    for y in range(len(level_decor)):
        for x in range(len(level_decor[y])):
            if level_decor[y][x] in tile_images['collision_block']:
                brick = Brick(x, y)
                all_collision.append(brick)
            else:
                OpenMap(x, y)

    for y in range(len(level_creatures)):
        for x in range(len(level_creatures[y])):
            if level_creatures[y][x] in tile_images['spawn']:
                new_player = Player(x, y)
            elif level_creatures[y][x] in tile_images['weapons']:
                weapons['sword'] = Sword(x, y)
                print(weapons)
            elif level_creatures[y][x] in tile_images['enemy']:
                Enemy(x, y, slime)
    return new_player


# Группа классов нужных для создания карты
class OpenMap(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(tiles_group, all_sprites)
        self.open_map = pytmx.load_pygame("maptiled/level.tmx")
        self.image = self.open_map.get_tile_image(x, y, 0)

        self.tile_size = self.open_map.tilewidth
        self.rect = self.image.get_rect().move(self.tile_size * x, self.tile_size * y)
        screen.blit(self.image, (self.tile_size * x, self.tile_size * y))


class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(collision_tiles_group, all_sprites, tiles_group)

        self.open_map = pytmx.load_pygame("maptiled/level.tmx")

        self.image = self.open_map.get_tile_image(x, y, 0)

        self.tile_size = self.open_map.tilewidth
        self.rect = self.image.get_rect().move(self.tile_size * x, self.tile_size * y)


# Класс меню
class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.screen_sizes = screen.get_size()

        self.TEXT_COLOR = (255, 255, 255)
        self.MENU_COLOR = (50, 50, 50)
        self.BTN_IMG_PTH = 'graphics/menu_buttons/'

        self.play_btn_img = pygame.image.load(self.BTN_IMG_PTH +
                                              'play_btn.png').convert_alpha()
        self.quit_btn_img = pygame.image.load(self.BTN_IMG_PTH +
                                              'quit_btn.png').convert_alpha()

        self.play_btn = Button(self.screen_sizes[0] / 2 - 128,
                               125, self.play_btn_img, 2)
        self.quit_btn = Button(self.screen_sizes[0] / 2 - 128,
                               250, self.quit_btn_img, 2)

        self.quit_value = False

        self.player_img_rect = player_image.get_rect(
            center=(self.screen_sizes[0] // 2, self.screen_sizes[1] // 1.5))

        self.run()

    def run(self):
        run = True
        while run:
            self.screen.fill(self.MENU_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_value = True
                    run = False
            if self.play_btn.draw(self.screen):
                break
            if self.quit_btn.draw(self.screen):
                self.quit_value = True
                run = False
            self.screen.blit(player_image, self.player_img_rect)

            pygame.display.update()

    def get_quit_value(self):
        return self.quit_value


class IngameMenu:
    def __init__(self, screen):
        self.screen = screen
        self.screen_sizes = screen.get_size()

        self.TEXT_COLOR = (255, 255, 255)
        self.MENU_COLOR = (50, 50, 50)
        self.BTN_IMG_PTH = 'graphics/menu_buttons/'

        self.cont_btn_img = pygame.image.load(self.BTN_IMG_PTH +
                                              'continue_btn.png').convert_alpha()
        self.save_btn_img = pygame.image.load(self.BTN_IMG_PTH +
                                              'save_btn.png').convert_alpha()
        self.settings_btn_img = pygame.image.load(self.BTN_IMG_PTH +
                                                  'settings_btn.png').convert_alpha()
        self.quit_btn_img = pygame.image.load(self.BTN_IMG_PTH +
                                              'quit_btn.png').convert_alpha()

        self.cont_btn = Button(self.screen_sizes[0] / 2 - 128,
                               125, self.cont_btn_img, 2)
        self.save_btn = Button(self.screen_sizes[0] / 2 - 128,
                               250, self.save_btn_img, 2)
        self.settings_btn = Button(self.screen_sizes[0] / 2 - 128,
                                   375, self.settings_btn_img, 2)
        self.quit_btn = Button(self.screen_sizes[0] / 2 - 128,
                               500, self.quit_btn_img, 2)

        self.quit_value = False

        self.run()

    def run(self):
        run = True
        while run:
            self.screen.fill(self.MENU_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_value = True
                    run = False
            if self.cont_btn.draw(self.screen):
                break
            if self.save_btn.draw(self.screen):
                pass
            if self.settings_btn.draw(self.screen):
                run_menu = True
                while run_menu:
                    settings_menu = SettingsMenu(self.screen)
                    if settings_menu.get_quit_value():
                        run_menu = False
            if self.quit_btn.draw(self.screen):
                self.quit_value = True
                run = False

            pygame.display.update()

    def get_quit_value(self):
        return self.quit_value


class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.screen_sizes = screen.get_size()

        self.TEXT_COLOR = (255, 255, 255)
        self.MENU_COLOR = (50, 50, 50)
        self.BTN_IMG_PTH = 'graphics/menu_buttons/'

        self.size_btn_img = pygame.image.load(self.BTN_IMG_PTH + 'size_btn.png').convert_alpha()
        self.volume_btn_img = pygame.image.load(self.BTN_IMG_PTH + 'volume_btn.png').convert_alpha()
        self.quit_btn_img = pygame.image.load(self.BTN_IMG_PTH + 'quit_btn.png').convert_alpha()

        self.size_btn = Button(self.screen_sizes[0] / 2 - 128,
                               375, self.size_btn_img, 2)
        self.volume_btn = Button(self.screen_sizes[0] / 2 - 128,
                                 250, self.volume_btn_img, 2)
        self.quit_btn_sett = Button(self.screen_sizes[0] / 2 - 128,
                                    125, self.quit_btn_img, 2)

        self.quit_value = False
        self.run()

    def run(self):
        run = True
        while run:
            self.screen.fill(self.MENU_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            if self.size_btn.draw(self.screen):
                # вставить функцию для изменения размера окна
                pass
            if self.volume_btn.draw(self.screen):
                # вставить функцию для звука
                pass
            if self.quit_btn_sett.draw(self.screen):
                self.quit_value = True
                return
            pygame.display.update()

    def get_quit_value(self):
        return self.quit_value


class GameOverMenu:
    def __init__(self, screen):
        self.screen = screen
        self.screen_sizes = screen.get_size()

        self.TEXT_COLOR = (255, 255, 255)
        self.TEXT_FONT = pygame.font.Font(None, 100)
        self.GAME_OVER_MESSAGE = self.TEXT_FONT.render('GAME OVER',
                                                       True, self.TEXT_COLOR)
        self.MENU_COLOR = (50, 50, 50)
        self.BTN_IMG_PTH = 'graphics/menu_buttons/'

        self.last_save_img = pygame.image.load(self.BTN_IMG_PTH +
                                               'last_save_btn.png').convert_alpha()
        self.quit_btn_img = pygame.image.load(self.BTN_IMG_PTH +
                                              'quit_btn.png').convert_alpha()

        self.last_save_btn = Button(self.screen_sizes[0] / 2 - 128, 256, self.last_save_img, 2)
        self.quit_btn = Button(self.screen_sizes[0] / 2 - 128, 384, self.quit_btn_img, 2)

        self.quit_value = False

        self.run()

    def run(self):
        run = True
        while run:
            self.screen.fill(self.MENU_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_value = True
                    run = False
            if self.last_save_btn.draw(self.screen):
                pass
            if self.quit_btn.draw(self.screen):
                self.quit_value = True
                run = False
            screen.blit(self.GAME_OVER_MESSAGE, (self.screen_sizes[0] / 2 - 200, 100))
            pygame.display.update()

    def get_quit_value(self):
        return self.quit_value


# Основа пока что
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)

        self.image = player_image.convert_alpha()
        self.color_alpha = (1, 1, 1)
        self.image.set_colorkey(self.color_alpha)
        self.rect = self.image.get_rect().move(
            TILE_SIZE * pos_x, TILE_SIZE * pos_y)

        self.pos_x = pos_x
        self.pos_y = pos_y

        self.health = 100

        self.attack_time = 0

        self.speed = 4

        self.smackthat = True

        self.direction = pygame.math.Vector2()

        self.boltAnimStay = pyganim.PygAnimation(PLAYER_ANIMATION_STAY)
        self.boltAnimStay.play()
        self.boltAnimStay.blit(self.image, (0, 0))

        # Анимация движения вправо
        botAnim = []
        for anim in PLAYER_ANIMATION_RIGHT:
            botAnim.append((anim, PLAYER_ANIMATION_DELAY))
        self.boltAnimRight = pyganim.PygAnimation(botAnim)
        self.boltAnimRight.play()
        # Анимация движения влево
        botAnim = []
        for anim in PLAYER_ANIMATION_LEFT:
            botAnim.append((anim, PLAYER_ANIMATION_DELAY))
        self.boltAnimLeft = pyganim.PygAnimation(botAnim)
        self.boltAnimLeft.play()
        # Анимация движения вверх
        botAnim = []
        for anim in PLAYER_ANIMATION_UP:
            botAnim.append((anim, PLAYER_ANIMATION_DELAY))
        self.boltAnimUp = pyganim.PygAnimation(botAnim)
        self.boltAnimUp.play()
        # Анимация движения вниз
        botAnim = []
        for anim in PLAYER_ANIMATION_DOWN:
            botAnim.append((anim, PLAYER_ANIMATION_DELAY))
        self.boltAnimDown = pyganim.PygAnimation(botAnim)
        self.boltAnimDown.play()

    def update(self):
        key = pygame.key.get_pressed()

        # Движение
        if key[pygame.K_LEFT] or key[pygame.K_a]:
            self.direction.x = -1
            self.image.fill(self.color_alpha)
            self.boltAnimLeft.blit(self.image, (0, 0))
        elif key[pygame.K_RIGHT] or key[pygame.K_d]:
            self.direction.x = 1
            self.image.fill(self.color_alpha)
            self.boltAnimRight.blit(self.image, (0, 0))
        else:
            self.direction.x = 0
            self.image.fill(self.color_alpha)
            self.boltAnimStay.blit(self.image, (0, 0))

        if key[pygame.K_DOWN] or key[pygame.K_s]:
            self.direction.y = 1
            self.image.fill(self.color_alpha)
            self.boltAnimDown.blit(self.image, (0, 0))
        elif key[pygame.K_UP] or key[pygame.K_w]:
            self.direction.y = -1
            self.image.fill(self.color_alpha)
            self.boltAnimUp.blit(self.image, (0, 0))
        else:
            self.direction.y = 0

        if key[pygame.K_SPACE]:
            self.attack('sword')
            self.attack_time = pygame.time.get_ticks()

        if pygame.sprite.collide_rect(self, weapons['sword']):
            weapons['sword'].rect = self.image.get_rect().move(self.rect.x, self.rect.y)
            if self.smackthat:
                NEW_ANIMATION_UP = [
                    'graphics/player/player_up_weapon.png',
                    'graphics/player/player_walk_up_r_weapon.png',
                    'graphics/player/player_walk_up_l_weapon.png'
                ]
                botAnim = [(anim, PLAYER_ANIMATION_DELAY) for anim in NEW_ANIMATION_UP]
                self.boltAnimUp = pyganim.PygAnimation(botAnim)
                self.boltAnimUp.play()
                self.smackthat = False

        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.rect.x += self.direction.x * self.speed
        self.collision_check('horizontal')
        self.rect.y += self.direction.y * self.speed
        self.collision_check('vertical')

    def collision_check(self, direct):
        if direct == 'horizontal':
            for sprite in all_collision:
                if pygame.sprite.collide_rect(self, sprite):
                    if self.direction.x > 0:
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.rect.left = sprite.rect.right

        if direct == 'vertical':
            for sprite in all_collision:
                if pygame.sprite.collide_rect(self, sprite):
                    if self.direction.y > 0:
                        self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.rect.top = sprite.rect.bottom

    def attack(self, weapon):
        current_time = pygame.time.get_ticks()
        if current_time - self.attack_time >= weapons[f'{weapon}'].attack_delay:
            weapon_attack.append(weapons[f'{weapon}'])
            weapons[f'{weapon}'].attack()

    def get_hp_inf(self):
        return self.health


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_info):
        super().__init__(all_sprites, enemy_group)

        self.image = pygame.image.load(enemy_info['image']).convert_alpha()
        self.rect = self.image.get_rect().move(TILE_SIZE * x, TILE_SIZE * y)

        self.hp = enemy_info['hp']
        self.attack = enemy_info['attack']

        self.attacking = False

    def update(self):
        if len(weapon_attack) > 0:
            if pygame.sprite.collide_rect(self, weapon_attack[0]):
                self.hp -= weapon_attack[0].damage
                if self.hp <= 0:
                    self.kill()
                weapon_attack.remove(weapons['sword'])


class Sword(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, weapon_group)
        self.image = pygame.image.load(weapons_images['sword'])
        self.rect = self.image.get_rect().move(TILE_SIZE * x, TILE_SIZE * y)

        self.damage = 5
        self.attack_delay = 400

        botAnim = []
        for anim in SWORD_ATTACK_ANIMATION:
            botAnim.append((anim, 100))
        self.boltAnimAttack = pyganim.PygAnimation(botAnim)
        self.boltAnimAttack.play()

    def update(self):
        if pygame.sprite.collide_rect(self, player):
            self.image.set_colorkey((255, 255, 255))
            self.image.fill((255, 255, 255))

    def attack(self):
        self.boltAnimAttack.blit(self.image, (0, 0))


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def health_bar(health):
    pygame.draw.rect(screen, (255, 0, 0),
                     (10, 10, health * 4, 25))
    pygame.draw.rect(screen, (255, 255, 255),
                     (10, 10, 400, 25), 4)


player = generate_level(load_level('maptiled\level_1_decor.csv'), load_level('maptiled\level_1_creatures.csv'))


def main():
    screen.fill((0, 0, 0))
    running = True
    camera = Camera()

    while running:
        clock.tick(FPS)
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            key = pygame.key.get_pressed()

            if key[pygame.K_ESCAPE]:
                menu = IngameMenu(screen)
                if menu.get_quit_value():
                    running = False

        camera.update(player)

        for sprite in all_sprites:
            camera.apply(sprite)

        all_sprites.update()

        all_sprites.draw(screen)
        tiles_group.draw(screen)
        enemy_group.draw(screen)

        player_group.draw(screen)
        weapon_group.draw(screen)
        health_bar(player.get_hp_inf())

        pygame.display.flip()


if __name__ == '__main__':
    menu = Menu(screen)
    if menu.get_quit_value():
        pygame.quit()
    else:
        main()
