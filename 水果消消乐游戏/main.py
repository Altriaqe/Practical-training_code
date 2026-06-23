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
    # 创建值为列表的字典，列表中存储每种水果的图片
    ASSETS["digit"] = [load_image(f"static/img/digit_{i}.png") for i in range(10)]
    ASSETS["fruit"] = [load_image(f"static/img/fruit_{name}.png") for name in 
                       ('lemon', 'watermelon', 'grapefruit', 'kiwfruit', 'nettedmelon', 'avocado')]   
    # 加载bling8.png图片，作为消除水果时的特效图片
    ASSETS["bling8"] = load_image("static/img/bling8.png")

    # 加载字体，如果加载失败则使用默认字体
    try:
        ASSETS["font_large"] = pygame.font.Font("static/font/zhengqingke", 43)
        ASSETS["font_small"] = pygame.font.Font("static/font/zhengqingke", 35)
    except:
        ASSETS["font_large"] = pygame.font.Font(None, 43)
        ASSETS["font_small"] = pygame.font.Font(None, 35)


class Manager:
    def __init__(self, screen):
        self.screen = screen  # 游戏窗口对象
        self.state = STATUS_START # 游戏状态：start, playing, game_over
        self.grid = [[-1] * WIDTH for _ in range(HEIGHT)] # 游戏矩阵，存储每个格子中的水果类型，-1表示空格

        self.score = 0 # 初始分数
        self.destory_counts = [0] * 6 # 每种水果的消除数量
        self.score_list = [] # 存储每次消除的分数，用于显示分数动画
        self.reset_layout = True # 允许随机生成self.grid的标志位

        self.last_sel = [-1, -1] # 上一次选中的水果位置
        self.cur_sel = [-1, -1] # 当前选中的水果位置
        self.exchange_status = -1 # 默认不可交换, 1表示可以交换，0表示交换完成
        
        self.start_time = 0 # 游戏开始时间
        self.runtime = 0 # 游戏运行时间
        self.time_is_over = False # 游戏时间是否结束
        self.death_sign = False # 游戏出现死局的标志位
        self.animating = False # 游戏正在播放消除动画的标志位
        self._score_recoreded = True # 游戏是否需要记录分数的标志， 下划线表示私有变量，表示是类内部使用的变量，不应该被外部访问

        self.feedback_img = None # 游戏结束时的反馈图片
        self.feedback_timer = 0 # 游戏结束时的反馈图片显示时间

        self.end_img = None # 游戏结束时的图片
        self.end_timer = 0 # 游戏结束时的图片显示时间


        # 预计计算各个水果框所在位置
        self._cell_coored = {}
        for row in range(HEIGHT):
            for col in range(WIDTH):
                self._cell_coored[(row, col)] = \
                (MATRIX_TOPLEFT[0] + col * CELL_SIZE, MATRIX_TOPLEFT[1] + row * CELL_SIZE)

    def reset_game(self):
        # 初始化游戏数据
        self.reset_layout = True
        self.score = 0
        self.destory_counts = [0] * 6
        self.runtime = 0
        self.start_time = pygame.time.get_ticks()
        self.death_sign = False
        self.animating = False
        self.cur_sel = [-1, -1]
        self.last_sel = [-1, -1]
        self.exchange_status = -1
        self._score_recoreded = True
        self.feedback_img = None
        self.feedback_timer = 0
        self.end_img = None
        self.end_timer = 0

    def go_to_score(self):
        # 计算分数并显示分数界面
        pass
    def xy_to_row_col(self, x, y):
        # 将鼠标点击的坐标转换为矩阵中的行列
        pass
    def handle_mouse(self, mouse_pos):
        if self.animating or self.end_game() > 0:  # 出现死局或正在播放消除动画时，不处理鼠标点击事件
            return
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

                    if self.last_sel != [-1, -1]:
                        if abs (row - self.last_sel[0]) + abs(col - self.last_sel[1]) == 1:
                            self.exchange_status = 1

            elif self.state == STATUS_PLAYING:
                if 620 < x < 820 and 160 < y < 220:
                    self.state = STATUS_PLAYING
                    self.reset_game()
                if 620 < x < 820 and 400 < y < 220:
                    sys.exit()



    def update(self):
        # 根据游戏状态更新游戏逻辑
        pass

    def draw(self):
        # 根据游戏状态绘制不同的界面
        pass

def main():
    pygame.init()  # 初始化pygame
    screen = pygame.display.set_mode(SCREEN_SIZE)  # 创建游戏窗口
    pygame.display.set_caption("水果消消乐")  # 设置窗口标题
    load_all_assets()  # 加载所有资源
    clock = pygame.time.Clock()  # 创建时钟对象，控制游戏帧率

    game = Manager(screen)  # 创建游戏管理器对象，负责游戏逻辑和界面绘制
    # 事件驱动
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
            if event.type == MOUSEBUTTONDOWN:
                game.handle_mouse(event.pos) # 对用户点击

        game.update() # 更新游戏逻辑
        game.draw()  # 绘制游戏界面
        pygame.display.flip()  # 更新屏幕显示
        clock.tick(FPS)  # 控制游戏帧率

if __name__ == "__main__":
    main()