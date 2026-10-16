import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QGridLayout, QVBoxLayout, QLineEdit)
from PyQt5.QtCore import Qt

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        # 初始化计算器界面
        self.initUI()

    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('简易计算器')
        self.resize(300, 400)

        # 创建显示区域（输入和结果显示）
        self.display = QLineEdit()
        # 设置显示框只读（只能通过按钮输入）
        self.display.setReadOnly(True)
        # 设置文本右对齐（符合计算器习惯）
        self.display.setAlignment(Qt.AlignRight)
        # 设置字体大小
        self.display.setStyleSheet("font-size: 20px; padding: 10px;")

        # 创建按钮布局（网格布局，4行4列）
        grid = QGridLayout()

        # 按钮文本布局（按计算器常用布局排列）
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            'C', '0', '=', '+'
        ]

        # 生成按钮并添加到网格布局
        positions = [(i, j) for i in range(4) for j in range(4)]
        for position, text in zip(positions, buttons):
            # 创建按钮
            button = QPushButton(text)
            # 设置按钮样式
            button.setStyleSheet("font-size: 18px; padding: 15px;")
            # 添加到网格布局
            grid.addWidget(button, *position)
            # 绑定按钮点击事件
            button.clicked.connect(self.on_button_click)

        # 创建主布局（垂直布局：显示框在上，按钮在下）
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.display)
        main_layout.addLayout(grid)

        # 设置窗口主布局
        self.setLayout(main_layout)

        # 显示窗口
        self.show()

    def on_button_click(self):
        # 获取点击的按钮文本
        button_text = self.sender().text()  # 返回触发当前事件的对象（即用户点击的那个按钮实例）
        # .text()是按钮(QPushButton)的方法，用于获取按钮上显示的文本内容

        # 处理清除按钮 (C)
        if button_text == 'C':
            self.display.clear()

        # 处理等号 (=)：计算结果
        elif button_text == '=':
            try:
                # 获取显示框中的表达式
                expression = self.display.text()
                # 替换乘除符号（适配Python语法）
                expression = expression.replace('×', '*').replace('÷', '/')
                # 计算表达式结果
                result = eval(expression) # Python内置函数，作用是将传入的字符串当作 Python 代码执行，并返回执行结果。
                # 显示结果
                self.display.setText(str(result))
            except Exception as e:
                # 处理计算错误（如除以0、表达式错误）
                self.display.setText('错误')

        # 处理其他按钮（数字和运算符）
        else:
            # 运算符显示优化（×代替*，÷代替/）
            if button_text == '*':
                button_text = '×'
            elif button_text == '/':
                button_text = '÷'

            # 在当前文本后添加按钮内容
            current_text = self.display.text()
            self.display.setText(current_text + button_text)


if __name__ == '__main__':
    # 创建应用实例
    app = QApplication(sys.argv)
    win = Calculator()
    sys.exit(app.exec_())
