import sys
import csv

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("登录")
        self.setGeometry(100,100,400,200)  # 设置窗口位置和大小
        self.correct_password = "123456"  # 正确的密码

        self.init_UI()

    def init_UI(self):
        main_layout = QVBoxLayout()

        # 文本框1
        text_layout1 = QHBoxLayout()
        label1 = QLabel("用户名:")
        self.username_input = QLineEdit()
        text_layout1.addWidget(label1)
        text_layout1.addWidget(self.username_input)

        # 文本框2
        text_layout2 = QHBoxLayout()
        label2 = QLabel("密  码:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)  # 设置为密码模式
        text_layout2.addWidget(label2)
        text_layout2.addWidget(self.password_input)

        # 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self.handle_login)

        main_layout.addLayout(text_layout1)
        main_layout.addLayout(text_layout2)
        main_layout.addWidget(self.login_btn)

        # 主布局    
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def handle_login(self):
        """验证用户名和密码"""
        name = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not name:
            QMessageBox.warning(self, "错误", "用户名和密码不能为空")
            self.username_input.setFocus()
            return
        elif not password:
            QMessageBox.warning(self, "错误", "用户名和密码不能为空")
            self.password_input.setFocus()
            return
        elif password != self.correct_password:
            QMessageBox.warning(self, "错误", "用户名或密码错误")
            self.password_input.clear()
            self.password_input.setFocus()
            return
        else:
            QMessageBox.information(self, "成功", "登录成功")
            self.open_parking_app()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())