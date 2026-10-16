import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.init_UI()
        self.init_timer()

        self.is_running = False  # 标记定时器是否正在运行
        self.remaining_time = 0  # 剩余时间，单位为秒
        self.total_time = 0  # 总时间，单位为秒

    
    def init_UI(self):
        # 设置窗口标题和大小
        self.setWindowTitle("定时器示例")
        self.setGeometry(500, 500, 300, 200)
        self.setMinimumSize(500, 300)

        # 创建布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # 标题标签
        title_label = QLabel("倒计时工具")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('simhei', 18, QFont.Bold))
        main_layout.addWidget(title_label)

        # 剩余时间显示区域
        self.time_display = QLabel("00:00:00")
        self.time_display.setAlignment(Qt.AlignCenter)
        self.time_display.setFont(QFont('simhei', 36, QFont.Bold))
        main_layout.addWidget(self.time_display)

        # 秒数输入框
        input_layout = QHBoxLayout()

        input_label = QLabel("输入秒数:")
        input_label.setFont(QFont('simhei', 12))
        input_layout.addWidget(input_label)

        self.seconds_input = QSpinBox()
        self.seconds_input.setRange(1, 3600)  # 设置范围为1到3600秒
        self.seconds_input.setFont(QFont('simhei', 12))
        self.seconds_input.setValue(60)  # 默认值为60秒
        self.seconds_input.setMinimumWidth(100)
        input_layout.addWidget(self.seconds_input)

        
        # 添加输入框到布局
        main_layout.addLayout(input_layout)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20) # 设置按钮之间的间距

        # 开始按钮
        self.start_btn = QPushButton("开始")
        self.start_btn.setFont(QFont('simhei', 12))
        self.start_btn.clicked.connect(self.start_countdown)
        button_layout.addWidget(self.start_btn)

        # 停止按钮
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setFont(QFont('simhei', 12))
        self.stop_btn.clicked.connect(self.stop_countdown)
        button_layout.addWidget(self.stop_btn)

        # 重置按钮
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setFont(QFont('simhei', 12))
        self.reset_btn.clicked.connect(self.reset_countdown)
        button_layout.addWidget(self.reset_btn)

        # 添加按钮到布局
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.show()

    # 按键事件处理函数

    # 初始化定时器
    def init_timer(self):
        """初始化计时器"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.setInterval(1000) # 1000ms触发一次

    # 时间转换
    def format_time(self, seconds):
        """将秒数格式化为时分秒的字符串"""
        hours = seconds // 36000
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    # 开始倒计时
    def start_countdown(self):
        """启动或继续定时器"""
        if not self.is_running:
            if self.remaining_time == 0:
                self.total_time = self.seconds_input.value()
                self.remaining_time = self.total_time
                # 验证
                if self.remaining_time <= 0:
                    QMessageBox.warning(self, "输入错误", "请输入大于0的秒数！")
                    return
        # 启动定时器
        self.timer.start()
        self.is_running = True
        # 更新按钮状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.seconds_input.setEnabled(False)

    def update_countdown(self):
        """更新时间"""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.time_display.setText(self.format_time(self.remaining_time))
        else:
            self.timer.stop()
            self.is_running = False
            QMessageBox.information(self, "倒计时结束", "时间到")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.start_btn.setText("开始")
            self.seconds_input.setEnabled(True)

    def stop_countdown(self):
        """暂停时间"""
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.start_btn.setEnabled(True)

    def reset_countdown(self):
        """重置时间"""
        self.timer.stop()
        self.is_running = False
        self.remaining_time = 0
        self.time_display.setText("00:00:00")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.seconds_input.setEnabled(True)

if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec_())