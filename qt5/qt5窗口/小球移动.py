import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("方向键控制小球")
        self.setMinimumSize(400, 300)
        self.setFocusPolicy(Qt.StrongFocus)

        self.ball_radius = 20  # 小球半径
        self.ball_x = self.width() // 2  # 小球初始x坐
        self.ball_y = self.height() // 2  # 小球初始y坐标
        self.step = 10  # 小球移动步长

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.red)
        # 绘制小球，小球的中心坐标为 (self.ball_x, self.ball_y)
        # drawEllipse() 方法的参数为 (x, y, width, height)，其中 (x, y) 为矩形区域的左上角坐标，width 和 height 为矩形区域的宽度和高度，所以绘制小球的矩形区域为 (self.ball_x - self.ball_radius, self.ball_y - self.ball_radius, self.ball_radius * 2, self.ball_radius * 2)
        painter.drawEllipse(self.ball_x - self.ball_radius, self.ball_y - self.ball_radius, self.ball_radius * 2, self.ball_radius * 2)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left or event.key() == Qt.Key_A:
            self.ball_x = max(self.ball_radius, self.ball_x - self.step)  # 向左移动
        elif event.key() == Qt.Key_Right or event.key() == Qt.Key_D:
            self.ball_x = min(self.width() - self.ball_radius, self.ball_x + self.step)  # 向右移动
        elif event.key() == Qt.Key_Up or event.key() == Qt.Key_W:
            self.ball_y = max(self.ball_radius, self.ball_y - self.step)  # 向上移动
        elif event.key() == Qt.Key_Down or event.key() == Qt.Key_S:
            self.ball_y = min(self.height() - self.ball_radius, self.ball_y + self.step)  # 向下移动

        self.update()  # 更新窗口，触发 paintEvent() 方法重新绘制小球


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())