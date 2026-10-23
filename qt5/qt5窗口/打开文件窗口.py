import sys
from PyQt5.QtWidgets import *

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.intUI()
        self.create_action()
        self.create_menu()

    def clear_text(self):
        self.text.clear()

    def copy_text(self):
        self.text.copy()

    def paste_text(self):
        self.text.paste()

    def create_menu(self):
        file_menu = self.menuBar().addMenu("文件")
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.clear_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = self.menuBar().addMenu("编辑")
        edit_menu.addAction(self.clear_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.exit_action)

        show_menu = self.menuBar().addMenu("显示")
        show_menu.addAction(self.save_action)

    def create_action(self):
        self.save_action = QAction("保存文件", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save)

        self.open_action = QAction("打开文件", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open)

        self.clear_action = QAction("清理文件", self)
        self.clear_action.setShortcut("Ctrl+L")
        self.clear_action.triggered.connect(self.clear_text)

        self.exit_action = QAction("退出", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)

        self.edit_action = QAction("编辑", self)
        self.edit_action.setShortcut("Ctrl+E")

        self.copy_action = QAction("复制", self)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.triggered.connect(self.copy_text)

        self.paste_action = QAction("粘贴", self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.triggered.connect(self.paste_text)


    def intUI(self):
        self.setWindowTitle("文本复选框")
        self.setMinimumSize(400, 250)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 布局
        btn_layout = QHBoxLayout()
        main_layout = QVBoxLayout(central_widget)

        # 组件
        self.text = QTextEdit()
        self.text.setPlaceholderText("请输入文本...")
        main_layout.addWidget(self.text)

        # 按钮
        self.save_btn = QPushButton("保存文件")
        self.open_btn = QPushButton("打开文件")
        self.clear_btn = QPushButton("清理文件")

        # # 事件
        self.save_btn.clicked.connect(self.save)
        self.open_btn.clicked.connect(self.open)
        self.clear_btn.clicked.connect(self.clear_text)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.open_btn)
        btn_layout.addWidget(self.clear_btn)

        main_layout.addLayout(btn_layout)
        self.show()

        # 事件逻辑
    def save(self):
        """保存文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存文件",
            "",
            "文本文件(*.txt);;所有文件(*)"
        ) 
        if file_path:
            if not file_path.endswith(".txt"):
                file_path += ".txt"
            with open(file_path, "w", encoding="utf-8") as f:
                content = self.text.toPlainText()
                f.write(content)

    def open(self):
        """打开文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,       # 当前窗口对象
            "打开文件",     # 所打开的子窗口的标题
            "",     # 默认打开位置
            "文本文件(*.txt);;所有文件(*)"       # 文件过滤器
        ) 
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.text.setText(content)  

if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    sys.exit(app.exec_())