import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class GoBangBoard(QWidget):
    turn_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
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

                self.update()

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

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        self.update_status(1)

    def update_status(self, player):
        color = "黑棋" if player == 1 else "白棋"
        self.status_label.setText(f"游戏状态: {color}落子")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

        