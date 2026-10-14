import sys
from PyQt5.QtWidgets import *

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PyQt5 窗口示例")
        self.setMinimumSize(700,500)

        layout = QHBoxLayout() # 水平布局

        # 创建组件
        self.label = QLabel("这是一个标签", self)
        self.button = QPushButton("点击我", self)

        # 设置布局
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        self.button.clicked.connect(self.on_button_click)

        self.setLayout(layout)
        self.show()

    def on_button_click(self):
        self.label.setText("按钮被点击了！")
        self.button.setText("已点击")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())