import pickle

import pygame.mixer

from level import Level
from ui import UI
from overworld import Overworld
from settings import *
from support import *


class LevelLauncher:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # overworld
        self.max_level = INIT_MAX_LEVEL
        self.overworld = Overworld(0, self.max_level, self.display_surface, self.create_level)

        # assets
        self.imports()

        # 鼠标指针
        surf = pygame.image.load('../graphics/cursors/mouse.png').convert_alpha()
        cursor = pygame.cursors.Cursor((0, 0), surf)
        pygame.mouse.set_cursor(cursor)

        # 游戏界面状态
        self.status = GAME_STATUS['overworld']

        # 游戏参数
        self.max_health = INIT_MAX_HEALTH
        self.cur_health = INIT_CUR_HEALTH
        self.coins = INIT_COINS

        # user interface
        self.ui = UI(self.display_surface)

    def imports(self):  # 关卡资源导入
        # terrain
        self.land_tiles = import_folder_dict('../graphics/terrain/land')
        self.water_bottom = pygame.image.load('../graphics/terrain/water/water_bottom.png').convert_alpha()
        self.water_top_animation = import_folder('../graphics/terrain/water/animation')

        # coins
        self.gold = import_folder('../graphics/items/gold')
        self.silver = import_folder('../graphics/items/silver')
        self.diamond = import_folder('../graphics/items/diamond')
        self.coin_particle = import_folder('../graphics/items/particle')

        # palm trees
        self.palms = {folder: import_folder(f'../graphics/terrain/palm/{folder}') for folder in list(walk('../graphics/terrain/palm'))[0][1]}

        # enemies
        self.spikes = pygame.image.load('../graphics/enemies/spikes/spikes.png').convert_alpha()
        self.tooth = {folder: import_folder(f'../graphics/enemies/tooth/{folder}') for folder in list(walk('../graphics/enemies/tooth'))[0][1]}
        self.shell = {folder: import_folder(f'../graphics/enemies/shell_left/{folder}') for folder in list(walk('../graphics/enemies/shell_left'))[0][1]}
        self.pearl = pygame.image.load('../graphics/enemies/pearl/pearl.png').convert_alpha()
        self.crabby = {folder: import_folder(f'../graphics/enemies/crabby/{folder}') for folder in list(walk('../graphics/enemies/tooth'))[0][1]}

        # player
        self.player_graphics = {folder: import_folder2x(f'../graphics/player/{folder}') for folder in list(walk('../graphics/player'))[0][1]}

        # player particles
        self.player_particles = {folder: import_folder2x(f'../graphics/player_particles/{folder}') for folder in list(walk('../graphics/player_particles'))[0][1]}

        # flag
        self.flag = import_folder('../graphics/flag')

        # clouds
        self.clouds = import_folder('../graphics/clouds')

        # sounds
        self.level_sounds = {
            'coin': pygame.mixer.Sound('../audio/level/coin/coin.wav'),
            'hit': pygame.mixer.Sound('../audio/level/player/hit.wav'),
            'jump': pygame.mixer.Sound('../audio/level/player/jump.wav'),
            'attack 0': pygame.mixer.Sound('../audio/level/player/attack 0.mp3'),
            'attack 1': pygame.mixer.Sound('../audio/level/player/attack 1.mp3'),
            'attack 2': pygame.mixer.Sound('../audio/level/player/attack 2.mp3'),
            'music': pygame.mixer.Sound('../audio/level/SuperHero.ogg'),
        }

    def create_level(self, current_level):
        with open(f'../level_data/data{current_level}', 'rb') as data:
            grid = pickle.load(data)
        self.level = Level(
            grid,
            {
                'land': self.land_tiles,
                'water bottom': self.water_bottom,
                'water top': self.water_top_animation,
                'gold': self.gold,
                'silver': self.silver,
                'diamond': self.diamond,
                'coin particle': self.coin_particle,
                'palms': self.palms,
                'spikes': self.spikes,
                'tooth': self.tooth,
                'shell': self.shell,
                'player': self.player_graphics,
                'player particles': self.player_particles,
                'flag': self.flag,
                'pearl': self.pearl,
                'crabby': self.crabby,
                'clouds': self.clouds
            },
            self.level_sounds,
            self.change_coins,
            self.change_health,
            self.get_max_health,
            self.set_max_health,
            self.get_cur_health,
            self.set_cur_health,
            current_level,
            self.lose,
            self.create_overworld
        )
        self.status = current_level + 1

    def create_overworld(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, self.display_surface, self.create_level)
        self.status = GAME_STATUS['overworld']

    # 函数传递
    def change_coins(self, amount):
        self.coins += amount

    def get_max_health(self):
        return self.max_health

    def set_max_health(self):
        return self.max_health

    def get_cur_health(self):
        return self.cur_health

    def set_cur_health(self, health):
        self.cur_health = health

    def change_health(self, damage):
        self.cur_health -= damage

    def lose(self):
        self.max_level = INIT_MAX_LEVEL
        self.max_health = INIT_MAX_HEALTH
        self.cur_health = INIT_CUR_HEALTH
        self.coins = INIT_COINS

    def run(self):
        while True:
            if self.status == GAME_STATUS['overworld']:
                self.clock.tick(60)

                self.display_surface.fill('grey')
                self.overworld.run()
            else:
                dt = self.clock.tick() / 1000
                # 运行关卡逻辑
                self.level.run(dt)
                # 显示ui
                self.ui.show_health(self.cur_health, self.max_health)
                self.ui.show_coins(self.coins)

            # 更新画面
            pygame.display.update()


if __name__ == '__main__':
    Game = LevelLauncher()
    Game.run()
