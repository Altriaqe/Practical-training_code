# 确认棋盘大小
size = 10 # 软编程

# 用列表来表示棋盘
board = [['-' for i in range(size)]for i in range(size)]  # 绘制一个二维列表，方便标识位置

"""
下棋的流程：
打印棋盘：‘o’,‘*’
输入坐标(进行一步检测)
检测是否决出胜负
"""

# 函数print_board()打印绘制棋盘
def print_board():
    print('   1   2   3   4   5   6   7   8   9   10')  # 表头
    for i in range(size):   # 根据尺寸遍历存储好数据的二维列表
        # 用字母做第一列的开头，因为要保证每行都是ABCD的顺序，所以对A的ASIC码加每一次的次数，后面加空格，保证不会默认换行
        print(chr(ord('A')+i), end=' ')
        for j in range(size):
            # 和对第一列一样的方法，但对存储好的数据遍历，打印出来
            print(f" {board[i][j]} ", end=' ')
        print()    # 换行


# 落子函数，如果无效则返回0
def put_chess(chess):
    pos = input().strip().upper()
    if len(pos) < 2 or len(pos) > 3:  # 判断输入是否有效
        return 0
    # 对输入的位置进行提取，转为可以识别的有效参数
    row = ord(pos[0])-ord('A')  # 行索引
    column = int(pos[1:]) - 1   # 列索引
    # 判断索引的有效性  
    if row < 0 or row >= size:
        return 0
    if column < 0 or column >= size:
        return 0
    # 判断所要进行的落子是否为空，如果是就落子，不是返回0
    if board[row][column] == '-':
        board[row][column] = chess
    else:
        return 0
    return row, column  # 同时返回两个值会被整合为一个元祖、为返回坐标


"""
在判断胜负的时候要考虑四个方向的位置，
所以先定义一个方向坐标，
对落子的坐标，进行方向坐标的加减，作为判断
如若判断成功为同类型落子，则对这个对象+1，统计为5个则结束判断，获胜
"""


# 判断胜负
directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # 四个方向的列表


def judge_winner(pos, chess):
    x, y = pos  # 对落子坐标进行解包
    for dx, dy in directions:   # 对方向列表进行解包
        counter = 1  # 因为已经进行落子，所以从1开始计数
        nx, ny = x + dx, y + dy  # 落子坐标的下一个判断坐标，作为起始点
        # 无限循环满足条件的坐标，统计计数
        while 0 <= nx < size and 0 <= ny < size and board[nx][ny] == chess:  # 正向判断
            counter += 1
            nx += dx
            ny += dy
        nx, ny = x - dx, y - dy
        while 0 <= nx < size and 0 <= ny < size and board[nx][ny] == chess:  # 反向判断
            counter += 1
            nx -= dx
            ny -= dy
        # 出现计数为5的则胜利，将布尔值判断为True
        if counter >= 5:
            return True
    return False


"""
主函数设计：
先定义一个游戏结束的变量，默认为False
对玩家进行标记
然后开始循环，直到is_game_over变量为真，则游戏结束
主要流程：
绘制棋盘
下棋（检测）
检测有效，则判断是否获胜，未获胜则换手，让player不等于1即可
"""
# 主函数
is_game_over = False
player = 1
while not is_game_over:
    print_board()
    if player == 1:
        chess = "*"
        print('\033[1;32;47m请玩家*落子:\033[0m')
        # 表达式\033[1;...;...m起始头、\033[0m结束头、用于设置字符串在控制台中输出的颜色
    else:
        chess = 'o'
        print('\033[1;32;47m请玩家o落子:\033[0m')

    pos = put_chess(chess)
    # 因为这里的函数范围若无效则为0，所以只需要检测pos不存在即可
    if not pos:
        print('\033[1;32;47m坐标输入错误,请重新输入\033[0m')
    else:
        # 如果judge_winner函数为真
        if judge_winner(pos,chess):
            print('\033[1;35;40m', end=" ")
            print_board()
            print('\033[0m', end=" ")
            print(f'\033[1;32;47m{chess}获胜\033[0m')
            is_game_over = True
        # 为假
        else:
            player = -player
