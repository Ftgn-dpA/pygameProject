import pygame
import sys

from pygame.math import Vector2 as vector
from level_data import levels
from support import import_folder
from settings import *


class Node(pygame.sprite.Sprite):
    def __init__(self, pos, status, icon_speed, path):
        super().__init__()
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        if status == 'available':
            self.status = 'available'
        else:
            self.status = 'locked'
        self.rect = self.image.get_rect(center=pos)

        self.detection_zone = pygame.Rect(self.rect.centerx - (icon_speed / 2), self.rect.centery - (icon_speed / 2), icon_speed, icon_speed)

    def animate(self):
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self):
        if self.status == 'available':
            self.animate()
        else:
            tint_surf = self.image.copy()
            tint_surf.fill('black', None, pygame.BLEND_RGBA_MULT)
            self.image.blit(tint_surf, (0, 0))


class Icon(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.image = pygame.image.load('../graphics/overworld/hat.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.rect.center = self.pos


class Overworld:
    def __init__(self, start_level, max_level, surface):
        # setup
        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level
        # movement
        self.moving = False
        self.move_direction = vector()
        self.speed = 8
        # sprites
        self.nodes = self.setup_nodes()
        self.icon = self.setup_icon()

    def setup_nodes(self):
        nodes = pygame.sprite.Group()
        for index, node_data in enumerate(levels.values()):
            if index <= self.max_level:
                node_sprite = Node(node_data['node_pos'], 'available', self.speed, node_data['node_graphics'])
            else:
                node_sprite = Node(node_data['node_pos'], 'locked', self.speed, node_data['node_graphics'])
            nodes.add(node_sprite)

        return nodes

    def setup_icon(self):
        icon = pygame.sprite.GroupSingle()
        icon_sprite = Icon(self.nodes.sprites()[self.current_level].rect.center)
        icon.add(icon_sprite)

        return icon

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.moving:
            if keys[pygame.K_d] and self.current_level < self.max_level:
                self.move_direction = self.get_move_direction('next')
                self.current_level += 1
                self.moving = True
            elif keys[pygame.K_a] and self.current_level > 0:
                self.move_direction = self.get_move_direction('previous')
                self.current_level -= 1
                self.moving = True

    def get_move_direction(self, target):
        start = vector(self.nodes.sprites()[self.current_level].rect.center)

        if target == 'next':
            end = vector(self.nodes.sprites()[self.current_level + 1].rect.center)
        else:
            end = vector(self.nodes.sprites()[self.current_level - 1].rect.center)

        return (end - start).normalize()

    def update_icon_pos(self):
        if self.moving and self.move_direction:
            self.icon.sprite.pos += self.move_direction * self.speed
            target_node = self.nodes.sprites()[self.current_level]
            if target_node.detection_zone.collidepoint(self.icon.sprite.pos):
                self.moving = False
                self.move_direction = vector()

    def draw_paths(self):
        points = [point['node_pos'] for index, point in enumerate(levels.values()) if index <= self.max_level]
        pygame.draw.lines(self.display_surface, PATH_COLOR, False, points, 6)

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def run(self):
        self.event_loop()
        self.input()
        self.update_icon_pos()
        self.icon.update()
        self.nodes.update()
        # draw
        self.draw_paths()
        self.nodes.draw(self.display_surface)
        self.icon.draw(self.display_surface)
