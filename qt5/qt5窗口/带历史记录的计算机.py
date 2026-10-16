import sys
from PyQt5.QtWidgets import *

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.intUI()

    def intUI(self):
        self.setWindowTitle("计算器")
        self.setMinimumSize(700,500)

        # 水平布局
        input_layout = QHBoxLayout() 
        main_layout = QVBoxLayout()

        #================第一部分计算区域=================
        # 输入框1
        self.num1 = QLineEdit(self)
        self.num1.setPlaceholderText("请输入数字1")
        self.num1.setMinimumWidth(50)
        input_layout.addWidget(self.num1)

        # “+”标签
        self.label2 = QLabel("+", self)
        self.label2.setMinimumWidth(20)
        input_layout.addWidget(self.label2)

        # 输入框2
        self.num2 = QLineEdit(self)
        self.num2.setPlaceholderText("请输入数字1")
        self.num2.setMinimumWidth(50)
        input_layout.addWidget(self.num2)

        # “=”标签
        self.label4 = QLabel("=", self)
        self.label4.setMinimumWidth(20)
        input_layout.addWidget(self.label4)

        # 计算结果框
        self.ruselt_label = QLineEdit(self)
        self.ruselt_label.setPlaceholderText("计算结果")
        self.ruselt_label.setReadOnly(True)
        input_layout.addWidget(self.ruselt_label)
        
        # 设置垂直为主布局 
        main_layout.addLayout(input_layout)

        # 计算按钮
        self.button = QPushButton("计算", self)
        self.button.clicked.connect(self.calculate)  # 信号和槽机制，得到什么-connect-执行什么
        main_layout.addWidget(self.button)

        #===========第二部分，历史记录==============
        # 历史记录标签
        self.label5 = QLabel("历史记录", self)
        self.label5.setMinimumWidth(50)
        main_layout.addWidget(self.label5)

        # 多行文本框
        self.history = QTextEdit()
        self.history.setReadOnly(True)
        self.history_text = ""
        self.history.setMinimumHeight(200)
        main_layout.addWidget(self.history)

        #===========第三部分，规定布局==============
        self.setLayout(main_layout)

        self.show()
    
    # 点击事件
    def calculate(self):
        num1 = float(self.num1.text())
        num2 = float(self.num2.text())
        ruselt = num1 + num2
        self.ruselt_label.setText(f"{ruselt}")
        old = f"{num1} + {num2} = {ruselt}"
        self.history_text += old + "\n"  # 旧的计算表达式加上新的计算表达式成为最后的历史记录，但因为要单行显示，加上换行符
        self.history.setPlainText(self.history_text)

        # 清空数字框
        self.num1.clear()
        self.num2.clear()



if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    sys.exit(app.exec_())