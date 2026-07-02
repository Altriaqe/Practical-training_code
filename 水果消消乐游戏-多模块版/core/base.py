import pygame

class Base:#基类   ：继承特性：面向对象的核心方法之一
    """
    一些 公共的 变量的 管理
    定义了 游戏的 窗口对象， 窗口的尺寸， 游戏的状态， 矩阵的尺寸， 矩阵的左上顶点坐标和 矩阵中每个小方块的边长窗口对象
    """

    clock = pygame.time.Clock()  # 创建一个对象来帮助跟踪时间,
    _screen_size = (900, 600)    # 屏幕 的 尺寸
    # 0: 首屏状态， 1: 打怪状态  2: 排行榜状态
    status = 0                   # 游戏状态

    _cell_size = 50              # 矩阵中每个小方块为边长为 50 的正方形，_代表私有变量，外部不能直接访问
    _width = 9                   # 矩阵的行数
    _height = 9                  # 矩阵的列数
    matrix_topleft = (250, 100)  # 矩阵的 左上顶点坐标


    def __init__(self):
        # 窗口对象的获取
        self.screen = pygame.display.set_mode(self._screen_size)
        # 设置窗口的标题
        pygame.display.set_caption("水果消消乐游戏")
