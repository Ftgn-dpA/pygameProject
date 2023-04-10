import pygame


class Timer:
    def __init__(self, duration, cyclic=False, action=None):
        self.start_time = 0  # 计时器开始时间戳
        self.duration = duration  # 计时器持续时间
        self.cyclic = cyclic  # 是否循环计时
        self.active = False  # 计时器启动
        self.expired = False  # 计时器到期
        self.action = action  # 计时器到期动作

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def clear(self):
        self.active = False
        self.expired = False
        self.start_time = 0

    def expire(self):
        self.expired = True
        self.act()

    def act(self):
        if self.action is not None:
            self.action()

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.expire()
            if not self.cyclic:
                self.clear()
