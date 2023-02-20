import pickle

import pygame.mixer

from level import Level
from settings import *
from support import *


class LevelLauncher:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        with open('../level_data/data', 'rb') as data:
            grid = pickle.load(data)
        self.imports()

        self.level = Level(
            grid,
            {
                'land': self.land_tiles,
                'water bottom': self.water_bottom,
                'water top': self.water_top_animation,
                'gold': self.gold,
                'silver': self.silver,
                'diamond': self.diamond,
                'particle': self.particle,
                'palms': self.palms,
                'spikes': self.spikes,
                'tooth': self.tooth,
                'shell': self.shell,
                'player': self.player_graphics,
                'pearl': self.pearl,
                'clouds': self.clouds
            },
            self.level_sounds
        )

        # 鼠标指针
        surf = pygame.image.load('../graphics/cursors/mouse.png').convert_alpha()
        cursor = pygame.cursors.Cursor((0, 0), surf)
        pygame.mouse.set_cursor(cursor)

    def imports(self):  # 关卡资源导入
        # terrain
        self.land_tiles = import_folder_dict('../graphics/terrain/land')
        self.water_bottom = pygame.image.load('../graphics/terrain/water/water_bottom.png').convert_alpha()
        self.water_top_animation = import_folder('../graphics/terrain/water/animation')

        # coins
        self.gold = import_folder('../graphics/items/gold')
        self.silver = import_folder('../graphics/items/silver')
        self.diamond = import_folder('../graphics/items/diamond')
        self.particle = import_folder('../graphics/items/particle')

        # palm trees
        self.palms = {folder: import_folder(f'../graphics/terrain/palm/{folder}') for folder in list(walk('../graphics/terrain/palm'))[0][1]}

        # enemies
        self.spikes = pygame.image.load('../graphics/enemies/spikes/spikes.png').convert_alpha()
        self.tooth = {folder: import_folder(f'../graphics/enemies/tooth/{folder}') for folder in list(walk('../graphics/enemies/tooth'))[0][1]}
        self.shell = {folder: import_folder(f'../graphics/enemies/shell_left/{folder}') for folder in list(walk('../graphics/enemies/shell_left'))[0][1]}
        self.pearl = pygame.image.load('../graphics/enemies/pearl/pearl.png').convert_alpha()

        # player
        self.player_graphics = {folder: import_folder2x(f'../graphics/player/{folder}') for folder in list(walk('../graphics/player'))[0][1]}

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
            'music': pygame.mixer.Sound('../audio/level/SuperHero.ogg')
        }

    def run(self):
        while True:
            dt = self.clock.tick() / 1000

            self.level.run(dt)
            pygame.display.update()


if __name__ == '__main__':
    level = LevelLauncher()
    level.run()
