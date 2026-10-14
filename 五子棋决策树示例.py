# 五子棋简单决策树示例
# 说明：这个例子用“if / elif / else”的方式模拟决策树，判断某一步落子后是否胜出。


def check_direction(board, row, col, dr, dc, player):
    """检查某个方向上是否形成五连"""
    count = 1

    # 正方向
    r, c = row + dr, col + dc
    while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == player:
        count += 1
        r += dr
        c += dc

    # 反方向
    r, c = row - dr, col - dc
    while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == player:
        count += 1
        r -= dr
        c -= dc

    return count >= 5


def has_five(board, row, col, player):
    """判断落子后是否形成五连"""
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dr, dc in directions:
        if check_direction(board, row, col, dr, dc, player):
            return True
    return False


def is_board_full(board):
    """判断棋盘是否已满"""
    for row in board:
        for cell in row:
            if cell == 0:
                return False
    return True


def judge_game(board, row, col, player):
    """用决策树的思路判断当前局面：胜、和、继续"""
    # 决策树：先判断是否落子合法，再判断是否五连，最后判断和棋
    if not (0 <= row < len(board) and 0 <= col < len(board[0])):
        return "非法落子"

    if board[row][col] != 0:
        return "该位置已有棋子"

    # 这里假设落子已经放到了 board[row][col]
    # 决策节点 1：是否横向连五
    if has_five(board, row, col, player):
        return "胜方：" + str(player)

    # 决策节点 2：是否棋盘已满
    if is_board_full(board):
        return "和棋"

    # 决策节点 3：继续下一轮
    return "继续游戏"


def play_example():
    """演示一个简单例子"""
    board = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    # 让黑棋在第 0 行连续落 5 子
    for col in range(5):
        board[0][col] = 1

    print("棋盘状态：")
    for row in board:
        print(row)

    print("结果：", judge_game(board, 0, 4, 1))


if __name__ == "__main__":
    play_example()
