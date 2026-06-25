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
GAME_TIME = 3 * 60 * 1000 # 游戏时间，单位为毫秒
SCORE_PER_FRUIT = [1,2,1,1,2,1] # 每种水果的分数

STATUS_START = 0
STATUS_PLAYING = 1
STATUS_SCORE = 2



# 具体加载一个图片或字体
def load_image(path):
    return pygame.image.load(path).convert_alpha()  # 加载图片并转换为带有alpha通道的格式，支持透明背景


# 加载图片到内存
ASSETS = {}
def load_all_assets():
    ASSETS["bg_tree"] = load_image("static/img/tree.png")
    ASSETS["bg_score"] = load_image("static/img/bs.png")
    ASSETS["bg_playing"] = load_image("static/img/bg.png")
    ASSETS["game_start_button"] = load_image("static/img/game_start_button.png")
    ASSETS["exit"] = load_image("static/img/exit.png")
    ASSETS["frame"] = load_image("static/img/frame.png")
    ASSETS["board_score"] = load_image("static/img/task.png")
    ASSETS["brick"] = load_image("static/img/brick.png")
    ASSETS["no_fruit"] = load_image("static/img/noneanimal.png")
    ASSETS["time_is_over"] = load_image("static/img/time_is_over.png")
    # 创建值为列表的字典，列表中存储每种水果的图片
    ASSETS["digit"] = [load_image(f"static/img/{i}.png") for i in range(10)]
    ASSETS["fruit"] = [load_image(f"static/img/{name}.png") for name in 
                       ('lemon', 'watermelon', 'grapefruit', 'kiwifruit', 'nettedmelon', 'avocado')]   
    # 加载bling8.png图片，作为消除水果时的特效图片
    ASSETS["bling"] = load_image("static/img/bling8.png")
    ASSETS['single_score'] = [load_image(f"static/img/{name}.png") for name in 
                              ('good', 'great', 'excellent', 'unbelievable')]

    # 加载字体，如果加载失败则使用默认字体
    try:
        ASSETS["font_large"] = pygame.font.Font("static/font/zhengqingke.ttf", 43)
        ASSETS["font_small"] = pygame.font.Font("static/font/zhengqingke.ttf", 35)
    except:
        ASSETS["font_large"] = pygame.font.Font(None, 43)
        ASSETS["font_small"] = pygame.font.Font(None, 35)


class Manager:
    def __init__(self, screen):
        self.screen = screen  # 游戏窗口对象
        self.state = STATUS_START # 游戏状态：start, playing, game_over
        self.grid = [[-1] * WIDTH for _ in range(HEIGHT)] # 游戏矩阵，存储每个格子中的水果类型，-1表示空格

        self.score = 0 # 初始分数
        self.destroy_counts = [0] * 6 # 每种水果的消除数量
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
        self._score_recorded = True # 游戏是否需要记录分数的标志， 下划线表示私有变量，表示是类内部使用的变量，不应该被外部访问

        self.feedback_img = None # 游戏结束时的反馈图片
        self.feedback_timer = 0 # 游戏结束时的反馈图片显示时间

        self.end_img = None # 游戏结束时的图片
        self.end_timer = 0 # 游戏结束时的图片显示时间


        # 预计计算各个水果框所在位置
        self._cell_coords = {}
        for row in range(HEIGHT):
            for col in range(WIDTH):
                self._cell_coords[(row, col)] = \
                (MATRIX_TOPLEFT[0] + col * CELL_SIZE, MATRIX_TOPLEFT[1] + row * CELL_SIZE)

    def reset_game(self):
        # 初始化游戏数据
        self.reset_layout = True
        self.score = 0
        self.destroy_counts = [0] * 6
        self.runtime = 0
        self.start_time = pygame.time.get_ticks()  # 记录游戏开始时间
        self.time_is_over = False
        self.death_sign = False
        self.animating = False
        self.cur_sel = [-1, -1]
        self.last_sel = [-1, -1]
        self.exchange_status = -1
        self._score_recorded = False
        self.feedback_img = None
        self.feedback_timer = 0
        self.end_img = None
        self.end_timer = 0


    def go_to_score(self):
        # 记录总分分数并显示分数界面
        if not self._score_recorded:
            self.score_list.append(self.score)
            self._score_recorded = True
        self.state = STATUS_SCORE


    def xy_to_row_col(self, x, y):
        # 将鼠标点击的坐标转换为矩阵中的行列
        # 用鼠标点击的坐标减去矩阵左上角的坐标，再除以每个格子的大小，得到行列索引
        row = (y - MATRIX_TOPLEFT[1]) // CELL_SIZE
        col = (x - MATRIX_TOPLEFT[0]) // CELL_SIZE
        return row, col


    def handle_mouse(self, mouse_pos):
        if self.animating or self.end_timer > 0:  # 出现死局或正在播放消除动画时，不处理鼠标点击事件
            return
        
        x, y = mouse_pos
        if self.state == STATUS_START:
            if 300 < x < 600 and 250 < y < 370:
                self.state = STATUS_PLAYING
                self.reset_game()
        elif self.state == STATUS_SCORE:
            if 620 < x < 820 and 160 < y < 220:
                self.state = STATUS_PLAYING
                self.reset_game()
                return
            if 620 < x < 820 and 400 < y < 460:
                pygame.quit()
                sys.exit()
            if 20 < x < 83 and 530 < y < 590:
                self.go_to_score()
                return

        elif self.state == STATUS_PLAYING:
            if 620 < x < 820 and 160 < y < 220:
                self.state = STATUS_PLAYING
                self.reset_game()
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
                    if abs(row - self.last_sel[0]) + abs(col - self.last_sel[1]) == 1:
                        self.exchange_status = 1


    def reset_grid(self):
        if not self.reset_layout:
            return
        for i in range(HEIGHT):
            for j in range(WIDTH):
                self.grid[i][j] = random.randint(0, 5)  # 随机生成水果类型，0-5表示6种水果
        self.eliminate_all(animate=True)  # 消除所有可以消除的水果，确保初始布局没有可消除的水果
        self.reset_layout = False  # 重置标志位，避免重复生成

    def drop_fruits(self, animate=True):
        '''
        下落水果，填补空缺，animate为是否播放下落动画
        '''
        for col in range(WIDTH):
            column = [self.grid[row][col] for row in range(HEIGHT) if self.grid[row][col] != -2] # 获取当前列中未被消除的水果
            new_col = [random.randint(0, 5) for _ in range(HEIGHT - len(column))] + column # 新的一列是由随机生成的水果和未被消除的水果组成

            for row in range(HEIGHT):
                self.grid[row][col] = new_col[row]

        if animate:
            self.draw_grid_only()   # 绘制游戏矩阵中的水果
            pygame.display.flip()   # 更新屏幕显示
            pygame.time.delay(30)  # 延迟30毫秒，模拟下落动画的效果

    def draw_grid_only(self):
        """
        绘制游戏矩阵中的水果
        """
        for row in range(HEIGHT):
            for col in range(WIDTH):
                x, y = self._cell_coords[(row, col)]
                self.screen.blit(ASSETS['brick'], (x, y))
                val = self.grid[row][col]
                # 获取当前格子在屏幕上的坐标
                if val not in (-1, -2):  # 原始状态或已经消除的水果不参与绘制
                    self.screen.blit(ASSETS['fruit'][val], (x, y)) 

    def play_clear_animation(self,cleared):
        #消除动画的显示
        self.animating = True
        positions = [(r,c) for  r,c,_ in cleared]
        total_frames = 12
        bling_img = ASSETS['bling']

        for frame in range(total_frames):
            progress = frame / total_frames
            angle = progress * 360#旋转角度
            scale = 1.0 - progress#缩放比例

            for r, c in positions:
                x,y = self._cell_coords[(r,c)]
                self.screen.blit(ASSETS['brick'],(x,y))

            if scale >= 0.1:
                rotated = pygame.transform.rotozoom(bling_img,angle,scale)
                for r, c in positions:
                    x,y = self._cell_coords[(r,c)]
                    cx,cy = x + CELL_SIZE // 2, y + CELL_SIZE // 2
                    self.screen.blit(rotated, rotated.get_rect(center=(cx,cy)))

            pygame.display.flip()
            pygame.time.wait(20)
        self.animating = False

    def show_feedback(self, delta):
        '''
        显示分数增加的动画，delta为增加的分数
        '''
        if delta < 5:
            return
        elif delta < 10:
            self.feedback_img = ASSETS['single_score'][0]
        elif delta < 15:
            self.feedback_img = ASSETS['single_score'][1]
        elif delta < 25:
            self.feedback_img = ASSETS['single_score'][2]
        elif delta < 40:
            self.feedback_img = ASSETS['single_score'][3]
        else:
            self.feedback_img = ASSETS['single_score'][3]

        self.feedback_timer = 60  # 显示动画的时间，单位为帧数，60帧约等于1秒

    def check_horizontal(self, row, col):
        '''
        检测当前水果横向是否有三连，返回True或False
        '''
        if col > WIDTH - 3:
            return False
        val = self.grid[row][col]
        return val not in (-1, -2) and self.grid[row][col + 1] == val and self.grid[row][col + 2] == val
            
        
    def check_vertical(self, row, col):
        '''
        检测当前水果纵向是否有三连，返回True或False
        '''
        if row > HEIGHT - 3:
            return False
        val = self.grid[row][col]
        return val not in (-1, -2) and self.grid[row + 1][col] == val and self.grid[row + 2][col] == val
    
    def count_horizontal(self, row, col):
        '''
        计算当前水果横向有多少个相同的水果
        '''
        val, cnt = self.grid[row][col], 1
        for j in range(col + 1, WIDTH):
            if self.grid[row][j] == val:
                cnt += 1
            else:
                break
        return cnt

    def count_vertical(self, row, col):
        '''
        计算当前水果纵向有多少个相同的水果
        '''
        val, cnt = self.grid[row][col], 1
        for i in range(row + 1, HEIGHT):
            if self.grid[i][col] == val:
                cnt += 1
            else:
                break
        return cnt
            
    def eliminate_all(self, animate=True):
        # animate=True 默认消除时要显示消除动画
        """
        ### 遍历矩阵，把所有能消除的水果全部标记、消除、生成新的水果、算分、显示激励图片
        主要逻辑：
        先对分数进行copy、标记一个changed变量为True，表示有水果被消除
        然后进入while循环，循环条件为changed为True，表示还有水果可以消除
        在循环之中遍历矩阵、去掉空位和已消除位置
        横向遍历，若检测函数check_horizontal()返回True，
        则调用count_horizontal()函数计算横向有多少个相同的水果，并
        将这些水果的位置加入to_clear列表中，同时更新destroy_counts字典，记录每种水果的消除数量
        纵向遍历，若检测函数check_vertical()返回True，
        则调用count_vertical()函数计算纵向有多少个相同的水果，
        并将这些水果的位置加入to_clear列表中，同时更新destroy_counts字典，记录每种水果的消除数量
        遍历完矩阵后，若to_clear列表不为空，则表示有水果需要消除
        将to_clear列表中的水果位置在矩阵中标记为已消除状态(-2),
        最后如果检测到有水果消除，则调用play_clear_animation()函数播放消除动画，
        然后调用drop_fruits()函数让水果下落，填补空缺
        并且有动画播放、则调用show_feedback()函数显示分数增加的动画
        """
        prev_score = self.score
        changed = True
        while changed:
            changed = False
            to_clear = []  # 存储需要消除的水果位置
            
            for row in range(HEIGHT):
                for col in range(WIDTH):
                    val = self.grid[row][col]
                    if val in (-1, -2):  # 原始状态或已经消除的水果不参与检测
                        continue
                    if self.check_horizontal(row, col):
                        cnt = self.count_horizontal(row, col) # 数横向一共有几个相同的水果
                        for k in range(cnt):
                            to_clear.append((row, col + k, val))  # 将需要消除的水果位置加入列表
                        self.destroy_counts[val] += cnt  # 更新消除数量
                        changed = True
                    if self.check_vertical(row, col):
                        cnt = self.count_vertical(row, col)
                        for k in range(cnt):
                            to_clear.append((row + k, col, val))  # 将需要消除的水果位置加入列表
                        self.destroy_counts[val] += cnt  # 更新消除数量
                        changed = True

            for row, col, _ in to_clear:
                self.grid[row][col] = -2  # 标记为已消除状态

            if changed:
                if animate:
                    self.play_clear_animation(to_clear)  # 播放消除动画
                self.drop_fruits(animate=animate)  # 下落水果，填补空缺

            self.calc_score()  # 计算分数
            if animate:
                delta = self.score - prev_score
                self.show_feedback(delta)  # 显示分数增加的动画

    def calc_score(self):
        # 计算分数
        """
        用enumerate()函数遍历destroy_counts列表，获取每种水果的索引i和消除数量cut，
        然后将每种水果的消除数量乘以对应的分数SCORE_PER_FRUIT[i]，最后将所有水果的分数相加得到总分
        """
        self.score = sum(cut * SCORE_PER_FRUIT[i] for i , cut in enumerate(self.destroy_counts))

    def has_match(self):
        # 检测当前矩阵中是否有可以消除的水果，返回True或False
        """
        检测游戏矩阵中是否有三连，允许横竖
        """
        for row in range(HEIGHT):
            for col in range(WIDTH):
                val = self.grid[row][col]
                if val in (-1, -2): # 原始状态或已经消除的水果不参与检测
                    continue
                # 检测横向三连
                """
                具体逻辑为：
                1. 检查当前水果的列索引是否小于等于WIDTH - 3，确保有足够的空间检查右边两个水果
                2. 检查当前水果的右边两个水果是否与当前水果类型，通过右侧两个水果的列索引分别为col + 1和col + 2，
                判断它们的类型是否与当前水果类型相同
                3. 如果满足以上两个条件，则说明当前水果与右边两个水果形成
                """
                if self.check_horizontal(row, col):
                    return True
                # 检测纵向三连
                if self.check_vertical(row, col):
                    return True
        return False  # 没有找到可以消除的水果，返回False
        
    def swap_fruits(self, p1, p2):
        # 交换水果位置
        r1, c1 = p1
        r2, c2 = p2
        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]

    def process_swap(self):
        # 处理水果交换逻辑, 判断能不能消除，记录消除哪些水果，分别积分是多少，还有没有连锁消除，积分
        # 一次完整的交换：交换、检测、消除、还原
        p1, p2 = self.last_sel, self.cur_sel
        self.swap_fruits(p1, p2)  # 交换两个水果

        if not self.has_match():
            self.swap_fruits(p1, p2)  # 如果没有消除，交换回来
        else:
            self.eliminate_all(animate=True)  # 如果有消除，播放消除动画 eliminate_all()函数会处理消除逻辑，包括计算分数、更新游戏状态等,这个函数还未实现
        
        self.last_sel = self.cur_sel = [-1, -1]  # 重置选中水果位置
        self.exchange_status = -1  # 重置交换状态

    def is_dead_map(self):
        # 判断游戏是否出现死局，返回死局的数量
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if self.grid[i][j] in (-1, -2):  # 原始状态或已经消除的水果不参与检测
                    continue

                # 尝试交换当前水果与右边的水果
                if j < WIDTH - 1:
                    self.swap_fruits((i, j), (i, j + 1))
                    if self.has_match():
                        self.swap_fruits((i, j), (i, j + 1))  # 交换回来
                        return False  # 有可消除的水果，返回False
                    self.swap_fruits((i, j), (i, j + 1))  # 交换回来

                # 尝试交换当前水果与下边的水果
                if i < HEIGHT - 1:
                    self.swap_fruits((i, j), (i + 1, j))
                    if self.has_match():
                        self.swap_fruits((i, j), (i + 1, j))  # 交换回来
                        return False  # 有可消除的水果，返回False
                    self.swap_fruits((i, j), (i + 1, j))  # 交换回来

        return True  # 没有可消除的水果，返回True，表示出现死局

    def show_end_image(self, img):
        # 显示游戏结束的图片，img为图片名称
        if img == 'time_up':
            self.end_img = ASSETS["time_is_over"]
        elif img == 'dead':
            self.end_img = ASSETS["no_fruit"]
        self.end_timer = 90  # 显示图片的时间，单位为帧数 1s为 60帧，90帧约等于1.5秒 一帧大概为0.167s

    def update(self):
        # 根据游戏状态更新游戏逻辑
        if self.state != STATUS_PLAYING:
            return
        # 初始化游戏框中的水果
        self.reset_grid()

        # 水果可交换
        if self.exchange_status == 1 and not self.animating and self.end_timer == 0:
            self.process_swap()  # 处理水果交换逻辑

        # 激励图片
        if self.feedback_timer >= 0:
            self.feedback_timer -= 1

        """
        # 游戏结束的处理逻辑
        主要逻辑线路
        self.time_is_over,self.end_timer(), self.death_sign() 这几个函数分别对应三个游戏结束的标志位
        在这三个标志位中，只有一个会被触发，触发后会显示对应的图片，调用show_end_image函数展示图片并且设置end_timer为90帧，表示图片显示的时间
        然后在update()函数中，每帧都会检查end_timer是否大于0，如果大于0，则end_timer减1，当end_timer减到0时，表示图片显示完毕，此时会调用go_to_score()函数，进入分数界面
        这样就实现了游戏结束后，先显示对应的图片，然后再进入分数界面的逻辑。
        """

        # 时间到 
        self.running_time = pygame.time.get_ticks() - self.start_time  # 计算游戏运行时间使用pygame中的get_ticks()函数获取当前时间，减去游戏开始时间，得到游戏运行时间
        if self.running_time >= GAME_TIME and not self.time_is_over:
            self.time_is_over = True
            self.show_end_image('time_up') # 显示时间到的图片

        #死图
        if not self.time_is_over and not self.death_sign and self.end_timer == 0:
            self.death_sign = self.is_dead_map()
            if self.death_sign:
                self.show_end_image('dead') # 显示死图的图片

        # 时间到和死图的图片显示完成后如何处理
        if self.end_timer > 0:
            self.end_timer -= 1
            if self.end_timer == 0 and not self._score_recorded:
                self.go_to_score() # 显示分数界面
            return
        
    def draw(self):
        # 根据游戏状态绘制不同的界面
        # blit()函数是pygame中用于绘制图像的方法，第一个参数是要绘制的图像，第二个参数是图像在屏幕上的位置坐标
        if self.state == STATUS_START:
            self.screen.blit(ASSETS["bg_tree"], (0, 0))
            self.screen.blit(ASSETS["game_start_button"], (300, 250))
        
        elif self.state == STATUS_PLAYING:
            self.screen.blit(ASSETS["bg_playing"], (0, 0))
            self.screen.blit(ASSETS["exit"], (20, 530))
            self.screen.blit(ASSETS["board_score"], (736, 15))

            s = str(self.score)
            for i,ch in enumerate(s):
                self.screen.blit(ASSETS["digit"][int(ch)], (755 + i * 30, 40))
            self.draw_grid_only()  # 绘制游戏矩阵中的水果

            if not self.time_is_over:
                remain = max(0, GAME_TIME - self.running_time) // 1000
                m, s = divmod(remain, 60) # 计算remain的分钟数和秒数，divmod()函数返回两个数相除的商和余数，分别对应分钟和秒数
                surf = ASSETS["font_large"].render(f"{m:02d}:{s:02d}", True, (0, 0, 0)) # 使用pygame的字体渲染函数render()将时间字符串渲染为图像，True表示抗锯齿，(255, 255, 255)表示白色
                self.screen.blit(surf, (59, 46)) # 将渲染后的时间图像绘制到屏幕上，位置为(59, 46)     

            if self.cur_sel != [-1, -1]:
                row, col = self.cur_sel
                x, y = self._cell_coords[(row, col)]
                self.screen.blit(ASSETS["frame"], (x, y)) # 绘制选中水果的边框

            if self.feedback_img and self.feedback_timer > 0:
                fw, fh = self.feedback_img.get_size()
                fx = SCREEN_SIZE[0] // 2 - fw // 2
                fy = MATRIX_TOPLEFT[1] - fh - 12
                self.screen.blit(self.feedback_img, (fx, fy))

            if self.end_img and self.end_timer > 0:
                w, h = self.end_img.get_size()
                cx, cy = SCREEN_SIZE[0] // 2 - w // 2, SCREEN_SIZE[1] // 2 - h // 2
                self.screen.blit(self.end_img, (cx, cy)) # 绘制结束提示图
            
        elif self.state == STATUS_SCORE:
                self.screen.blit(ASSETS["bg_score"], (0, 0))
                top = sorted(self.score_list, reverse=True)[:8]  # 取前八名分数
                for i, score in enumerate(top):
                    surf = ASSETS["font_small"].render(f"{i + 1}. {score}", True, (0, 0, 0))
                    self.screen.blit(surf, (370, 125 + i * 50)) # 绘制分数列表，位置为(370, 125 + i * 50)           

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