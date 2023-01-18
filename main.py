import pygame
import pyganim as pyganim
import pytmx
import csv
from random import choice

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
floor_sprite = pygame.sprite.Group()
all_collision = []
weapons = {}
weapon_attack = []

tile_images = {
    'spawn': ['40'],
    'weapons': ['39'],
    'npc': ['42'],
    'enemy': ['41', ['']],
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
    'attack': 2
}

player = None


# Группа инструментархных функций
def load_level(file):
    with open(file) as csvf:
        reader = csv.reader(csvf, delimiter=',')
        level_map = [i for i in reader]

    return level_map


def generate_level(level_decor, level_creatures, level):
    new_player = None
    for y in range(len(level_decor)):
        for x in range(len(level_decor[y])):
            if level_decor[y][x] in tile_images['collision_block']:
                brick = Brick(x, y, level)
                all_collision.append(brick)
            elif level_creatures[y][x] in tile_images['spawn']:
                new_player = Player(x, y)
            elif level_creatures[y][x] in tile_images['weapons']:
                weapons['sword'] = Sword(x, y, new_player)
            elif level_creatures[y][x] in tile_images['enemy']:
                Enemy(x, y, slime)
    Floor(level)
    return new_player


# Группа классов нужных для создания карты
class OpenMap(pygame.sprite.Sprite):
    def __init__(self, x, y, level):
        super().__init__(tiles_group, all_sprites)
        self.open_map = pytmx.load_pygame(f"maptiled/level_{level}.tmx")
        self.image = self.open_map.get_tile_image(x, y, 0)

        self.tile_size = self.open_map.tilewidth
        self.rect = self.image.get_rect().move(self.tile_size * x, self.tile_size * y)
        screen.blit(self.image, (self.tile_size * x, self.tile_size * y))


class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, level):
        super().__init__(collision_tiles_group, all_sprites, tiles_group)

        self.open_map = pytmx.load_pygame(f"maptiled/level_{level}.tmx")

        self.image = self.open_map.get_tile_image(x, y, 0)

        self.tile_size = self.open_map.tilewidth
        self.rect = self.image.get_rect().move(self.tile_size * x, self.tile_size * y)


class Floor(pygame.sprite.Sprite):
    def __init__(self, num):
        super().__init__(floor_sprite)
        self.image = pygame.image.load(f'maptiled\ground_{num}.png')
        self.rect = self.image.get_rect().move(0, 0)


# Класс, ответственный за отрисовку и функционал кнопок
class Button:
    """The class responsible for drawing and functionality of the buttons"""

    def __init__(self, x, y, image, scale):
        """initializer function"""
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


# класс ответственный за отрисовку стартового меню
class Menu:
    """the class responsible for drawing the start menu"""

    def __init__(self):
        """initializer function"""
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

    # функция запуска стартового меню
    def run(self):
        """start menu launch function"""
        run = True
        while run:
            screen.fill(self.MENU_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_value = True
                    run = False
            if self.play_btn.draw(screen):
                break
            if self.quit_btn.draw(screen):
                self.quit_value = True
                run = False
            screen.blit(player_image, self.player_img_rect)

            pygame.display.update()

    # функция возвращающая значение переменной выхода
    def get_quit_value(self):
        """a function that returns the value of an output variable"""
        return self.quit_value


# класс ответственный за отрисовку внутриигрового меню
class IngameMenu:
    """the class responsible for drawing the in-game menu"""

    def __init__(self):
        """initializer function"""
        self.screen_sizes = screen.get_size()

        self.TEXT_COLOR = (255, 255, 255)
        self.MENU_COLOR = (50, 50, 50)
        self.BTN_IMG_PTH = 'graphics/menu_buttons/'

        self.cont_btn_img = pygame.image.load(self.BTN_IMG_PTH +
                                              'continue_btn.png').convert_alpha()
        self.save_btn_img = pygame.image.load(self.BTN_IMG_PTH +
                                              'save_btn.png').convert_alpha()
        self.quit_btn_img = pygame.image.load(self.BTN_IMG_PTH +
                                              'quit_btn.png').convert_alpha()

        self.cont_btn = Button(self.screen_sizes[0] / 2 - 128,
                               125, self.cont_btn_img, 2)
        self.quit_btn = Button(self.screen_sizes[0] / 2 - 128,
                               250, self.quit_btn_img, 2)

        self.quit_value = False

        self.run()

    # функция запуска внутриигрового меню
    def run(self):
        """in-game menu launch function"""
        run = True
        while run:
            screen.fill(self.MENU_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_value = True
                    run = False
            if self.cont_btn.draw(screen):
                break
            if self.quit_btn.draw(screen):
                self.quit_value = True
                run = False

            pygame.display.update()

    # функция возвращающая значение переменной выхода
    def get_quit_value(self):
        """a function that returns the value of an output variable"""
        return self.quit_value


# класс ответственный за меню поражения
class GameOverMenu:
    """class responsible for game over menu"""

    def __init__(self):
        """initializer function"""
        self.screen_sizes = screen.get_size()

        self.TEXT_COLOR = (255, 255, 255)
        self.TEXT_FONT = pygame.font.Font(None, 100)
        self.GAME_OVER_MESSAGE = self.TEXT_FONT.render('GAME OVER',
                                                       True, self.TEXT_COLOR)
        self.MENU_COLOR = (50, 50, 50)
        self.BTN_IMG_PTH = 'graphics/menu_buttons/'
        self.quit_btn_img = pygame.image.load(self.BTN_IMG_PTH +
                                              'quit_btn.png').convert_alpha()
        self.quit_btn = Button(self.screen_sizes[0] / 2 - 128,
                               self.screen_sizes[1] / 1.5,
                               self.quit_btn_img, 2)

        self.quit_value = False

        self.run()

    # функция запуска меню поражения
    def run(self):
        """game-over menu launch function"""
        run = True
        while run:
            screen.fill(self.MENU_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_value = True
                    run = False
            if self.quit_btn.draw(screen):
                run = False
                pygame.quit()
                return
            screen.blit(self.GAME_OVER_MESSAGE, (self.screen_sizes[0] / 2 - 200, 100))
            pygame.display.update()

    # функция возвращающая значение переменной выхода
    def get_quit_value(self):
        """a function that returns the value of an output variable"""
        return self.quit_value


# класс ответственный за отрисовку меню конца игры
class GameEndMenu:
    """the class responsible for drawing the game end menu"""

    def __init__(self):
        """initializer function"""
        self.screen_sizes = screen.get_size()

        self.TEXT_COLOR = (255, 255, 255)
        self.TEXT_FONT = pygame.font.Font(None, 110)
        self.TEXT = self.TEXT_FONT.render('THE END',
                                          True, self.TEXT_COLOR)

        with open('data\\res.csv', 'r') as csvf:
            reader = csv.reader(csvf, delimiter=';')
            result = [i for i in reader]
        self.TEXT_RES = None
        result[0][1] = f'SCORE: {12 * 100 * choice([1, 2, 3, 8])}'

        for i in result:
            if i[0] == 'END':
                print('yes')
                self.TEXT_RES = self.TEXT_FONT.render(i[1],
                                                      True, self.TEXT_COLOR)

        self.MENU_COLOR = (50, 50, 50)
        self.BTN_IMG_PTH = 'graphics/menu_buttons/'

        self.quit_btn_img = pygame.image.load(self.BTN_IMG_PTH +
                                              'quit_btn.png').convert_alpha()

        self.quit_btn = Button(self.screen_sizes[0] / 2 - 150,
                               self.screen_sizes[1] / 1.5, self.quit_btn_img, 2)

        self.run()

    # функция запускающая меню конца игры
    def run(self):
        """function launching the game end menu"""
        run = True
        while run:
            screen.fill(self.MENU_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_value = True
                    run = False
            if self.quit_btn.draw(screen):
                pygame.quit()
                return
            screen.blit(self.TEXT, (self.screen_sizes[0] / 2 - 200, 100))
            screen.blit(self.TEXT_RES, (self.screen_sizes[0] / 2 - 200, 250))
            pygame.display.update()


# класс ответственный за меню загрузки
class LoadingMenu:
    """the class responsible for the loading menu"""

    def __init__(self):
        """initializer function"""
        self.LOADING_FONT = pygame.font.Font(None, 100)
        self.LOADING_TEXT = self.LOADING_FONT.render('LOADING...', True,
                                                     (255, 255, 255))

    # функция ответственная за запуск меню загрузки
    def run(self):
        """function launching the loading menu"""
        screen.fill(SCREEN_COLOR)
        screen.blit(self.LOADING_TEXT, (screen.get_width() // 2 - 150,
                                        screen.get_height() // 2 - 100))
        pygame.display.flip()


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

        self.speed = 6

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
        self.speed = 3

        self.attack_radius = 100
        self.move_radius = 200

        self.status = None

        self.can_attack = True
        self.attack_time = 0
        self.attack_cooldown = 500

        self.direction = pygame.math.Vector2()

    def update(self):
        if len(weapon_attack) > 0:
            if pygame.sprite.collide_rect(self, weapon_attack[0]):
                self.hp -= weapon_attack[0].damage
                if self.hp <= 0:
                    self.kill()
                weapon_attack.remove(weapons['sword'])

        if self.get_status() == 'attack':
            if pygame.sprite.collide_rect(self, player):
                if self.do_attack():
                    self.attack_time = pygame.time.get_ticks()
        elif self.get_status() == 'move':
            self.direction = self.get_player_distance(player)[1]
        else:
            self.direction = pygame.math.Vector2()

        self.rect.x += self.direction.x * self.speed
        self.collision_check('horizontal')
        self.rect.y += self.direction.y * self.speed
        self.collision_check('vertical')

    def do_attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.attack_time >= self.attack_cooldown:
            player.health -= self.attack
            return True
        return False

    def get_player_distance(self, obj):
        vec_enemy = pygame.math.Vector2(self.rect.center)
        vec_player = pygame.math.Vector2(obj.rect.center)

        distance = (vec_player - vec_enemy).magnitude()

        if distance > 0:
            direction = (vec_player - vec_enemy).normalize()
        else:
            direction = pygame.math.Vector2()

        return distance, direction

    def get_status(self):
        distance = self.get_player_distance(player)[0]

        if distance <= self.attack_radius:
            return 'attack'
        elif distance <= self.move_radius:
            return 'move'
        else:
            return 'No'

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


class Sword(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__(all_sprites, weapon_group)
        self.player = player
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
        if pygame.sprite.collide_rect(self, self.player):
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


# класс ответственный за хп-бар
class HP_bar:
    """class responsible for hp-bar"""

    def __init__(self):
        """initializer function"""
        self.TEXT_COLOR = (255, 255, 255)
        self.TEXT_FONT = pygame.font.Font(None, 35)
        self.HP_STR = self.TEXT_FONT.render('HP', True,
                                            self.TEXT_COLOR)

    # функция отрисовки хп-бара
    def health_bar(self, health):
        """HP bar drawing function"""
        pygame.draw.rect(screen, (255, 0, 0),
                         (40, 10, health * 4, 25))
        pygame.draw.rect(screen, (255, 255, 255),
                         (40, 10, 400, 25), 4)
        screen.blit(self.HP_STR, (5, 10))


# класс ответственный за уровень
class Level:
    """the class responsible for the level"""

    def __init__(self, player):
        """initializer function"""
        self.enemies = len(enemy_group)
        self.player = player
        self.surface = pygame.display.get_surface()

    # функция ответственная за запуск уровня
    def run(self):
        """function responsible for starting the level"""
        screen.fill((0, 0, 0))
        running = True
        camera = Camera()
        hp_bar = HP_bar()

        while running:
            clock.tick(FPS)
            screen.fill((104, 159, 56))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                key = pygame.key.get_pressed()

                if key[pygame.K_ESCAPE]:
                    menu = IngameMenu()
                    if menu.get_quit_value():
                        running = False

            camera.update(self.player)

            for sprite in all_sprites:
                camera.apply(sprite)
            for sprite in floor_sprite:
                camera.apply(sprite)

            floor_sprite.draw(screen)
            collision_tiles_group.draw(screen)
            player_group.draw(screen)
            enemy_group.draw(screen)
            weapon_group.draw(screen)
            # all_sprites.draw(screen)

            all_sprites.update()

            hp_bar.health_bar(self.player.get_hp_inf())
            if self.player.get_hp_inf() <= 0:
                GameOverMenu()
                break
            pygame.display.flip()

            if len(enemy_group) == 0:
                return 1
        pygame.quit()
        return 'end'


# функция ответственная за запуск уровней
def main():
    global player

    loading = LoadingMenu()
    loading.run()
    player = generate_level(load_level('maptiled\level_1_decor.csv'),
                            load_level('maptiled\level_1_creatures.csv'),
                            '1')
    level = Level(player)
    if level.run() == 'end':
        return
    loading.run()

    with open('data\\res.csv', 'w', encoding="utf8", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['1 level', '5 mobs kill'])

    for sprite in all_sprites:
        sprite.kill()
    for sprite in floor_sprite:
        sprite.kill()

    del player
    del level

    player = generate_level(load_level('maptiled\level_2_decor.csv'),
                            load_level('maptiled\level_2_creatures.csv'),
                            '2')
    level = Level(player)
    if level.run() == 'end':
        return

    loading.run()

    with open('data\\res.csv', 'w+') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['2 level', '6 mobs kill'])

    for sprite in all_sprites:
        sprite.kill()
    for sprite in floor_sprite:
        sprite.kill()

    del player
    del level

    with open('data\\res.csv', 'w', encoding="utf8", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['END', '12 mobs kill'])

    GameEndMenu()


if __name__ == '__main__':
    pygame.init()
    clock = pygame.time.Clock()
    menu = Menu()
    if menu.get_quit_value():
        pygame.quit()
    else:
        main()
