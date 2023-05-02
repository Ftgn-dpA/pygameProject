import sprites
import pygame

from random import choice
from pygame.math import Vector2 as vector
from settings import *
from timer import Timer


class Tooth(sprites.Generic):
    def __init__(self, assets, pos, group, collision_sprites):
        # 通用设置
        self.animation_frames = assets
        self.frame_index = 0
        self.default_status = 'run'
        self.status = 'run'
        self.orientation = 'left'
        surf = self.animation_frames[self.status][int(self.frame_index)]
        super().__init__(pos, surf, group)
        self.rect.bottom = self.rect.top + TILE_SIZE
        self.mask = pygame.mask.from_surface(self.image)
        self.hitbox = self.mask.get_bounding_rects()[0]
        # 计时器
        self.hit_timer = Timer(200)
        self.dead_ground_timer = Timer(duration=3000, action=self.kill)
        # 声音
        self.hit_sound = pygame.mixer.Sound('../audio/level/tooth/hit.mp3')
        # 移动
        self.direction = vector(choice((1, -1)), 0)
        self.orientation = 'left' if self.direction.x < 0 else 'right'
        self.pos = vector(self.rect.topleft)
        self.speed = 120
        self.collision_sprites = collision_sprites
        # 单位属性
        self.health = 10
        self.is_dead = False
        # 组
        self.damage_sprites = group[1]
        self.attackable_sprites = group[2]
        # 删除不在地面的tooth
        if not [sprite for sprite in collision_sprites if sprite.rect.collidepoint(self.rect.midbottom + vector(0, 10))]:
            self.kill()

    def animate(self, dt):
        current_animation = self.animation_frames[self.status]
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            # 一次性动画，播放结束切换状态
            if TOOTH_ANIMATION_STATUS[self.status]['times'] == 'once':
                if self.status == 'dead hit':  # 死亡（打击）动画结束，转换状态为死亡（地面）
                    self.dead_ground()
                elif self.status == 'hit':
                    self.frame_index = 0
                    self.status = self.default_status
                else:
                    self.frame_index = len(current_animation) - 1
            else:  # 循环动画
                self.frame_index = 0
        self.image = current_animation[int(self.frame_index)] if self.orientation == 'left' else pygame.transform.flip(current_animation[int(self.frame_index)], True, False)
        self.mask = pygame.mask.from_surface(self.image)

    def run(self, dt):
        right_gap = self.rect.bottomright + vector(1, 1)
        right_block = self.rect.midright + vector(1, 0)
        left_gap = self.rect.bottomleft + vector(-1, 1)
        left_block = self.rect.midleft + vector(-1, 0)
        if self.direction.x > 0:  # 向右
            # 1. 悬崖检测
            floor_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(right_gap)]
            # 2. 墙壁检测
            wall_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(right_block)]
            if wall_sprites or not floor_sprites:
                self.direction.x *= -1
                self.orientation = 'left'
        if self.direction.x < 0:  # 向左
            # 1. 悬崖检测
            floor_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(left_gap)]
            # 2. 墙壁检测
            wall_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(left_block)]
            if wall_sprites or not floor_sprites:
                self.direction.x *= -1
                self.orientation = 'right'
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        self.hitbox.center = self.rect.center

    def hit(self, damage):
        self.frame_index = 0
        self.status = 'hit'
        self.health -= damage
        self.hit_sound.play()

    def dead_hit(self):
        self.frame_index = 0
        self.status = 'dead hit'
        self.is_dead = True
        self.damage_sprites.remove(self)
        self.attackable_sprites.remove(self)

    def dead_ground(self):
        self.frame_index = 0
        self.status = 'dead ground'
        self.dead_ground_timer.activate()

    def get_status(self):
        if not self.is_dead:
            if self.health <= 0 and not self.is_dead:  # 生命值降到0及以下，触发死亡
                self.dead_hit()
                return self.status

    def update(self, dt):
        if self.status == 'dead ground':
            self.dead_ground_timer.update()
        if self.status == 'run':
            self.run(dt)
        self.get_status()
        self.animate(dt)
