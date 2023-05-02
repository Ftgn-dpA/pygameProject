import pickle
import sys
from random import choice, randint

from pygame.image import load
from pygame.math import Vector2 as vector
from pygame.mouse import get_pos as mouse_pos
from pygame.mouse import get_pressed as mouse_buttons

from menu import Menu
from settings import *
from support import *
from timer import Timer


class Editor:
    def __init__(self):

        # main setup
        self.display_surface = pygame.display.get_surface()
        self.canvas_data = {}

        # imports
        self.land_tiles = import_folder_dict('../graphics/terrain/land')
        self.imports()

        # clouds
        self.current_clouds = []
        self.cloud_surf = import_folder('../graphics/clouds')
        self.cloud_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.cloud_timer, 2000)
        self.startup_clouds()

        # navigation
        self.origin = vector()
        self.pan_active = False
        self.pan_offset = vector()

        # support lines
        self.support_line_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.support_line_surf.set_colorkey('green')
        self.support_line_surf.set_alpha(30)

        # selection
        self.selection_index = 2
        self.last_selected_cell = None

        # menu
        self.menu = Menu()

        # objects
        self.canvas_objects = pygame.sprite.Group()
        self.foreground = pygame.sprite.Group()
        self.background = pygame.sprite.Group()
        self.object_drag_active = False
        self.object_timer = Timer(400)

        # player
        CanvasObject(
            pos=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2),
            frames=self.animations[0]['frames'],
            tile_id=0,
            origin=self.origin,
            group=[self.canvas_objects, self.foreground]
        )

        # sky
        self.sky_handle = CanvasObject(
            pos=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2),
            frames=[self.sky_handle_surf],
            tile_id=1,
            origin=self.origin,
            group=[self.canvas_objects, self.foreground]
        )

        # music
        self.editor_music = pygame.mixer.Sound('../audio/editor/Explorer.ogg')
        self.editor_music.set_volume(0.05)  # 音量
        self.editor_music.play(loops=-1)

    # support
    # 获取当前块坐标
    def get_current_cell(self, obj=None):
        distance_to_origin = vector(mouse_pos()) - self.origin if not obj else vector(obj.distance_to_origin) - self.origin

        col = int(distance_to_origin.x // TILE_SIZE)
        row = int(distance_to_origin.y // TILE_SIZE)

        return col, row

    # 检查图块周围（保持贴图相连）
    def check_neighbors(self, cell_pos):

        # create a local cluster
        cluster_size = 3  # 检查周围方块集群的边长
        local_cluster = [
            (cell_pos[0] + col - int(cluster_size / 2), cell_pos[1] + row - int(cluster_size / 2))
            for col in range(cluster_size)
            for row in range(cluster_size)
        ]

        # check neighbors
        # 以当前块为中心的3*3的块阵
        for cell in local_cluster:
            if cell in self.canvas_data:
                self.canvas_data[cell].terrain_neighbors = []
                self.canvas_data[cell].water_on_top = False
                for name, side in NEIGHBOR_DIRECTIONS.items():
                    neighbor_cell = (cell[0] + side[0], cell[1] + side[1])

                    # terrain neighbors
                    if neighbor_cell in self.canvas_data:
                        if self.canvas_data[neighbor_cell].has_terrain:
                            self.canvas_data[cell].terrain_neighbors.append(name)

                        # water top neighbor
                        if self.canvas_data[neighbor_cell].has_water and self.canvas_data[cell].has_water and name == 'A':
                            self.canvas_data[cell].water_on_top = True

    # 资源导入
    def imports(self):
        self.water_bottom = load('../graphics/terrain/water/water_bottom.png').convert_alpha()
        self.sky_handle_surf = load('../graphics/cursors/handle.png').convert_alpha()

        # animations
        self.animations = {}
        for key, value in EDITOR_DATA.items():
            if value['graphics']:
                graphics = import_folder(value['graphics'])
                self.animations[key] = {
                    'frame index': 0,
                    'frames': graphics,
                    'length': len(graphics)
                }

        # preview
        self.preview_surfs = {key: load(value['preview']).convert_alpha() for key, value in EDITOR_DATA.items() if value['preview']}

    # 动画
    def animation_update(self, dt):
        for value in self.animations.values():
            value['frame index'] += ANIMATION_SPEED * dt
            if value['frame index'] >= value['length']:
                value['frame index'] = 0

    # 检查当前鼠标是否点击的是对象
    def mouse_on_object(self):
        for sprite in self.canvas_objects:
            if sprite.rect.collidepoint(mouse_pos()):
                return sprite

    def create_grid(self):
        for tile in self.canvas_data.values():
            tile.objects = []

        for obj in self.canvas_objects:
            current_cell = self.get_current_cell(obj)
            offset = vector(obj.distance_to_origin) - vector(current_cell) * TILE_SIZE

            if current_cell in self.canvas_data:
                self.canvas_data[current_cell].add_id(obj.tile_id, offset)
            else:
                self.canvas_data[current_cell] = CanvasTile(obj.tile_id, offset)

        layers = {
            'water': {},
            'bg palms': {},
            'terrain': {},
            'enemies': {},
            'coins': {},
            'flag': {},
            'fg objects': {},
        }

        # grid offset
        left = sorted(self.canvas_data.keys(), key=lambda tile: tile[0])[0][0]
        top = sorted(self.canvas_data.keys(), key=lambda tile: tile[1])[0][1]

        # fill the grid
        for tile_pos, tile in self.canvas_data.items():
            row_adjusted = tile_pos[1] - top
            col_adjusted = tile_pos[0] - left
            x = col_adjusted * TILE_SIZE
            y = row_adjusted * TILE_SIZE

            if tile.has_water:
                layers['water'][(x, y)] = tile.get_water()

            if tile.has_terrain:
                layers['terrain'][(x, y)] = tile.get_terrain() if tile.get_terrain() in self.land_tiles else 'X'

            if tile.coin:
                layers['coins'][(x + TILE_SIZE // 2, y + TILE_SIZE // 2)] = tile.coin

            if tile.enemy:
                layers['enemies'][(x, y)] = tile.enemy

            if tile.flag:
                layers['flag'][(x, y)] = tile.flag

            if tile.objects:
                for obj, offset in tile.objects:
                    if obj in [key for key, value in EDITOR_DATA.items() if value['style'] == 'palm_bg']:
                        layers['bg palms'][(int(x + offset.x), int(y + offset.y))] = obj
                    else:
                        layers['fg objects'][(int(x + offset.x), int(y + offset.y))] = obj

        return layers

    @staticmethod
    def save_grid(grid):
        with open('../level_data/data', 'wb') as data:
            pickle.dump(grid, data)

    # input
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                grid = self.create_grid()
                self.save_grid(grid)

            self.pan_input(event)
            self.selection_hotkeys(event)
            self.menu_click(event)

            self.object_drag(event)

            self.canvas_add()
            self.canvas_remove()

            self.create_clouds(event)

    # 地图平移
    def pan_input(self, event):
        # 按下鼠标中键
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[1]:
            self.pan_active = True
            self.pan_offset = vector(mouse_pos()) - self.origin
        if not mouse_buttons()[1]:
            self.pan_active = False
        # 更新origin
        if self.pan_active:
            self.origin = vector(mouse_pos()) - self.pan_offset
            for sprite in self.canvas_objects:
                sprite.pan_pos(self.origin)

    def selection_hotkeys(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.selection_index += 1
            if event.key == pygame.K_LEFT:
                self.selection_index -= 1
        self.selection_index = max(2, min(self.selection_index, len(EDITOR_DATA)))  # 限制index范围2~20

    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(mouse_pos()):
            new_index = self.menu.click(mouse_pos(), mouse_buttons())
            self.selection_index = new_index if new_index else self.selection_index

    # 画布添加（鼠标左键）
    def canvas_add(self):
        if mouse_buttons()[0] and not self.menu.rect.collidepoint(mouse_pos()) and not self.object_drag_active:
            current_cell = self.get_current_cell()
            if EDITOR_DATA[self.selection_index]['type'] == 'tile':
                # 方块
                if current_cell != self.last_selected_cell:

                    if current_cell in self.canvas_data:
                        self.canvas_data[current_cell].add_id(self.selection_index)
                    else:
                        self.canvas_data[current_cell] = CanvasTile(self.selection_index)

                    self.check_neighbors(current_cell)
                    self.last_selected_cell = current_cell
            else:
                # 对象
                if not self.object_timer.active:
                    groups = [self.canvas_objects, self.background] if EDITOR_DATA[self.selection_index]['style'] == 'palm_bg' else [self.canvas_objects, self.foreground]
                    CanvasObject(
                        pos=mouse_pos(),
                        frames=self.animations[self.selection_index]['frames'],
                        tile_id=self.selection_index,
                        origin=self.origin,
                        group=groups
                    )
                    self.object_timer.activate()

    # 删除贴图块（鼠标右键）
    def canvas_remove(self):
        if mouse_buttons()[2] and not self.menu.rect.collidepoint(mouse_pos()):

            # delete objects
            selected_object = self.mouse_on_object()
            if selected_object:
                if EDITOR_DATA[selected_object.tile_id]['style'] not in ('player', 'sky'):
                    selected_object.kill()

            # delete tiles
            if self.canvas_data:
                current_cell = self.get_current_cell()
                if current_cell in self.canvas_data:
                    self.canvas_data[current_cell].remove_id(self.selection_index)

                    if self.canvas_data[current_cell].is_empty:
                        del self.canvas_data[current_cell]
                    self.check_neighbors(current_cell)

    # 拖动对象
    def object_drag(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[0]:
            for sprite in self.canvas_objects:
                if sprite.rect.collidepoint(mouse_pos()):
                    sprite.start_drag()
                    self.object_drag_active = True

        if event.type == pygame.MOUSEBUTTONUP and self.object_drag_active:
            for sprite in self.canvas_objects:
                if sprite.selected:
                    sprite.end_drag(self.origin)
                    self.object_drag_active = False

    # drawing
    # 网格线
    def draw_tile_lines(self):
        cols = WINDOW_WIDTH // TILE_SIZE
        rows = WINDOW_HEIGHT // TILE_SIZE

        origin_offset = vector(
            x=self.origin.x - int(self.origin.x / TILE_SIZE) * TILE_SIZE,
            y=self.origin.y - int(self.origin.y / TILE_SIZE) * TILE_SIZE
        )

        self.support_line_surf.fill('green')

        for col in range(cols + 1):
            x = origin_offset.x + col * TILE_SIZE
            pygame.draw.line(self.support_line_surf, LINE_COLOR, (x, 0), (x, WINDOW_HEIGHT))

        for row in range(rows + 1):
            y = origin_offset.y + row * TILE_SIZE
            pygame.draw.line(self.support_line_surf, LINE_COLOR, (0, y), (WINDOW_WIDTH, y))

        self.display_surface.blit(self.support_line_surf, (0, 0))

    # 绘制关卡
    def draw_level(self):
        self.background.draw(self.display_surface)
        for cell_pos, tile in self.canvas_data.items():
            pos = self.origin + vector(cell_pos) * TILE_SIZE  # 化单元格坐标为像素坐标

            # terrain
            if tile.has_terrain:
                terrain_string = ''.join(tile.terrain_neighbors)
                terrain_style = terrain_string if terrain_string in self.land_tiles else 'X'  # 如果地形字符串不在已导入的地形名中就使用通用地形'X'
                self.display_surface.blit(self.land_tiles[terrain_style], pos)

            # water
            if tile.has_water:
                if tile.water_on_top:
                    self.display_surface.blit(self.water_bottom, pos)
                else:
                    frames = self.animations[3]['frames']
                    index = int(self.animations[3]['frame index'])
                    surf = frames[index]
                    self.display_surface.blit(surf, pos)

            # coins
            if tile.coin:
                frames = self.animations[tile.coin]['frames']
                index = int(self.animations[tile.coin]['frame index'])
                surf = frames[index]
                rect = surf.get_rect(center=(pos[0] + TILE_SIZE // 2, pos[1] + TILE_SIZE // 2))  # 保证金币位于格子中心
                self.display_surface.blit(surf, rect)

            # flag
            if tile.flag:
                frames = self.animations[tile.flag]['frames']
                index = int(self.animations[tile.flag]['frame index'])
                surf = frames[index]
                rect = surf.get_rect(center=(pos[0] + TILE_SIZE // 2, pos[1] + 18))  # 保证旗子底部位于格子中心底部
                self.display_surface.blit(surf, rect)

            # enemies
            if tile.enemy:
                frames = self.animations[tile.enemy]['frames']
                index = int(self.animations[tile.enemy]['frame index'])
                surf = frames[index]
                rect = surf.get_rect(midbottom=(pos[0] + TILE_SIZE // 2, pos[1] + TILE_SIZE))  # 保证敌人位于格子中心底部
                self.display_surface.blit(surf, rect)
        self.foreground.draw(self.display_surface)

    # 预览
    def preview(self):
        selected_object = self.mouse_on_object()
        if not self.menu.rect.collidepoint(mouse_pos()):
            if selected_object:
                rect = selected_object.rect.inflate(10, 10)
                color = 'black'
                width = 3
                size = 15
                # topleft
                pygame.draw.lines(self.display_surface, color, False, ((rect.left, rect.top + size), rect.topleft, (rect.left + size, rect.top)),
                                  width)
                # topright
                pygame.draw.lines(self.display_surface, color, False, ((rect.right, rect.top + size), rect.topright, (rect.right - size, rect.top)),
                                  width)
                # bottomleft
                pygame.draw.lines(self.display_surface, color, False,
                                  ((rect.left, rect.bottom - size), rect.bottomleft, (rect.left + size, rect.bottom)), width)
                # bottomright
                pygame.draw.lines(self.display_surface, color, False,
                                  ((rect.right, rect.bottom - size), rect.bottomright, (rect.right - size, rect.bottom)), width)
            else:
                type_dict = {key: value['type'] for key, value in EDITOR_DATA.items()}
                surf = self.preview_surfs[self.selection_index].copy()
                surf.set_alpha(200)

                # tile
                if type_dict[self.selection_index] == 'tile':
                    current_cell = self.get_current_cell()
                    match self.selection_index:
                        case 11:  # crabby，预览位置修正
                            rect = surf.get_rect(midbottom=self.origin + vector(current_cell) * TILE_SIZE + vector(TILE_SIZE // 2, TILE_SIZE))
                        case 12:  # pinkstar，预览位置修正
                            rect = surf.get_rect(midbottom=self.origin + vector(current_cell) * TILE_SIZE + vector(TILE_SIZE // 2, TILE_SIZE))
                        case 21:  # flag，预览位置修正
                            rect = surf.get_rect(bottomleft=self.origin + vector(current_cell) * TILE_SIZE + vector(0, TILE_SIZE))
                        case _:
                            rect = surf.get_rect(topleft=self.origin + vector(current_cell) * TILE_SIZE)
                # object
                else:
                    rect = surf.get_rect(center=mouse_pos())

                self.display_surface.blit(surf, rect)

    # 天空
    def display_sky(self, dt):
        self.display_surface.fill(SKY_COLOR)
        y = self.sky_handle.rect.centery

        # horizon lines
        if y > 0:
            horizon_rect1 = pygame.Rect(0, y - 10, WINDOW_WIDTH, 10)
            horizon_rect2 = pygame.Rect(0, y - 15, WINDOW_WIDTH, 5)
            horizon_rect3 = pygame.Rect(0, y - 20, WINDOW_WIDTH, 2.5)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect1)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect2)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect3)

            self.display_clouds(dt, y)

        # sea
        if 0 < y < WINDOW_HEIGHT:
            sea_rect = pygame.Rect(0, y, WINDOW_WIDTH, WINDOW_HEIGHT)
            pygame.draw.rect(self.display_surface, SEA_COLOR, sea_rect)
        if y < 0:
            self.display_surface.fill(SEA_COLOR)

        pygame.draw.line(self.display_surface, HORIZON_COLOR, (0, y), (WINDOW_WIDTH, y), 3)

    def display_clouds(self, dt, horizon_y):
        for cloud in self.current_clouds:
            cloud['pos'][0] -= cloud['speed'] * dt
            x = cloud['pos'][0]
            y = horizon_y - cloud['pos'][1]
            self.display_surface.blit(cloud['surf'], (x, y))

    def create_clouds(self, event):
        if event.type == self.cloud_timer:
            surf = choice(self.cloud_surf)
            surf = pygame.transform.scale2x(surf) if randint(0, 4) < 2 else surf

            pos = [WINDOW_WIDTH + randint(50, 100), randint(0, WINDOW_HEIGHT)]
            self.current_clouds.append({'surf': surf, 'pos': pos, 'speed': randint(20, 50)})

            # remove clouds
            self.current_clouds = [cloud for cloud in self.current_clouds if cloud['pos'][0] > -400]

    def startup_clouds(self):
        for i in range(20):
            surf = pygame.transform.scale2x(choice(self.cloud_surf)) if randint(0, 4) < 2 else choice(self.cloud_surf)
            pos = [randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)]
            self.current_clouds.append({'surf': surf, 'pos': pos, 'speed': randint(20, 50)})

    # update
    def run(self, dt):
        self.event_loop()

        # updating
        self.animation_update(dt)
        self.canvas_objects.update(dt)
        self.object_timer.update()

        # drawing
        self.display_surface.fill('grey')
        self.display_sky(dt)
        self.draw_level()
        self.draw_tile_lines()
        pygame.draw.circle(self.display_surface, 'red', self.origin, 5)
        self.preview()
        self.menu.display(self.selection_index)


class CanvasTile:
    def __init__(self, tile_id, offset=vector()):
        # terrain
        self.has_terrain = False
        self.terrain_neighbors = []
        # water
        self.has_water = False
        self.water_on_top = False  # 是否是顶层的水（顶层水需要动画，而非顶层不需要）
        # coin
        self.coin = None  # 4, 5, 6
        # enemy
        self.enemy = None
        # flag
        self.flag = None
        # objects
        self.objects = []

        self.add_id(tile_id, offset)
        self.is_empty = False

    def add_id(self, tile_id, offset=vector()):
        options = {key: value['style'] for key, value in EDITOR_DATA.items()}
        match options[tile_id]:
            case 'terrain':
                self.has_terrain = True
            case 'water':
                self.has_water = True
            case 'coin':
                self.coin = tile_id
            case 'enemy':
                self.enemy = tile_id
            case 'flag':
                self.flag = tile_id
            case _:  # objects
                if (tile_id, offset) not in self.objects:
                    self.objects.append((tile_id, offset))

    def remove_id(self, tile_id):
        options = {key: value['style'] for key, value in EDITOR_DATA.items()}
        match options[tile_id]:
            case 'terrain':
                self.has_terrain = False
            case 'water':
                self.has_water = False
            case 'coin':
                self.coin = None
            case 'flag':
                self.flag = None
            case 'enemy':
                self.enemy = None
        self.check_content()

    def check_content(self):
        if not self.has_terrain and not self.has_water and not self.coin and not self.enemy:
            self.is_empty = True

    def get_terrain(self):
        return ''.join(self.terrain_neighbors)

    def get_water(self):
        return 'bottom' if self.water_on_top else 'top'


class CanvasObject(pygame.sprite.Sprite):
    def __init__(self, pos, frames, tile_id, origin, group):
        super().__init__(group)
        self.tile_id = tile_id

        # animation
        self.frames = frames
        self.frame_index = 0

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        # movement
        self.distance_to_origin = vector(self.rect.topleft) - origin
        self.selected = False
        self.mouse_offset = vector()

    # 开始拖动对象
    def start_drag(self):
        self.selected = True
        self.mouse_offset = vector(mouse_pos()) - vector(self.rect.topleft)

    # 结束拖动对象
    def end_drag(self, origin):
        self.selected = False
        self.distance_to_origin = vector(self.rect.topleft) - origin

    # 鼠标拖动对象
    def drag(self):
        if self.selected:
            self.rect.topleft = vector(mouse_pos()) - vector(self.mouse_offset)

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        self.frame_index = 0 if self.frame_index >= len(self.frames) else self.frame_index
        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def pan_pos(self, origin):
        self.rect.topleft = origin + self.distance_to_origin

    def update(self, dt):
        self.animate(dt)
        self.drag()
