import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.value = 0

        self.timer = QTimer(self)
        self.timer.start(100)  # 设置定时器间隔为100毫秒
        self.timer.timeout.connect(self.update_time)

        self.progress_barl = QProgressBar(self)  # 创建进度条
        self.progress_barl.setRange(0, 100)  # 设置进度条范围

        v_laypout = QVBoxLayout()
        v_laypout.addWidget(self.progress_barl)
        self.setLayout(v_laypout)

    def update_time(self):
        self.value += 1
        self.progress_barl.setValue(self.value)

        if self.value >= 100:
            self.timer.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.setWindowTitle("进度条")
    window.resize(400, 200)
    window.show()
    sys.exit(app.exec_())