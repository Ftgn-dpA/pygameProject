import os.path
from os import walk

import pygame


# 资源导入
def import_folder(path):
    surface_list = []

    for folder_name, sub_folders, img_files in walk(path):
        for img_name in img_files:
            full_path = path + '/' + img_name
            img_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(img_surf)

    return surface_list


def import_folder_dict(path):
    surface_dict = {}

    for folder_name, sub_folders, img_files in walk(path):
        for img_name in img_files:
            full_path = path + '/' + img_name
            img_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[img_name.split('.')[0]] = img_surf

    return surface_dict


def import_folder2x(path):
    surface_list = []

    for folder_name, sub_folders, img_files in walk(path):
        for img_name in sorted(img_files, key=lambda file_name: int(os.path.splitext(file_name)[0])):
            full_path = path + '/' + img_name
            img_surf = pygame.transform.scale2x(pygame.image.load(full_path).convert_alpha())
            surface_list.append(img_surf)

    return surface_list


def import_folder_dict2x(path):
    surface_dict = {}

    for folder_name, sub_folders, img_files in walk(path):
        for img_name in sorted(img_files, key=lambda file_name: int(os.path.splitext(file_name)[0])):
            full_path = path + '/' + img_name
            img_surf = pygame.transform.scale2x(pygame.image.load(full_path).convert_alpha())
            surface_dict[img_name.split('.')[0]] = img_surf

    return surface_dict

