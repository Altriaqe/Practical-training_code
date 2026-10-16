import sys
from PyQt5.QtWidgets import *

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.intUI()

    def intUI(self):
        self.setWindowTitle("文本复选框")
        self.setMinimumSize(400, 250)

        # 布局
        btn_layout = QHBoxLayout()
        main_layout = QVBoxLayout()

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
        self.clear_btn.clicked.connect(self.text.clear)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.open_btn)
        btn_layout.addWidget(self.clear_btn)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
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