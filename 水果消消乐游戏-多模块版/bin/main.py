import sys
import pygame
from pygame.locals import *
from core.first_eye import Screen_Manager
#  core包，文件夹，first_eye.py模块 ，Screen_Manager类
from core.handler import Manager
from core.sort_score import Score_Manager

def main():
    """
    消消乐 游戏主 函数
    :return:
    """
    pygame.init()             # 设备的检测
    pygame.font.init()        # 字体文件的初始化

    # 在 这里 创建 每一个 页面类的对象
    mr = Screen_Manager()     # 实例化首屏页面管理对象
    mg = Manager()            # 实例化打怪页面管理对象
    ms = Score_Manager()      # 实例化排行榜页面管理对象

    while 1:
        mg.judge_time()  # 判断游戏超时
        # 在这里 判断不同的游戏状态，从而执行 不同的 具体操作
        if mr.status == 0:           # 游戏 首屏 状态
            mr.open_game_init()

        if mg.status == 1:           # 游戏打怪状态
            mg.reset_animal()        # 随机分配元素
            # 绘制打怪页面
            AnimalSpriteGroup = mg.start_game_init()
            mg.clear_ele()  # 标记清除
            mg.is_death_map() # 死图判断
            mg.exchange_ele(AnimalSpriteGroup)  # 元素交换
        mg.stop_game()               # 结束游戏

        if ms.status == 2:           # 游戏排行榜状态
            mg.record_score()        # 记录本场游戏得分， 并分数清零
            ms.choice_game_init()

        for event in pygame.event.get():  # 事件的监听与循环
            if event.type == KEYDOWN:
                if event.key == K_q or event.key == K_ESCAPE:
                    sys.exit()
            if event.type == QUIT:
                sys.exit()
            # 在这里 进行不同页面的事件监听，从而改变游戏状态
            mg.mouse_select(event)  # 对游戏打怪页面的事件监听
            ms.mouse_select(event)  # 对游戏排行榜页面的事件监听
            mr.mouse_select(event)  # 对 游戏首屏 的 事件监听

















