import pygame
import sprites

from settings import *
from pygame.math import Vector2 as vector
from random import choice


class Crabby(sprites.Generic):
    def __init__(self, assets, pos, group, collision_sprites):
        # 通用设置
        self.animation_frames = assets
        self.frame_index = 0
        self.status = 'run'
        self.orientation = 'left'
        surf = self.animation_frames[self.status][int(self.frame_index)]
        super().__init__(pos, surf, group)
        self.rect.bottom = self.rect.top + TILE_SIZE
        self.mask = pygame.mask.from_surface(self.image)
        self.hitbox = self.mask.get_bounding_rects()[0]

        # 移动
        self.direction = vector(choice((1, -1)), 0)
        self.orientation = 'left' if self.direction.x < 0 else 'right'
        self.pos = vector(self.rect.topleft)
        self.speed = 120
        self.collision_sprites = collision_sprites

        # 单位属性
        self.health = 10

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
                self.status = 'run'
        self.image = current_animation[int(self.frame_index)] if self.orientation == 'left' else pygame.transform.flip(current_animation[int(self.frame_index)], True, False)
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, dt):
        right_gap = self.rect.bottomright + vector(1, 1)
        right_block = self.rect.midright + vector(1, 0)
        left_gap = self.rect.bottomleft + vector(-1, 1)
        left_block = self.rect.midleft + vector(-1, 0)

        if self.direction.x > 0:  # moving right
            # 1. no floor collision
            floor_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(right_gap)]
            # 2. wall collision
            wall_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(right_block)]
            if wall_sprites or not floor_sprites:
                self.direction.x *= -1
                self.orientation = 'left'

        if self.direction.x < 0:  # moving left
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
        self.health -= damage
        self.status = 'hit'
        # 不可打断的状态，从0号帧开始播放
        self.frame_index = 0
        self.hit_sound.play()

    def dead(self):
        self.kill()

    def update(self, dt):
        if self.health <= 0:
            self.dead()
        else:
            self.animate(dt)
            if self.status == 'run':
                self.move(dt)
