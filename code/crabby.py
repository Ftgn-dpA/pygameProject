import pygame
import sprites
import timer

from settings import *
from pygame.math import Vector2 as vector
from random import choice


class Crabby(sprites.Generic):
    def __init__(self, assets, pos, group, collision_sprites):
        # 通用设置
        self.animation_frames = assets
        self.frame_index = 0
        self.status = 'idle'
        self.orientation = 'left'
        surf = self.animation_frames[self.status][int(self.frame_index)]
        super().__init__(pos, surf, group)
        self.rect.bottom = self.rect.top + TILE_SIZE
        self.mask = pygame.mask.from_surface(self.image)
        self.hitbox = self.mask.get_bounding_rects()[0]
        self.hitbox.center = self.rect.center

        # 移动
        self.direction = vector(choice((1, -1)), 0)
        self.orientation = 'left' if self.direction.x < 0 else 'right'
        self.pos = vector(self.rect.topleft)
        self.speed = 120
        self.collision_sprites = collision_sprites

        # 单位属性
        self.is_dead = False
        self.dead_ground_timer = timer.Timer(duration=3000, action=self.kill)
        self.health = 20

        # 组
        self.damage_sprites = group[1]
        self.attackable_sprites = group[2]

        # 删除不在地面的crabby
        if not [sprite for sprite in collision_sprites if sprite.rect.collidepoint(self.rect.midbottom + vector(0, 10))]:
            self.kill()

    def animate(self, dt):
        current_animation = self.animation_frames[self.status]
        self.frame_index += ANIMATION_SPEED * dt

        if self.frame_index >= len(current_animation):  # 动画播放到最后一帧
            if CRABBY_ANIMATION_STATUS[self.status]['times'] == 'once':  # 一次性动画
                if self.status == 'dead hit':  # 死亡（打击）动画结束，转换状态为死亡（地面）
                    self.frame_index = 0
                    self.dead_ground()
                else:
                    self.frame_index = len(current_animation) - 1
            else:  # 循环动画
                self.frame_index = 0

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
        # 从0号帧开始播放
        self.frame_index = 0
        self.status = 'hit'
        self.health -= damage

    def dead_hit(self):
        self.status = 'dead hit'
        self.is_dead = True
        self.damage_sprites.remove()
        self.attackable_sprites.remove()

    def dead_ground(self):
        self.status = 'dead ground'
        self.dead_ground_timer.activate()

    def update(self, dt):
        if self.health <= 0 and not self.is_dead:  # 生命值降到0及以下，触发死亡
            self.dead_hit()
        if self.status == 'run':
            self.move(dt)
        if self.status == 'dead ground':
            self.dead_ground_timer.update()
        self.animate(dt)
