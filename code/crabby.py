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
        self.default_status = 'idle'
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
        self.attack_cooldown = timer.Timer(duration=1000, action=self.attack_reset)
        self.has_attacked = False
        self.health = 20
        # 组
        self.damage_sprites = group[1]
        self.attackable_sprites = group[2]
        # 删除不在地面的crabby
        if not [sprite for sprite in collision_sprites if sprite.rect.collidepoint(self.rect.midbottom + vector(0, 10))]:
            self.kill()

    def animate(self, dt):
        current_animation = self.animation_frames[self.status]
        if self.frame_index >= len(current_animation):  # 动画播放到最后一帧
            if CRABBY_ANIMATION_STATUS[self.status]['times'] == 'once':  # 一次性动画
                if self.status == 'dead hit':  # 死亡（打击）动画结束，转换状态为死亡（地面）
                    self.dead_ground()
                elif self.status == 'anticipation':  # 预警状态结束
                    self.attack()
                elif self.status == 'attack':
                    self.frame_index = 0
                    self.status = self.default_status
                elif self.status == 'hit':
                    self.frame_index = 0
                    self.status = self.default_status
                else:
                    self.frame_index = len(current_animation) - 1
            else:  # 循环动画
                self.frame_index = 0
        self.image = current_animation[int(self.frame_index)] if self.orientation == 'left' else pygame.transform.flip(current_animation[int(self.frame_index)], True, False)
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        self.pos = vector(self.rect.topleft)
        self.mask = pygame.mask.from_surface(self.image)
        self.hitbox = self.mask.get_bounding_rects()[0]
        self.hitbox.center = self.rect.center
        self.frame_index += ANIMATION_SPEED * dt

    def get_status(self):
        if not self.is_dead:
            if self.health <= 0 and not self.is_dead:  # 生命值降到0及以下，触发死亡
                self.dead_hit()
                return self.status
            if abs(self.rect.center[1] - self.player.rect.center[1]) <= TILE_SIZE // 2 and abs(self.rect.center[0] - self.player.rect.center[0]) <= 300 and not self.has_attacked and self.status == self.default_status:  # 与玩家处于同一层且距离足够近，切换攻击状态
                self.anticipation()
                return self.status

    def anticipation(self):
        self.frame_index = 0
        self.status = 'anticipation'
        self.has_attacked = True
        self.attack_cooldown.activate()

    def attack(self):
        self.frame_index = 0
        self.status = 'attack'

    def attack_reset(self):
        self.has_attacked = False

    def hit(self, damage):
        self.frame_index = 0
        self.status = 'hit'
        self.health -= damage

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

    def update(self, dt):
        if self.status == 'dead ground':
            self.dead_ground_timer.update()
        if self.has_attacked:
            self.attack_cooldown.update()
        self.get_status()
        self.animate(dt)
