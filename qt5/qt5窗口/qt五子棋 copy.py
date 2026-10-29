import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Evaluator:
    """估值函数类 - 评估棋盘局面"""
    def __init__(self):
        # 棋型权重表
        self.patterns = {
            "FIVE": 1000000,       # 连五
            "FOUR": 100000,        # 活四
            "FOUR_SLEEP": 12000,   # 冲四/眠四
            "THREE": 8000,          # 活三
            "THREE_SLEEP": 1500,   # 眠三
            "TWO": 300,             # 活二
            "TWO_SLEEP": 50         # 眠二
        }
    
    def evaluate(self, board, player, last_i=-1, last_j=-1):
        """
        评估当前局面
        返回正分表示对player有利
        """
        opponent = 3 - player
        my_score = 0
        opp_score = 0
        
        # 如果指定了最后落子位置，只评估其周围区域（性能优化）
        if last_i >= 0 and last_j >= 0:
            cells_to_check = self.get_nearby_cells(board, last_i, last_j, 2)
        else:
            cells_to_check = [(i, j) for i in range(len(board)) 
                            for j in range(len(board[i])) if board[i][j] != 0]
        
        for i, j in cells_to_check:
            if board[i][j] == player:
                my_score += self.evaluate_position(board, i, j, player)
            elif board[i][j] == opponent:
                opp_score += self.evaluate_position(board, i, j, opponent)
        
        # 返回分数差，防守权重略高
        return my_score - opp_score * 1.25
    
    def evaluate_position(self, board, x, y, player):
        """评估单个位置产生的棋型价值"""
        total_score = 0
        # 四个方向：水平、垂直、主对角线、副对角线
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            pattern = self.get_pattern(board, x, y, dx, dy, player)
            total_score += self.pattern_to_score(pattern)
        
        return total_score
    
    def get_pattern(self, board, x, y, dx, dy, player):
        """
        提取一个方向上的棋型模式
        返回字符串，'1'表示己方棋子，'0'表示空位，'2'表示对方棋子，'#'表示边界
        """
        size = len(board)
        pattern = []
        
        # 向正方向取5格
        for step in range(-5, 6):
            nx = x + dx * step
            ny = y + dy * step
            if 0 <= nx < size and 0 <= ny < size:
                if board[nx][ny] == player:
                    pattern.append('1')
                elif board[nx][ny] == 0:
                    pattern.append('0')
                else:
                    pattern.append('2')
            else:
                pattern.append('#')
        
        return ''.join(pattern)
    
    def pattern_to_score(self, pattern):
        """根据棋型字符串返回分数"""
        # 连五检测
        if '11111' in pattern:
            return self.patterns["FIVE"]
        
        # 活四检测
        if '011110' in pattern:
            return self.patterns["FOUR"]
        
        # 冲四检测（多种形态）
        four_patterns = ['11110', '01111', '11101', '10111', '11011']
        for fp in four_patterns:
            if fp in pattern:
                return self.patterns["FOUR_SLEEP"]
        
        # 活三检测
        three_patterns = ['01110', '10110']
        for tp in three_patterns:
            if tp in pattern:
                return self.patterns["THREE"]
        
        # 简单的眠三检测
        if '1110' in pattern or '0111' in pattern:
            return self.patterns["THREE_SLEEP"]
        
        # 活二检测
        if '0110' in pattern:
            return self.patterns["TWO"]
        
        # 眠二检测
        if '110' in pattern or '011' in pattern:
            return self.patterns["TWO_SLEEP"]
        
        return 0
    
    def get_nearby_cells(self, board, x, y, radius):
        """获取棋子周围指定半径内的非空格子"""
        size = len(board)
        cells = []
        for i in range(max(0, x - radius), min(size, x + radius + 1)):
            for j in range(max(0, y - radius), min(size, y + radius + 1)):
                if board[i][j] != 0:
                    cells.append((i, j))
        return cells
    
    def evaluate_fast(self, board, x, y, player):
        """快速评估一个点落子后的分数（用于启发式排序）"""
        # 临时放子
        original = board[x][y]
        board[x][y] = player
        score = self.evaluate_position(board, x, y, player)
        board[x][y] = original
        return score


class GameTreeSearcher:
    """博弈树搜索类 - 使用Alpha-Beta剪枝"""
    def __init__(self, evaluator, max_depth=3):
        self.evaluator = evaluator
        self.max_depth = max_depth
        self.nodes_searched = 0
        self.best_move = None
        self.start_time = 0
        self.max_time = 3.0  # 最大搜索时间（秒）
    
    #search_best_move方法是类的入口方法
    #last_move对手的上一步落子点
    def search_best_move(self, board, current_player, last_move=None):
        """
        对外接口：搜索最佳走法
        返回 (x, y)
        """
        import time
        self.start_time = time.time()
        self.nodes_searched = 0  #统计搜索的节点
        self.best_move = None  #记录当前找到的最佳方法
        
        # 迭代加深搜索循环，这是核心重点方法
        best_move = None
        for depth in range(1, self.max_depth + 1):
            # 检查时间
            if time.time() - self.start_time > self.max_time:
                break
            
            # 调用Alpha-Beta搜索
            #-float('inf')，Max层的下界，始终为负无穷
            #float('inf'），Min层的上界，始终为正无穷
            #True，从Max层开始
            self.alpha_beta_search(board, depth, -float('inf'), float('inf'), 
                                   True, current_player, last_move)
            
            if self.best_move:
                best_move = self.best_move
        
        print(f"搜索了 {self.nodes_searched} 个节点, 深度: {self.max_depth}")
        return best_move if best_move else self.get_center_move(board)
    
    def alpha_beta_search(self, board, depth, alpha, beta, is_maximizing, player, last_move=None):
        """
        Alpha-Beta剪枝搜索
        """
        import time
        # 时间超时检查
        if time.time() - self.start_time > self.max_time:
            return 0
        
        self.nodes_searched += 1
        
        # 终止条件
        if depth == 0 or self.is_terminal(board, last_move):
            return self.evaluator.evaluate(board, player, last_move[0] if last_move else -1, last_move[1] if last_move else -1)
        
        opponent = 3 - player
        #opponent = player
        
        if is_maximizing:
            max_eval = -float('inf')
            moves = self.generate_moves(board, last_move)
            moves = self.order_moves(board, moves, player)
            
            for x, y in moves:
                # 落子
                original = board[x][y]
                board[x][y] = player
                
                # 递归搜索
                eval = self.alpha_beta_search(board, depth-1, alpha, beta, False, opponent, (x, y))
                
                # 悔棋
                board[x][y] = original
                
                # 更新最大值
                if eval > max_eval:
                    max_eval = eval
                    if depth == self.max_depth or (depth == 1 and self.best_move is None):
                        self.best_move = (x, y)
                
                # Alpha剪枝
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval if max_eval != -float('inf') else 0
        else:
            min_eval = float('inf')
            moves = self.generate_moves(board, last_move)
            moves = self.order_moves(board, moves, opponent)
            
            for x, y in moves:
                original = board[x][y]
                board[x][y] = opponent
                eval = self.alpha_beta_search(board, depth-1, alpha, beta, True, player, (x, y))
                board[x][y] = original
                
                if eval < min_eval:
                    min_eval = eval
                
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval if min_eval != float('inf') else 0
    
    def generate_moves(self, board, last_move=None):
        """
        生成所有合法走法
        优化：只生成现有棋子周围的空位
        """
        size = len(board)
        moves = []
        
        # 统计棋盘上的棋子数
        piece_count = sum(1 for i in range(size) for j in range(size) if board[i][j] != 0)
        
        # 开局特殊处理（第一步）
        if piece_count == 0:
            center = size // 2
            moves.append((center, center))
            return moves
        
        # 如果有最后落子，在其周围生成候选点
        if last_move:
            radius = 2
            x, y = last_move
            candidate_set = set()
            for dx in range(-radius, radius+1):
                for dy in range(-radius, radius+1):
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < size and 0 <= ny < size and board[nx][ny] == 0:
                        candidate_set.add((nx, ny))
            moves = list(candidate_set)
        else:
            # 收集所有有棋子的位置
            pieces = []
            for i in range(size):
                for j in range(size):
                    if board[i][j] != 0:
                        pieces.append((i, j))
            
            # 在每个棋子周围2格范围内生成候选点
            radius = 2
            candidate_set = set()
            for x, y in pieces:
                for dx in range(-radius, radius+1):
                    for dy in range(-radius, radius+1):
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < size and 0 <= ny < size and board[nx][ny] == 0:
                            candidate_set.add((nx, ny))
            moves = list(candidate_set)
        
        # 如果候选点太少，补全所有空位
        if len(moves) < 5:
            moves = [(i, j) for i in range(size) 
                    for j in range(size) if board[i][j] == 0]
        
        return moves
    
    def order_moves(self, board, moves, player):
        """
        走法排序：优先尝试好走法
        """
        if not moves:
            return moves
        
        move_scores = []
        size = len(board)
        center = size // 2
        
        for x, y in moves:
            score = 0
            # 中心偏好
            dist_to_center = abs(x - center) + abs(y - center)
            score += (size - dist_to_center)
            
            # 快速估值
            score += self.evaluator.evaluate_fast(board, x, y, player)
            
            move_scores.append((score, x, y))
        
        # 降序排序
        move_scores.sort(reverse=True, key=lambda t: t[0])
        return [(x, y) for _, x, y in move_scores[:24]]  # 只保留前24个
    
    def is_terminal(self, board, last_move):
        """判断是否终局"""
        if last_move is None:
            return False
        
        x, y = last_move
        player = board[x][y]
        if player != 0 and self.check_win(board, x, y, player):
            return True
        
        # 检查是否平局
        size = len(board)
        for i in range(size):
            for j in range(size):
                if board[i][j] == 0:
                    return False
        return True
    
    def check_win(self, board, row, col, player):
        """检查是否获胜"""
        directions = [
            [(0, 1), (0, -1)],   # 水平
            [(1, 0), (-1, 0)],   # 垂直
            [(1, 1), (-1, -1)],  # 主对角线
            [(1, -1), (-1, 1)]   # 副对角线
        ]
        
        for dir_pair in directions:
            count = 1
            for dx, dy in dir_pair:
                r, c = row + dx, col + dy
                while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == player:
                    count += 1
                    r += dx
                    c += dy
            if count >= 5:
                return True
        return False
    
    def get_center_move(self, board):
        """返回中心位置或随机空位"""
        size = len(board)
        center = size // 2
        if board[center][center] == 0:
            return (center, center)
        
        for i in range(size):
            for j in range(size):
                if board[i][j] == 0:
                    return (i, j)
        return None


class GoBangBoard(QWidget):
    def __init__(self, parent=None, ai_mode=False):
        super().__init__(parent)
        self.initUI()
        self.ai_player = 2  # 默认AI为白棋
        self.intAi()
        self.ai_mode = False  # AI模式开关

    def intAi(self):
        """初始化AI"""
        self.evaluator = Evaluator()
        self.ai_searcher = GameTreeSearcher(self.evaluator, max_depth=4)
        self.ai_timer = None
        self.ai_thinking = False

    def initUI(self):
        self.setMinimumSize(900, 900)
        self.board_size = 15  # 棋盘大小
        self.cell_size = 30   # 每个格子的像素大小
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]  # 棋盘状态，0表示空，1表示黑子，2表示白子
        self.current_player = 1  # 1表示黑棋，2表示白棋
        self.last_i = -1  # 上一次落子的行
        self.last_j = -1  # 上一次落子的列
        self.game_over = False  # 游戏是否结束

    def paintEvent(self, event):
        """绘制棋盘和棋子"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), QColor(240,190,100))  # 填充背景

        # 绘制棋盘网格
        cell_size = min(self.width() - 40, self.height() - 40) // (self.board_size - 1)
        start_x = (self.width() - (self.board_size - 1) * cell_size) // 2
        start_y = (self.height() - (self.board_size - 1) * cell_size) // 2
        
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)

        for i in range(self.board_size):
            painter.drawLine(
                start_x + i * cell_size,
                start_y,
                start_x + i * cell_size,
                start_y + (self.board_size - 1) * cell_size,
            )
            painter.drawLine(
                start_x,
                start_y + i * cell_size,
                start_x + (self.board_size - 1) * cell_size,
                start_y + i * cell_size,
            )

        # 绘制星位,存储星位的坐标
        star_positions = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        # 遍历星位坐标，绘制星位
        for pos in star_positions:
            x, y = pos
            painter.setBrush(Qt.black)
            # 绘制星位为小圆点
            painter.drawEllipse(start_x + x * cell_size - 5, start_y + y * cell_size - 5, 10, 10)

        
        # 绘制棋子
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == 0:
                    continue

                x = start_x + j * cell_size
                y = start_y + i * cell_size
                painter.setPen(QPen(Qt.black, 2))

                if self.board[i][j] == 1:
                    painter.setBrush(Qt.black)
                else:
                    painter.setBrush(Qt.white)

                painter.drawEllipse(
                    QPoint(x, y),
                    cell_size // 2 - 2,
                    cell_size // 2 - 2,
                )

                if i == self.last_i and j == self.last_j:
                    painter.setPen(QPen(Qt.red, 2))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawEllipse(QPoint(x, y), 5, 5)

        if self.game_over:
            painter.setPen(QPen(Qt.red, 4))
            painter.setFont(QFont('simhei', 24, QFont.Bold))
            painter.drawText(self.rect(), Qt.AlignCenter, self.win_info)
            self.parent().status_label.setText(self.win_info)
           

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if self.game_over:
            return

        if event.button() == Qt.LeftButton:
            cell_size = min(self.width() - 40, self.height() - 40) // (self.board_size - 1)
            start_x = (self.width() - (self.board_size - 1) * cell_size) // 2
            start_y = (self.height() - (self.board_size - 1) * cell_size) // 2

            x = event.x() - start_x
            y = event.y() - start_y

            col = round(x / cell_size)
            row = round(y / cell_size)

            if 0 <= col < self.board_size and 0 <= row < self.board_size and self.board[row][col] == 0:
                if self.make_move(row, col):
                    self.update()

                if self.ai_mode and not self.game_over and self.current_player == self.ai_player:
                    self.ai_move()
                
    def make_move(self, row, col):
        """执行落子操作"""            
        self.board[row][col] = self.current_player
        self.last_i, self.last_j = row, col

        if self.check_winner(row, col):
            self.game_over = True
            if self.current_player == 1:
                self.win_info = "黑棋获胜！"
            else:
                self.win_info = "白棋获胜！"
            self.parent().update_status(self.win_info)
        else:
            self.current_player = 2 if self.current_player == 1 else 1
            plar = "黑棋" if self.current_player == 1 else "白棋"
            self.parent().status_label.setText(f"游戏状态: {plar}落子")

        return True

    def ai_move(self):
        """AI落子"""
        if self.game_over or self.current_player != self.ai_player:
            return

        self.ai_thinking = True
        self.update()

        self.ai_timer = QTimer(self)
        self.ai_timer.setSingleShot(True)
        self.ai_timer.timeout.connect(self.do_ai_move)
        self.ai_timer.start(10)  # 延迟100毫秒执行AI落子

    def do_ai_move(self):
        """执行AI落子"""
        if self.game_over or self.current_player != self.ai_player:
            self.ai_thinking = False
            return 

        last_move = (self.last_i, self.last_j) if self.last_i >= 0 and self.last_j >= 0 else None
        move = self.ai_searcher.search_best_move(self.board, self.ai_player, last_move)

        if move:
            row, col = move
            self.make_move(row, col)
            self.update()

        self.ai_thinking = False

    def check_winner(self, row, col):
            """判断输赢"""
            directions = [
                [(0, 1), (0, -1)],  # 水平方向
                [(1, 0), (-1, 0)],  # 垂直方向
                [(1, 1), (-1, -1)],  # 主对角线方向
                [(1, -1), (-1, 1)]   # 副对角线方向
            ]

            current_color = self.board[row][col]

            for dir_pair in directions: # 取大方向
                count = 1  # 包括当前落子
                for dx, dy in dir_pair:  # 取小方向
                    r, c = row + dx, col + dy
                    while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == current_color:
                        count += 1
                        r += dx
                        c += dy

                if count >= 5:  # 最大为9
                    return True

            return False


    def reset_game(self):
        """重置游戏"""
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.last_i = -1
        self.last_j = -1
        self.game_over = False
        self.win_info = ""
        self.update()
        self.parent().status_label.setText("当前状态: 黑棋落子")

        
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.init_UI()

    def init_UI(self):
        """初始化界面"""
        self.setWindowTitle("五子棋")
        self.setMinimumSize(600, 400)

        # 主布局
        main_layout = QVBoxLayout()

        # 创建状态标签
        self.status_label = QLabel("游戏状态: 等待开始")
        self.status_label.setFont(QFont('simhei', 12))
        main_layout.addWidget(self.status_label)

        # 创建棋盘区域
        self.board_widget = GoBangBoard()
        self.board_widget.setMinimumSize(800, 800)
        main_layout.addWidget(self.board_widget)

        # 按钮布局
        btn_layout = QHBoxLayout()

        # 重新开始按钮
        self.restart_btn = QPushButton("重新开始")
        self.restart_btn.setFont(QFont('simhei', 12))
        self.restart_btn.clicked.connect(self.board_widget.reset_game)
        btn_layout.addWidget(self.restart_btn)

        # ai按钮
        self.ai_btn = QPushButton("AI模式:关闭")
        self.ai_btn.setFont(QFont('simhei', 12))
        self.ai_btn.clicked.connect(self.toggle_ai_mode)
        btn_layout.addWidget(self.ai_btn)

        # 难度选择
        self.difficulty_label = QLabel("AI难度:")
        btn_layout.addWidget(self.difficulty_label)
        self.difficulty_combo = QPushButton("中等")
        self.difficulty_combo.setFont(QFont('simhei', 12))
        self.difficulty_combo.clicked.connect(self.change_difficulty)
        btn_layout.addWidget(self.difficulty_combo)
        btn_layout.addStretch()  # 添加弹性空间，使按钮靠左对齐

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        self.update_status(1)


    def update_status(self, player):
        color = "黑棋" if player == 1 else "白棋"
        self.status_label.setText(f"游戏状态: {color}落子")

    def toggle_ai_mode(self):
        """切换AI模式"""
        self.board_widget.ai_mode = not self.board_widget.ai_mode
        self.ai_btn.setText("AI模式:开启" if self.board_widget.ai_mode else "AI模式:关闭")
        self.board_widget.reset_game()  # 切换模式时重置游戏

    def change_difficulty(self):
        """更改AI难度"""
        difficulty = ['简单', '中等', '困难']
        current = self.difficulty_combo.text()

        # 根据选择的难度设置AI的策略
        if current == "简单":
            new_difficulty = "中等"
            self.board_widget.ai_searcher.max_depth = 4
        elif current == "中等":
            new_difficulty = "困难"
            self.board_widget.ai_searcher.max_depth = 5
        else:
            new_difficulty = "简单"
            self.board_widget.ai_searcher.max_depth = 2

        self.difficulty_combo.setText(new_difficulty)
        self.status_label.setText(f"AI难度已更改为: {new_difficulty}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
