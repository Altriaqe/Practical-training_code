import pygame
from pygame.locals import *
import time
import random
from functools import lru_cache # 缓存相关
from .base import Base
from .entity import Element, Font_Fact

class Manager(Base):
    """
    游戏进行中的管理
    """
    stop_width = 63           # 正方形 退出 按钮 的 边长
    reset_layout = True       # 重新 布局元素的标志
    cur_sel = [-1, -1]        # 当前选中的 小方块, 值为 矩阵 索引
    score = 0                 # 游戏得分
    # 消除水果列表：消除各小水果的个数
    destory_animal_num = [0, 0, 0, 0, 0, 0]
    # 计分规则列表:  消除每一类水果所得的分数
    every_animal_score = [1, 2, 1, 1, 2, 1]
    last_sel = [-1, -1]       # 上一次选中的水果, 值为水果索引
    exchange_status = -1      # 交换的 标志， 1: 代表交换 ， -1: 不交换
    score_list = []           # 排行榜存储分数列表
    death_sign =  True        # 死图标志，初始不是死图

    TIMEOUT = 1000 * 60 * 3   # 每场游戏的规定时长
    start_time = 0            # 每场游戏的开始时间
    end_time = 0              # 每场游戏的时间
    running_time = 0          # 每场游戏的运行时间, 毫秒
    time_is_over = False      # 每场游戏的时间状态控制


    def __init__(self):
        super(Manager, self).__init__()
        # 水果矩阵： 存储每个小方块中所要绘制的水果的编号(0 - 5),
        # -1 代表不画， -2 代表将要消除
        self.animal = [[-1 for i in range(self._width)] for j in range(self._height)]

    def start_game_init(self):
        """ 游戏 页面 绘制  """
        # 绘制 打怪 的 背景
        Element(Element.bg_start_image, (0, 0)).draw(self.screen)
        # 绘制 暂停键
        Element(Element.stop, Element.stop_position).draw(self.screen)
        # 绘制 显示 分数的 板子
        score_board = Element(Element.board_score, Element.score_posi)
        score_board.draw(self.screen)
        # 绘制 游戏分数
        str_score = str(self.score)
        for k, sing in enumerate(str_score):
             Element(Element.score[int(sing)], (755 + k * 32, 40)).draw(self.screen)
        # 创建 小方块背景图片 精灵 组
        BrickSpriteGroup = pygame.sprite.Group()
        # 创建 水果 精灵 组
        AnimalSpriteGroup = pygame.sprite.Group()
        # 向精灵组中 添加 精灵
        for row in range(self._height):
            for col in range(self._width):
                x, y = self.cell_xy(row, col)
                BrickSpriteGroup.add(Element(Element.brick, (x, y)))
                if self.animal[row][col] != -2:
                    AnimalSpriteGroup.add(Element(Element.animal[self.animal[row][col]], (x, y)))
        # 绘制 小方块 的 背景 图
        BrickSpriteGroup.draw(self.screen)
        # 绘制 小方块 中 的 水果
        for ani in AnimalSpriteGroup:
            self.screen.blit(ani.image, ani.rect)
        # 绘制 鼠标所点击的 水果的 突出显示边框
        if self.cur_sel != [-1, -1]:
            frame_sprite = Element(Element.frame_image, self.cell_xy(self.cur_sel[0], self.cur_sel[1]))
            self.screen.blit(frame_sprite.image, frame_sprite.rect)
        # 绘制游戏倒计时时间
        if not self.time_is_over:
            if self.running_time <= self.TIMEOUT:
                try:
                    time_str = time.strftime("%X", time.localtime(self.TIMEOUT // 1000 - self.running_time // 1000)).partition(":")[2]
                    Font_Fact(time_str, Font_Fact.show_time_posi, 43, (0, 0, 0)).draw(self.screen)
                except Exception as e:
                    pass
        else:
            time_str = "00:00"
            Font_Fact(time_str, Font_Fact.show_time_posi, 43, (0, 0, 0)).draw(self.screen)

        pygame.display.flip()  # 更新页面显示， 必须添加

        return AnimalSpriteGroup

    def clear_ele(self):
        """ 清除 标记 元素 ， 且 上方元素 向下 坠落  """
        single_score = self.score
        self.change_value_sign = False
        for i in range(self._height):
            for j in range(self._width):
                if self.exist_right(i, j, 5):
                    self.change_value_sign = True
                    if self.exist_down(i, j + 2, 3):
                        # 记录 消除 的 水果 数量
                        self.destory_animal_num[self.animal[i][j]] += 7
                        # 对矩阵中消除的水果位置标记清除为 -2 , 代表将被消除
                        self.change_right(i, j, 5)
                        self.change_down(i, j + 2, 3)
                    else:
                        self.destory_animal_num[self.animal[i][j]] += 5
                        self.change_right(i, j, 5)
                elif self.exist_right(i, j, 4):
                    self.change_value_sign = True
                    if self.exist_down(i, j + 1, 3):
                        self.destory_animal_num[self.animal[i][j]] += 6
                        self.change_right(i, j, 4)
                        self.change_down(i, j + 1, 3)
                    elif self.exist_down(i, j, 3):
                        self.destory_animal_num[self.animal[i][j]] += 6
                        self.change_right(i, j, 4)
                        self.change_down(i, j, 3)
                    else:
                        self.destory_animal_num[self.animal[i][j]] += 4
                        self.change_right(i, j, 4)
                elif self.exist_right(i, j, 3):
                    self.change_value_sign = True
                    if self.exist_down(i, j, 3):
                        self.destory_animal_num[self.animal[i][j]] += 5
                        self.change_right(i, j, 3)
                        self.change_down(i, j, 3)
                    elif self.exist_down(i, j + 1, 3):
                        self.destory_animal_num[self.animal[i][j]] += 5
                        self.change_right(i, j, 3)
                        self.change_down(i, j + 1, 3)
                    elif self.exist_down(i, j + 2, 3):
                        self.destory_animal_num[self.animal[i][j]] += 5
                        self.change_right(i, j, 3)
                        self.change_down(i, j + 2, 3)
                    else:
                        self.destory_animal_num[self.animal[i][j]] += 3
                        self.change_right(i, j, 3)
                elif self.exist_down(i, j, 5):
                    self.change_value_sign = True
                    if self.exist_right(i + 2, j, 3):
                        self.destory_animal_num[self.animal[i][j]] += 7
                        self.change_down(i, j, 5)
                        self.change_right(i + 2, j, 3)
                    elif self.exist_left(i + 2, j, 3):
                        self.destory_animal_num[self.animal[i][j]] += 7
                        self.change_down(i, j, 5)
                        self.change_left(i + 2, j, 3)
                    else:
                        self.destory_animal_num[self.animal[i][j]] += 5
                        self.change_down(i, j, 5)
                elif self.exist_down(i, j, 4):
                    self.change_value_sign = True
                    if self.exist_right(i + 1, j, 3):
                        self.destory_animal_num[self.animal[i][j]] += 6
                        self.change_down(i, j, 4)
                        self.change_right(i + 1, j, 3)
                    elif self.exist_left(i + 1, j, 3):
                        self.destory_animal_num[self.animal[i][j]] += 6
                        self.change_down(i, j, 4)
                        self.change_left(i + 1, j, 3)
                    elif self.exist_right(i + 2, j, 3):
                        self.destory_animal_num[self.animal[i][j]] += 6
                        self.change_down(i, j, 4)
                        self.change_right(i + 2, j, 3)
                    elif self.exist_left(i + 2, j, 3):
                        self.destory_animal_num[self.animal[i][j]] += 6
                        self.change_down(i, j, 4)
                        self.change_left(i + 2, j, 3)
                    else:
                        self.destory_animal_num[self.animal[i][j]] += 4
                        self.change_down(i, j, 4)
                elif self.exist_down(i, j, 3):
                    self.change_value_sign = True
                    if self.exist_right(i + 1, j, 3):
                        self.destory_animal_num[self.animal[i][j]] += 5
                        self.change_down(i, j, 3)
                        self.change_right(i + 1, j, 3)
                    elif self.exist_left(i + 1, j, 3):
                        self.destory_animal_num[self.animal[i][j]] += 5
                        self.change_down(i, j, 3)
                        self.change_left(i + 1, j, 3)
                    elif self.exist_right(i + 2, j, 3):
                        self.destory_animal_num[self.animal[i][j]] += 5
                        self.change_down(i, j, 3)
                        self.change_right(i + 2, j, 3)
                    elif self.exist_left(i + 2, j, 3):
                        self.destory_animal_num[self.animal[i][j]] += 5
                        self.change_down(i, j, 3)
                        self.change_left(i + 2, j, 3)
                    elif self.exist_left(i + 2, j, 2) and self.exist_right(i + 2, j, 2):
                        self.destory_animal_num[self.animal[i][j]] += 5
                        self.change_down(i, j, 3)
                        self.change_left(i + 2, j, 2)
                        self.change_right(i + 2, j, 2)
                    elif self.exist_left(i + 2, j, 2) and self.exist_right(i + 2, j, 3):
                        self.destory_animal_num[self.animal[i][j]] += 6
                        self.change_down(i, j, 3)
                        self.change_left(i + 2, j, 2)
                        self.change_right(i + 2, j, 3)
                    elif self.exist_left(i + 2, j, 3) and self.exist_right(i + 2, j, 2):
                        self.destory_animal_num[self.animal[i][j]] += 6
                        self.change_down(i, j, 3)
                        self.change_left(i + 2, j, 3)
                        self.change_right(i + 2, j, 2)
                    elif self.exist_left(i + 2, j, 3) and self.exist_right(i + 2, j, 3):
                        self.destory_animal_num[self.animal[i][j]] += 7
                        self.change_down(i, j, 3)
                        self.change_left(i + 2, j, 3)
                        self.change_right(i + 2, j, 3)
                    else:
                        self.destory_animal_num[self.animal[i][j]] += 3
                        self.change_down(i, j, 3)

        self.drop_animal()               # 下降函数
        
        self.cal_score(self.destory_animal_num) # 计算分数

        # 根据此次交换 获得的分数 绘制 不同的 鼓励的 语句
        single_score = self.score - single_score

        if single_score < 5:
            pass
        elif single_score < 8:   # 绘制 Good
            Element(Element.single_score[0], (350, 250)).draw(self.screen)
            pygame.display.flip()
            pygame.time.delay(500)
        elif single_score < 10:  # 绘制 Great
            Element(Element.single_score[1], (350, 250)).draw(self.screen)
            pygame.display.flip()
            pygame.time.delay(500)
        elif single_score < 15:  # 绘制 Amazing
            Element(Element.single_score[2], (350, 250)).draw(self.screen)
            pygame.display.flip()
            pygame.time.delay(500)
        elif single_score < 20:  # 绘制 Excellent
            Element(Element.single_score[3], (350, 250)).draw(self.screen)
            pygame.display.flip()
            pygame.time.delay(500)
        elif single_score >= 20:  # 绘制 Unbelievable
            Element(Element.single_score[4], (350, 250)).draw(self.screen)
            pygame.display.flip()
            pygame.time.delay(500)

        return self.change_value_sign


    def drop_animal(self):
        """ 水果掉落函数  """
        clock = pygame.time.Clock()

        position = []          # 水果矩阵中要消除的水果列表
        for i in range(self._width):
            for j in range(self._height):
                if self.animal[i][j] == -2:
                    x, y = self.cell_xy(i, j)
                    position.append((x, y))
        # 绘制 消除小方块的 消除效果
        if position != []:
            for index in range(0, 9):
                # clock.tick(40)
                for pos in position:
                    Element(Element.brick, pos).draw(self.screen)
                    Element(Element.bling[index], (pos[0], pos[1])).draw(self.screen)
                    pygame.display.flip()

        for i in range(self._width):
            # 此行之上所有要降落的水果的背景图片列表
            brick_position = []
            # 此行之上所有要降落的水果列表
            fall_animal_list = []
            speed = [0, 1]
            for j in range(self._height):
                if self.animal[i][j] == -2:
                    x, y = self.cell_xy(i, j)
                    brick_position.append((x, y))
                    for m in range(i, -1, -1):
                        if m == 0:  # 此列中最上方的水果(补缺)
                            self.animal[m][j] = random.randint(0, 5)
                        else:
                            x, y = self.cell_xy(m - 1, j)
                            brick_position.append((x, y))
                            animal = Element(Element.animal[self.animal[m - 1][j]], (x, y))
                            fall_animal_list.append(animal)
                            # 在水果矩阵列表中交换上下两个水果。
                            self.animal[m][j] = self.animal[m - 1][j]
            # 移动所消除的小方块的上方的小方块向下移动
            while speed != [0, 0] and fall_animal_list != []:
                # 绘制水果的背景图片
                for position in brick_position:
                    Element(Element.brick, position).draw(self.screen)
                # 向下移动水果
                for animal_sprite in fall_animal_list:
                    animal_sprite.move(speed)
                    animal_sprite.draw(self.screen)
                    speed = animal_sprite.speed
                pygame.display.flip()


    def exchange_ele(self, AnimalSpriteGroup):
        """  交换 鼠标 前后 点击的 两个 元素  """
        if self.exchange_status == -1:
            self.last_sel = self.cur_sel
        if self.exchange_status == 1:
            last_x, last_y = self.cell_xy(*self.last_sel)
            cur_x, cur_y = self.cell_xy(*self.cur_sel)
            # 左右 相邻
            if self.last_sel[0] == self.cur_sel[0]:  # 比较的是矩阵索引
                for animal_sur in AnimalSpriteGroup:
                    if animal_sur.rect.topleft == (last_x, last_y):
                        last_sprite = animal_sur
                        last_sprite.speed = [self.cur_sel[1] - \
                                             self.last_sel[1], 0]
                    if animal_sur.rect.topleft == (cur_x, cur_y):
                        cur_sprite = animal_sur
                        cur_sprite.speed = [self.last_sel[1] - \
                                            self.cur_sel[1], 0]
            # 上下 相邻
            elif self.last_sel[1] == self.cur_sel[1]:
                for animal_sur in AnimalSpriteGroup:
                    if animal_sur.rect.topleft == (last_x, last_y):
                        last_sprite = animal_sur
                        last_sprite.speed = [0, self.cur_sel[0] - \
                                             self.last_sel[0]]
                    if animal_sur.rect.topleft == (cur_x, cur_y):
                        cur_sprite = animal_sur
                        cur_sprite.speed = [0, self.last_sel[0] - \
                                            self.cur_sel[0]]
            # 移动水果
            while last_sprite.speed != [0, 0]:
                pygame.time.delay(5)
                Element(Element.brick, (last_x, last_y)).draw(self.screen)
                Element(Element.brick, (cur_x, cur_y)).draw(self.screen)
                last_sprite.move(last_sprite.speed)
                cur_sprite.move(cur_sprite.speed)
                last_sprite.draw(self.screen)
                cur_sprite.draw(self.screen)
                pygame.display.flip()

            self.change_value()        # 交换 水果 值
            if not self.clear_ele():   # 交换 后 若 不存在消除， 则 归位
                self.change_value()
            self.exchange_status = -1  # 关闭交换
            self.cur_sel = [-1, -1]    # 保证 每次 交换的 两个元素 不 存在交叉


    def change_value(self):
        """ 交换水果 """
        temp = self.animal[self.last_sel[0]][self.last_sel[1]]
        self.animal[self.last_sel[0]][self.last_sel[1]] \
            = self.animal[self.cur_sel[0]][self.cur_sel[1]]
        self.animal[self.cur_sel[0]][self.cur_sel[1]] = temp


    def mouse_select(self, event):
        """  游戏 页面 事件监听  """
        if event.type == MOUSEBUTTONDOWN: # 鼠标按下事件
            mouse_x, mouse_y = event.pos  # 获取当前鼠标的坐标
            if self.status == 1:
                # 判断点击的是水果
                if self.matrix_topleft[0] < mouse_x < \
                    self.matrix_topleft[0] + self._cell_size * self._width \
                    and self.matrix_topleft[1] < mouse_y < \
                    self.matrix_topleft[1] + self._cell_size * self._height:
                    mouse_selected = self.xy_cell(mouse_x, mouse_y)
                    # 记录当前鼠标点击的 小方块
                    self.cur_sel = mouse_selected

                    # 判断前后点击的两个水果是否相邻
                    if (self.last_sel[0] == self.cur_sel[0] and \
                        abs(self.last_sel[1] - self.cur_sel[1]) == 1) or\
                            (self.last_sel[1] == self.cur_sel[1] and \
                             abs(self.last_sel[0] - self.cur_sel[0]) == 1):
                        self.exchange_status = 1  # 确定相邻， 交换值

                # 判断点击的是退出按钮, 需注意此退出按钮的坐标为左上角
                elif Element.stop_position[0] < mouse_x < \
                    Element.stop_position[0] + Manager.stop_width \
                    and Element.stop_position[1] < mouse_y < \
                    Element.stop_position[1] + Manager.stop_width:
                    # 不可为  self.status  = 2, 不理解请移步 python 面向对象 章节
                    Base.status = 2
                    self.reset_layout = True  # 布局 下一盘 游戏的 元素
                else:
                    self.cur_sel = [-1, -1]  # 处理无效的 点击

    # 缓存 调用此函数不同参数时的结果
    @lru_cache(None)  # 必须要有 一个 参数， None 代表 不限
    def cell_xy(self, row, col):
        """ 矩阵索引 转  坐标 """
        return int(Base.matrix_topleft[0] + col * Base._cell_size), \
               int(Base.matrix_topleft[1] + row * Base._cell_size)

    @lru_cache(None)
    def xy_cell(self, x, y):
        """ 坐标 转 矩阵索引 """
        return int((y - Base.matrix_topleft[1]) / Base._cell_size), \
               int((x - Base.matrix_topleft[0]) / Base._cell_size)

    def reset_animal(self):
        """ 对矩阵中的小方块 随机 分配 水果 """
        if self.reset_layout:
            for i in range(self._height):
                for j in range(self._width):
                    self.animal[i][j] = random.randint(0, 5)
        self.reset_layout = False

    def exist_right(self, row, col, num):
        """ 判断 self.animal[i][j] 元素  右边  是否存在与其自身
            图像相同的 num - 1 个  图像 """
        if col <= self._width - num:
            for item in range(num):
                if self.animal[row][col] != self.animal[row][col + item] \
                        or self.animal[row][col] == -2:
                    break
            else:
                return True
            return False
        else:
            return False

    def exist_down(self, row, col, num):
        """ 判断 self.animal[i][j] 元素  下方是否存在与其
            自身图像 相同的 num - 1 个  图像 """
        if row <= self._height - num:
            for item in range(num):
                if self.animal[row][col] != self.animal[row + item][col] \
                        or self.animal[row][col] == -2:
                    break
            else:
                return True
            return False
        else:
            return False

    def exist_left(self, row, col, num):
        """ 判断 self.animal[i][j] 元素  左方  是否存在与其
            自身图像相同的 num - 1 个  图像 """
        if col >= num - 1:
            for item in range(num):
                if self.animal[row][col] != self.animal[row][col - item] \
                        or self.animal[row][col] == -2:
                    break
            else:
                return True
            return False
        else:
            return False

    def change_right(self, row, col, num):
        """ 改变 当前水果及 右边的 num 个水果 为 消除 状态 """
        for item in range(num):
            self.animal[row][col + item] = -2

    def change_down(self, row, col, num):
        for item in range(num):
            self.animal[row + item][col] = -2

    def change_left(self, row, col, num):
        for item in range(num):
            self.animal[row][col - item] = -2

    def cal_score(self, destory_animal_num):
        """ 统计当前分数 """
        self.score = 0
        for k, num in enumerate(destory_animal_num):
            self.score += self.every_animal_score[k] * num

    def record_score(self):
        """ 记录每场游戏得分 """
        if self.score != 0:
            self.score_list.append(self.score)
            self.destory_animal_num = [0, 0, 0, 0, 0, 0]
            self.score = 0     # 分数 复位 归零




    def is_death_map(self):
        """ 判断 当前 是否 为 死图  """
        for i in range(self._width):
            for j in range(self._height):
                # 边界判断
                if i >= 1 and j >= 1 and i <= 7 and j <= 6:
                    if self.animal[i][j] == self.animal[i][j + 1]:
                        """e     b
                             e e 
                           b     e
                        """
                    if (self.animal[i][j] in [self.animal[i - 1][j - 1], \
                                              self.animal[i + 1][j - 1]] \
                        and self.animal[i][j - 1] != -1) or \
                            (self.animal[i][j] in [self.animal[i - 1][j + 2], \
                                                   self.animal[i + 1][j + 2]] \
                             and self.animal[i][j + 2] != -1):
                        self.death_sign = False
                        break

                if i >= 1 and j >= 1 and i <= 6 and j <= 7:
                    if self.animal[i][j] == self.animal[i + 1][j]:
                        if (self.animal[i][j] in [self.animal[i - 1][j - 1], \
                                                  self.animal[i - 1][j + 1]] \
                            and self.animal[i - 1][j] != -1) or \
                                (self.animal[i][j] in [self.animal[i + 2][j - 1], \
                                                       self.animal[i + 2][j + 1]] \
                                 and self.animal[i + 2][j] != -1):
                            """e   b
                                 e
                                 e 
                               c   e"""
                            self.death_sign = False
                            break

                elif i >= 1 and j >= 1 and i <= 7 and j <= 7:
                    if self.animal[i - 1][j - 1] == self.animal[i][j]:
                        if (self.animal[i][j] == self.animal[i - 1][j + 1] \
                            and self.animal[i - 1][j] != -1) \
                                or (self.animal[i][j] == self.animal[i + 1][j - 1] \
                                    and self.animal[i][j - 1] != -1):
                            """e   e      e   b
                                 e          e
                               c          e    """
                            self.death_sign = False
                            break

                    if self.animal[i][j] == self.animal[i + 1][j + 1]:
                        if (self.animal[i][j] == self.animal[i - 1][j + 1] \
                            and self.animal[i][j + 1] != -1) \
                                or (self.animal[i][j] == self.animal[i + 1][j - 1] \
                                    and self.animal[i + 1][j] != -1):
                            """    e          b
                                 e          e
                               b   e      e   e"""
                            self.death_sign = False
                            break


    def judge_time(self):
        """ 判断 游戏时间 是否超时  """
        self.end_time = pygame.time.get_ticks() # 更新结束时间
        # 避免 在 self.status = 2 的 情况下更新 self.end_time ,
        # 从而使 self.time_is_over == True
        if self.status == 1:
            self.running_time = self.end_time - self.start_time
            if self.running_time >= self.TIMEOUT:
                self.time_is_over = True



    def stop_game(self):
        """ 结束 本场游戏， 进入 排行榜 的界面  """
        if self.status == 1:
            # 游戏死图
            if self.death_sign:
                pygame.time.delay(500)
                Element(Element.none_animal, Element.none_animal_posi).draw(self.screen)
                pygame.display.flip()
                pygame.time.delay(500)
                Base.status = 2           # 需要为  Base.status  = 2, 结束本场游戏
                self.reset_layout = True  # 布局下一盘游戏的元素
                self.time_is_over = False
            else:
                self.death_sign = True
            # 游戏超时
            if self.time_is_over:
                pygame.time.delay(600)  # 暂停程序一段时间
                # 绘制 "时间到了" 图片
                Element(Element.time_is_over_image, Element.time_is_over_posi).draw(self.screen)
                pygame.display.flip()
                pygame.time.delay(1300)   # 暂停程序一段时间, 避免 "game over" 图片 一闪而过.
                Base.status = 2           # 需要为  Base.status  = 2, 结束本场 游戏
                self.reset_layout = True  # 布局 下一盘 游戏的 元素
                self.time_is_over = False

