import sys
from PyQt5.QtWidgets import *

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt5 窗口示例")
        self.setMinimumSize(700,500)

        # 组件
        self.num1 = QLineEdit(self)
        
        self.Label1 = QLabel("数字1:", self)
        self.label2 = QLabel("+", self)
        self.num2 = QLineEdit(self)
        self.Label3 = QLabel("数字2:", self)
        self.Label4 = QLabel("=", self)
        self.button = QPushButton("计算", self)
        self.history = QLabel("历史记录:", self)
        self.history_list = QListWidget(self)

        # 计算按钮点击事件
        self.button.clicked.connect(self.calculate)
        # 历史记录点击事件
        self.history_list.itemClicked.connect(self.show_history)

        # 设置布局
        Vlayout = QVBoxLayout() # 垂直布局
        Hlayout = QHBoxLayout() # 水平布局
        """
        布局函数
        QvBoxLayout: 垂直布局
        QHBoxLayout: 水平布局
        QGridLayout: 网格布局
        QFormLayout: 表单布局
        QStackedLayout: 堆叠布局
        QBoxLayout: 盒子布局
        """
        # 添加组件到布局
        Hlayout.addWidget(self.Label1)
        Hlayout.addWidget(self.num1)
        Hlayout.addWidget(self.label2)
        Hlayout.addWidget(self.Label3)
        Hlayout.addWidget(self.num2)
        Hlayout.addWidget(self.Label4)
        Vlayout.addLayout(Hlayout)
        Vlayout.addWidget(self.button)
        Vlayout.addWidget(self.history)
        Vlayout.addWidget(self.history_list)
        self.setLayout(Vlayout)


        # 计算函数
    def calculate(self):
        try:
            num1 = float(self.num1.text())
            num2 = float(self.num2.text())
            result = num1 + num2
            self.Label4.setText(f"= {result}")
            # 添加历史记录
            self.history_list.addItem(f"{num1} + {num2} = {result}")
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的数字！")
        # 显示历史记录函数
    def show_history(self, item):
        QMessageBox.information(self, "历史记录", item.text())




if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec_())