from random import choice
from random import randint

import pygame
from pygame.math import Vector2 as vector

from settings import *
from timer import Timer


class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, group, z=LEVEL_LAYERS['main']):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z


class Block(Generic):
    def __init__(self, pos, size, group):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, group)


class Animated(Generic):
    def __init__(self, assets, pos, group, z=LEVEL_LAYERS['main']):
        self.animation_frames = assets
        self.frame_index = 0
        super().__init__(pos, self.animation_frames[self.frame_index], group, z)

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        self.frame_index = 0 if self.frame_index >= len(self.animation_frames) else self.frame_index
        self.image = self.animation_frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)


class Cloud(Generic):
    def __init__(self, pos, surf, group, left_limit):
        super().__init__(pos, surf, group, LEVEL_LAYERS['clouds'])
        self.left_limit = left_limit
        # movement
        self.pos = vector(self.rect.topleft)
        self.speed = randint(20, 30)

    def update(self, dt):
        self.pos.x -= self.speed * dt
        self.rect.x = round(self.pos.x)
        if self.rect.x <= self.left_limit:
            self.kill()


class Player(Generic):
    def __init__(self, pos, assets, particles, group, collision_sprites, attackable_sprites, hit_sound, jump_sound, attack_sounds):
        # 动画
        self.animation_frames = assets
        self.frame_index = 0  # 玩家动画帧索引
        self.status = 'idle'
        self.common_status_active = True
        self.orientation = 'right'
        surf = self.animation_frames[self.status][int(self.frame_index)]
        super().__init__(pos, surf, group)
        # 移动
        self.direction = vector()
        self.pos = vector(self.rect.center)
        self.speed = 400
        self.gravity = 5
        self.on_floor = False  # hitbox下一像素检测是否是地面
        # 碰撞
        self.collision_sprites = collision_sprites
        self.hitbox = self.rect.inflate(-95, -34)
        self.mask = pygame.mask.from_surface(self.image)
        # 攻击
        self.attackable_sprites = attackable_sprites
        self.dealt_damage_flag = False  # 为了保证一次攻击只造成一次伤害
        # 音效
        self.hit_sound = hit_sound
        self.jump_sound = jump_sound
        self.attack_sounds = attack_sounds
        # 粒子特效
        self.particles = particles
        # 组
        self.group = group
        # 单位属性
        self.base_damage = 5

    # 被击中
    def hit(self):
        self.hit_sound.play()
        self.direction.y = -1  # 飞起一段距离

    def common_status(self):
        if self.common_status_active:
            if self.direction.y < 0:
                self.status = 'jump'
            elif self.direction.y > 1:
                self.status = 'fall'
            elif self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'

    # 玩家动画
    def animate(self, dt):
        current_animation = self.animation_frames[self.status]
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if not PLAYER_ANIMATION_STATUS[self.status]['interruptible']:  # 不可打断的动画播放完毕重新开启common_status
                self.common_status_active = True

        self.image = current_animation[int(self.frame_index)] if self.orientation == 'right' else pygame.transform.flip(current_animation[int(self.frame_index)], True, False)
        self.mask = pygame.mask.from_surface(self.image)

    def input(self):
        keys = pygame.key.get_pressed()
        # 左右移动
        if keys[pygame.K_d]:
            self.direction.x = 1
            self.orientation = 'right'
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.orientation = 'left'
        else:
            self.direction.x = 0
        # 跳跃
        if keys[pygame.K_SPACE] and self.on_floor:
            self.direction.y = -2
            self.jump_sound.play()
            self.jump_dust_particles()

    def attack_0(self):
        if PLAYER_ANIMATION_STATUS[self.status]['interruptible']:
            self.dealt_damage_flag = False
            self.status = 'attack 0'
            self.frame_index = 0
            self.common_status_active = PLAYER_ANIMATION_STATUS[self.status]['interruptible']
            self.attack_sounds[0].play()

    def attack_1(self):
        if PLAYER_ANIMATION_STATUS[self.status]['interruptible']:
            self.dealt_damage_flag = False
            self.status = 'attack 1'
            self.frame_index = 0
            self.common_status_active = PLAYER_ANIMATION_STATUS[self.status]['interruptible']
            self.attack_sounds[1].play()

    def attack_2(self):
        if PLAYER_ANIMATION_STATUS[self.status]['interruptible']:
            self.dealt_damage_flag = False
            self.status = 'attack 2'
            self.frame_index = 0
            self.common_status_active = PLAYER_ANIMATION_STATUS[self.status]['interruptible']
            self.attack_sounds[2].play()

    def dealt_damage(self):
        status_type = self.status.split()
        if status_type[0] == 'attack' and int(self.frame_index) == 1:
            match status_type[1]:
                case '0':
                    size = (38, 20)
                    if self.orientation == 'right':
                        lefttop = (self.hitbox.right + 10, self.hitbox.top + 34)
                    else:
                        lefttop = (self.hitbox.left - size[0] - 10, self.hitbox.top + 34)
                case '1':
                    size = (28, 48)
                    if self.orientation == 'right':
                        lefttop = (self.hitbox.right + 10, self.hitbox.top + 16)
                    else:
                        lefttop = (self.hitbox.left - size[0] - 10, self.hitbox.top + 16)
                case '2':
                    size = (30, 52)
                    if self.orientation == 'right':
                        lefttop = (self.hitbox.right + 10, self.hitbox.top - 6)
                    else:
                        lefttop = (self.hitbox.left - size[0] - 10, self.hitbox.top - 6)
                case _:
                    size = (0, 0)
                    lefttop = (0, 0)
            detection_zone = pygame.Rect(lefttop, size)
            for sprite in self.attackable_sprites:
                if detection_zone.colliderect(sprite.hitbox):
                    sprite.hit(self.base_damage)
                    self.hit_sound.play()
            self.dealt_damage_flag = True

    # 跳跃灰尘特效
    def jump_dust_particles(self):
        JumpParticles(self.particles['jump_dust_particles'], self.rect.center, self.group)

    # 落地灰尘特效
    def fall_dust_particles(self):
        if self.on_floor and self.status == 'fall':
            FallParticles(self.particles['fall_dust_particles'], self.rect.center, self.group)

    def move(self, dt):
        # 水平
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        # 垂直
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def apply_gravity(self, dt):
        self.direction.y += self.gravity * dt
        self.rect.y += self.direction.y

    def check_on_floor(self):
        floor_rect = pygame.Rect(self.hitbox.bottomleft, (self.hitbox.width, 1))
        floor_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.colliderect(floor_rect)]
        self.on_floor = True if floor_sprites else False

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox):
                if direction == 'horizontal':
                    self.hitbox.right = sprite.rect.left if self.direction.x > 0 else self.hitbox.right
                    self.hitbox.left = sprite.rect.right if self.direction.x < 0 else self.hitbox.left
                    self.rect.centerx = self.hitbox.centerx
                    self.pos.x = self.hitbox.centerx
                else:  # vertical
                    self.hitbox.top = sprite.rect.bottom if self.direction.y < 0 else self.hitbox.top
                    self.hitbox.bottom = sprite.rect.top if self.direction.y > 0 else self.hitbox.bottom
                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.hitbox.centery
                    self.direction.y = 0

    def update(self, dt):
        self.input()
        self.apply_gravity(dt)
        self.move(dt)
        self.check_on_floor()
        self.fall_dust_particles()
        # 更新玩家一般状态
        if self.common_status_active:
            self.common_status()
        # 攻击造成伤害
        if self.status in ['attack 0', 'attack 1', 'attack 2'] and not self.dealt_damage_flag:
            self.dealt_damage()
        self.animate(dt)


class JumpParticles(Animated):
    def __init__(self, assets, pos, group):
        super().__init__(assets, pos, group)
        self.rect = self.image.get_rect(center=pos)

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.animation_frames):
            self.image = self.animation_frames[int(self.frame_index)]
        else:
            self.kill()


class FallParticles(Animated):
    def __init__(self, assets, pos, group):
        super().__init__(assets, pos, group)
        self.rect = self.image.get_rect(center=pos)

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.animation_frames):
            self.image = self.animation_frames[int(self.frame_index)]
        else:
            self.kill()


class Flag(Animated):
    def __init__(self, assets, pos, group):
        super().__init__(assets, pos, group)
        self.rect = self.image.get_rect(center=pos + vector(0, 18))
        self.mask = pygame.mask.from_surface(self.image)
        self.hitbox = self.mask.get_bounding_rects()[0]
        self.hitbox.center = self.rect.center


class Coin(Animated):
    def __init__(self, coin_type, assets, pos, group):
        super().__init__(assets, pos, group)
        self.rect = self.image.get_rect(center=pos)
        self.coin_type = coin_type


# 拾取金币粒子特效
class CoinParticles(Animated):
    def __init__(self, assets, pos, group):
        super().__init__(assets, pos, group)
        self.rect = self.image.get_rect(center=pos)

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.animation_frames):
            self.image = self.animation_frames[int(self.frame_index)]
        else:
            self.kill()


class Spikes(Generic):
    def __init__(self, surf, pos, group):
        super().__init__(pos, surf, group)
        self.mask = pygame.mask.from_surface(self.image)
        self.hitbox = self.mask.get_bounding_rects()[0]
        self.hitbox.midbottom = self.rect.midbottom


class Shell(Generic):
    def __init__(self, orientation, assets, pos, group, pearl_surf, damage_sprites):
        self.orientation = orientation
        self.animation_frames = assets.copy()
        if orientation == 'right':
            for key, value in self.animation_frames.items():
                self.animation_frames[key] = [pygame.transform.flip(surf, True, False) for surf in value]

        self.frame_index = 0
        self.status = 'idle'
        super().__init__(pos, self.animation_frames[self.status][self.frame_index], group)
        self.rect.bottom = self.rect.top + TILE_SIZE

        self.pearl_surf = pearl_surf
        self.has_shot = False
        self.attack_cooldown = Timer(2000)  # 攻击冷却时间
        self.damage_group = damage_sprites

    def animate(self, dt):
        current_animation = self.animation_frames[self.status]
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.has_shot:
                self.attack_cooldown.activate()
                self.has_shot = False
        self.image = current_animation[int(self.frame_index)]

        if int(self.frame_index) == 2 and self.status == 'attack' and not self.has_shot:
            pearl_direction = vector(-1, 0) if self.orientation == 'left' else vector(1, 0)
            offset = (pearl_direction * 50) + vector(0, -10) if self.orientation == 'left' else (pearl_direction * 20) + vector(0, -10)
            Pearl(self.rect.center + offset, pearl_direction, self.pearl_surf, [self.groups()[0], self.damage_group])
            self.has_shot = True

    def get_status(self):
        if vector(self.player.rect.center).distance_to(vector(self.rect.center)) < 500 and not self.attack_cooldown.active:
            self.status = 'attack'
        else:
            self.status = 'idle'

    def update(self, dt):
        self.get_status()
        self.animate(dt)
        self.attack_cooldown.update()


class Pearl(Generic):
    def __init__(self, pos, direction, surf, group):
        super().__init__(pos, surf, group)
        self.mask = pygame.mask.from_surface(self.image)
        self.hitbox = self.mask.get_bounding_rects()[0]
        # 移动
        self.pos = vector(self.rect.topleft)
        self.direction = direction
        self.speed = 150
        # 计时器
        self.timer = Timer(6000)
        self.timer.activate()

    def update(self, dt):
        # 移动
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        self.hitbox.center = self.rect.center
        # 计时器
        self.timer.update()
        if not self.timer.active:
            self.kill()
