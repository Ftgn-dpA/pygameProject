import sys

import pygame

from level_data import *
from sprites import *
from support import *
from tooth import Tooth
from crabby import Crabby
from pinkstar import Pinkstar


class Level:
    def __init__(self, grid, asset_dict, audio, change_coins, change_health, get_max_health, set_max_health, get_cur_health, set_cur_health, current_level, lose, create_overworld):

        self.display_surface = pygame.display.get_surface()

        # level setup
        self.current_level = current_level
        self.new_max_level = levels[self.current_level]['unlock']

        # groups
        self.all_sprites = CameraGroup()
        self.coin_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.shell_sprites = pygame.sprite.Group()
        self.crabby_sprites = pygame.sprite.Group()
        self.pinkstar_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # sounds
        self.bg_music = audio['music']
        self.bg_music.set_volume(0.01)
        self.bg_music.play(loops=-1)

        self.coin_sound = audio['coin']
        self.coin_sound.set_volume(0.3)

        self.hit_sound = audio['hit']
        self.hit_sound.set_volume(0.3)

        self.jump_sound = audio['jump']
        self.jump_sound.set_volume(0.3)

        self.build_level(
            grid=grid,
            asset_dict=asset_dict,
            hit_sound=self.hit_sound,
            jump_sound=self.jump_sound,
            attack_sounds=[audio[f'attack {i}'] for i in range(3)]
        )

        # level limits
        self.level_limits = {
            'left': min(grid['terrain'].keys(), key=lambda pos: pos[0])[0] - 1000,
            'right': max(grid['terrain'].keys(), key=lambda pos: pos[0])[0] + 500
        }

        # player particles
        self.dust_animation_speed = 0.15
        self.run_dust_frame_index = 0
        self.run_dust_particle_surfs = asset_dict['player particles']

        # additional stuff
        self.coin_particle_surfs = asset_dict['coin particle']
        self.cloud_surfs = asset_dict['clouds']
        self.cloud_timer = pygame.USEREVENT + 2
        pygame.time.set_timer(self.cloud_timer, 2000)  # 每2秒触发一次创建云事件
        self.startup_cloud()

        # timer
        self.invul_timer = Timer(500)

        # user interface
        self.change_coins = change_coins
        self.change_health = change_health

        self.get_max_health = get_max_health
        self.set_max_health = set_max_health
        self.get_cur_health = get_cur_health
        self.set_cur_health = set_cur_health
        self.lose = lose

        # switch
        self.create_overworld = create_overworld

    def build_level(self, grid, asset_dict, hit_sound, jump_sound, attack_sounds):
        for layer_name, layer in grid.items():
            for pos, data in layer.items():
                if layer_name == 'terrain':
                    Generic(pos, asset_dict['land'][data], [self.all_sprites, self.collision_sprites])
                if layer_name == 'water':
                    if data == 'top':
                        Animated(asset_dict['water top'], pos, self.all_sprites, LEVEL_LAYERS['water'])
                    else:
                        Generic(pos, asset_dict['water bottom'], self.all_sprites, LEVEL_LAYERS['water'])

                match data:
                    # player
                    case 0:
                        self.player = Player(
                            pos=pos,
                            assets=asset_dict['player'],
                            particles=asset_dict['player particles'],
                            group=self.all_sprites,
                            collision_sprites=self.collision_sprites,
                            attackable_sprites=self.attackable_sprites,
                            hit_sound=hit_sound,
                            jump_sound=jump_sound,
                            attack_sounds=attack_sounds
                        )
                    # sky
                    case 1:
                        self.horizon_y = pos[1]
                        self.all_sprites.horizon_y = pos[1]
                    # coins
                    case 4:
                        Coin('gold', asset_dict['gold'], pos, [self.all_sprites, self.coin_sprites])
                    case 5:
                        Coin('silver', asset_dict['silver'], pos, [self.all_sprites, self.coin_sprites])
                    case 6:
                        Coin('diamond', asset_dict['diamond'], pos, [self.all_sprites, self.coin_sprites])
                    # enemies
                    case 7:
                        Spikes(
                            surf=asset_dict['spikes'],
                            pos=pos,
                            group=[self.all_sprites, self.damage_sprites]
                        )
                    case 8:
                        Tooth(
                            assets=asset_dict['tooth'],
                            pos=pos,
                            group=[self.all_sprites, self.damage_sprites, self.attackable_sprites],
                            collision_sprites=self.collision_sprites
                        )
                    case 9:
                        Shell(
                            orientation='left',
                            assets=asset_dict['shell'],
                            pos=pos,
                            group=[self.all_sprites, self.collision_sprites, self.shell_sprites],
                            pearl_surf=asset_dict['pearl'],
                            damage_sprites=self.damage_sprites
                        )
                    case 10:
                        Shell(
                            orientation='right',
                            assets=asset_dict['shell'],
                            pos=pos,
                            group=[self.all_sprites, self.collision_sprites, self.shell_sprites],
                            pearl_surf=asset_dict['pearl'],
                            damage_sprites=self.damage_sprites
                        )
                    case 11:
                        Crabby(
                            assets=asset_dict['crabby'],
                            pos=pos,
                            group=[self.all_sprites, self.damage_sprites, self.attackable_sprites, self.crabby_sprites],
                            collision_sprites=self.collision_sprites
                        )
                    case 12:
                        Pinkstar(
                            assets=asset_dict['pinkstar'],
                            pos=pos,
                            group=[self.all_sprites, self.damage_sprites, self.attackable_sprites, self.pinkstar_sprites],
                            collision_sprites=self.collision_sprites
                        )
                    # palm trees fg
                    case 13:
                        Animated(asset_dict['palms']['small_fg'], pos, self.all_sprites)
                        Block(pos, (76, 50), self.collision_sprites)
                    case 14:
                        Animated(asset_dict['palms']['large_fg'], pos, self.all_sprites)
                        Block(pos, (76, 50), self.collision_sprites)
                    case 15:
                        Animated(asset_dict['palms']['left_fg'], pos, self.all_sprites)
                        Block(pos, (76, 50), self.collision_sprites)
                    case 16:
                        Animated(asset_dict['palms']['right_fg'], pos, self.all_sprites)
                        Block(pos + vector(50, 0), (76, 50), self.collision_sprites)
                    # palm trees bg
                    case 17:
                        Animated(asset_dict['palms']['small_bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])
                    case 18:
                        Animated(asset_dict['palms']['large_bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])
                    case 19:
                        Animated(asset_dict['palms']['left_bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])
                    case 20:
                        Animated(asset_dict['palms']['right_bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])
                    # flag
                    case 21:
                        self.flag = Flag(asset_dict['flag'], pos, self.all_sprites)

        for sprite in self.shell_sprites:  # 用于贝壳检测与玩家的距离
            sprite.player = self.player
        for sprite in self.crabby_sprites:
            sprite.player = self.player
        for sprite in self.pinkstar_sprites:
            sprite.player = self.player

    # 玩家移动灰尘特效
    def run_dust_particles(self, player):
        mid_pos = vector(590, 343)  # 玩家中心坐标
        offset = vector(18, 0)  # x轴偏移值
        if player.status == 'run' and player.on_floor:
            current_dust_particles = self.run_dust_particle_surfs[f'{player.status}_dust_particles']
            self.run_dust_frame_index += self.dust_animation_speed
            if self.run_dust_frame_index >= len(current_dust_particles):
                self.run_dust_frame_index = 0

            if player.orientation == 'right':
                frame = current_dust_particles[int(self.run_dust_frame_index)]
                self.display_surface.blit(frame, mid_pos - offset)
            else:
                frame = pygame.transform.flip(current_dust_particles[int(self.run_dust_frame_index)], True, False)
                self.display_surface.blit(frame, mid_pos + offset)

    # 拾取金币
    def get_coins(self):
        collided_coins = pygame.sprite.spritecollide(self.player, self.coin_sprites, True)
        for sprite in collided_coins:
            self.coin_sound.play()
            match sprite.coin_type:
                case 'gold':
                    self.change_coins(2)
                case 'silver':
                    self.change_coins(1)
                case 'diamond':
                    self.change_coins(10)
            CoinParticles(self.coin_particle_surfs, sprite.rect.center, self.all_sprites)  # 金币消失粒子特效

    # 受到伤害
    def get_damage(self):
        if not self.invul_timer.active:
            for sprite in self.damage_sprites:
                if self.player.hitbox.colliderect(sprite.hitbox):
                    self.change_health(10)
                    self.invul_timer.activate()
                    self.player.hit()
                    break
        # 受到伤害变白
        else:
            mask = pygame.mask.from_surface(self.player.image)
            surf = mask.to_surface()
            surf.set_colorkey('black')
            self.player.image = surf

    def check_win(self):
        if self.player.hitbox.colliderect(self.flag.hitbox):
            self.create_overworld(self.current_level, self.new_max_level)
            self.bg_music.stop()

    def check_lose(self):
        if self.get_cur_health() <= 0:
            self.lose()
            self.create_overworld(0, 0)
            self.bg_music.stop()

    def event_loop(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == self.cloud_timer:  # 创建云计时器事件
                surf = choice(self.cloud_surfs)
                surf = pygame.transform.scale2x(surf) if randint(0, 5) > 3 else surf
                x = self.level_limits['right'] + randint(100, 300)
                y = self.horizon_y - randint(100, 500)
                Cloud((x, y), surf, self.all_sprites, self.level_limits['left'])
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                if keys[pygame.K_w]:
                    self.player.attack_2()
                elif keys[pygame.K_a] or keys[pygame.K_d]:
                    self.player.attack_0()
                else:
                    self.player.attack_1()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.create_overworld(self.current_level, 0)
                    self.bg_music.stop()

    def startup_cloud(self):
        for _ in range(40):
            surf = choice(self.cloud_surfs)
            surf = pygame.transform.scale2x(surf) if randint(0, 5) > 3 else surf
            x = randint(self.level_limits['left'], self.level_limits['right'])
            y = self.horizon_y - randint(100, 500)
            Cloud((x, y), surf, self.all_sprites, self.level_limits['left'])

    def run(self, dt):
        # update
        self.event_loop()
        self.all_sprites.update(dt)
        self.check_win()
        self.check_lose()
        self.get_coins()
        self.get_damage()
        self.invul_timer.update()
        # drawing
        self.display_surface.fill(SKY_COLOR)
        self.all_sprites.custom_draw(self.player)
        self.run_dust_particles(self.player)


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()

    def draw_horizon(self):
        horizon_pos = self.horizon_y - self.offset.y

        if horizon_pos < WINDOW_HEIGHT:
            sea_rect = pygame.Rect(0, horizon_pos, WINDOW_WIDTH, WINDOW_HEIGHT - horizon_pos)
            pygame.draw.rect(self.display_surface, SEA_COLOR, sea_rect)

            horizon_rect1 = pygame.Rect(0, horizon_pos - 10, WINDOW_WIDTH, 10)
            horizon_rect2 = pygame.Rect(0, horizon_pos - 15, WINDOW_WIDTH, 5)
            horizon_rect3 = pygame.Rect(0, horizon_pos - 20, WINDOW_WIDTH, 2.5)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect1)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect2)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect3)
            pygame.draw.line(self.display_surface, HORIZON_COLOR, (0, horizon_pos), (WINDOW_WIDTH, horizon_pos))

        if horizon_pos < 0:
            self.display_surface.fill(SEA_COLOR)

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2
        self.offset.y = player.rect.centery - WINDOW_HEIGHT / 2

        for sprite in self:
            if sprite.z == LEVEL_LAYERS['clouds']:
                offset_rect = sprite.rect.copy()
                offset_rect.center -= self.offset
                self.display_surface.blit(sprite.image, offset_rect)

        self.draw_horizon()
        for sprite in self:
            for layer in LEVEL_LAYERS.values():
                if sprite.z == layer and sprite.z != LEVEL_LAYERS['clouds']:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
