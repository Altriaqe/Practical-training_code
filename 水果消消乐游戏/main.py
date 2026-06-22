import sys
import pygame
from pygame.locals import *
import random 



# 全局变量
SCREEN_SIZE = (900, 600)   # 游戏窗口大小
CELL_SIZE = 50              # 每个格子的大小
WIDTH, HEIGHT = 9, 9        # 游戏矩阵的行数和列数 
MATRIX_TOPLEFT = (250, 100)     # 游戏矩阵在窗口中的左上角坐标
FPS = 60
GAME_TIME = 3 * 60 * 100 # 游戏时间，单位为纳秒
SCORE_PER_FRUIT = [1,2,1,1,2,1] # 每种水果的分数

STATUS_START = 0
STATUS_PLAYING = 1
STATUS_SCORE = 2



# 具体加载一个图片或字体
def load_image(path):
    return pygame.image.load(path).convert().alpha() # 加载图片并转换为带有alpha通道的格式，支持透明背景


# 加载图片到内存
ASSETS = {}
def load_all_assets():
    ASSETS["bg_tree"] = load_image("static/img/tree.png")
    ASSETS["bg_score"] = load_image("static/img/bs.png")
    ASSETS["bg_playing"] = load_image("static/img/bp.png")
    ASSETS["game_start_button"] = load_image("static/img/game_start_butten.png")
    ASSETS["exit"] = load_image("static/img/exit.png")
    ASSETS["frame"] = load_image("static/img/frame.png")
    ASSETS["board_score"] = load_image("static/img/task.png")
    ASSETS["brick"] = load_image("static/img/brick.png")
    ASSETS["no_fruit"] = load_image("static/img/nonaeanimal.png")
    ASSETS["time_is_over"] = load_image("static/img/time_is_over.png")
    ASSETS["digit"] = [load_image(f"static/img/digit_{i}.png") for i in range(10)]

class Manager:
    def __init__(self, screen):
        self.screen = screen
        self.state = STATUS_START # 游戏状态：start, playing, game_over
        self.last_sel = [-1, -1] # 上一次选中的水果位置
        self.cur_sel = [-1, -1] # 当前选中的水果位置
        
    def reset_game(self):
        # 初始化游戏数据
        pass
    def go_to_score(self):
        # 计算分数并显示分数界面
        pass
    def xy_to_row_col(self, x, y):
        # 将鼠标点击的坐标转换为矩阵中的行列
        pass
    def handle_mouse(self, mouse_pos):
        x, y = mouse_pos
        if self.state == STATUS_START:
            if 300 < x < 600 and 250 < y < 370:
                self.state = STATUS_PLAYING
                self.reset_game()
            elif self.state == STATUS_SCORE:
                if 20 < x < 83 and 530 < y < 590:
                   self.go_to_score()
                   return
                mx1, my1 = MATRIX_TOPLEFT
                mx2, my2 = mx1 + CELL_SIZE * WIDTH, my1 + CELL_SIZE * HEIGHT
                if mx1 < x < mx2 and my1 < y < my2:
                    row, col = self.xy_to_row_col(x, y)
                    self.last_sel = self.cur_sel
                    self.cur_sel = [row, col]
        pass

    def update(self):
        # 根据游戏状态更新游戏逻辑
        pass

    def draw(self):
        # 根据游戏状态绘制不同的界面
        pass

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("水果消消乐")
    load_all_assets()
    clock = pygame.time.Clock()

    game = Manager(screen)
    # 事件驱动
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
            if event.type == MOUSEBUTTONDOWN:
                game.handle_mouse(event.pos)

        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()