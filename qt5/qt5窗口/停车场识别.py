import sys
from datetime import datetime

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
            self.close()  # 关闭登录窗口
            window = ParkingApp()  # 创建停车管理系统窗口
            window.show()  # 显示停车管理系统窗口

class ParkingSystem:
    """系统逻辑"""
    def __init__(self, capacity=50):
        self.capacity = capacity
        self.parked_cars = {} # 车牌，进入时间
        self.rate = 5.0
        self.history = []

    def get_availabe_spots(self):
        return self.capacity - len(self.parked_cars)

    def set_rate(self, rate):
        if rate > 0:
            self.rate = rate
            return True
        return False

    def set_capacity(self, capacity):
        if capacity >= len(self.parked_cars) and capacity > 0:
            self.capacity = capacity
            return True
        return False

    def car_enter(self, license_plate):
        if len(self.parked_cars) >= self.capacity:
            return False
        if license_plate in self.parked_cars:
            return False
        enter_time = datetime.now()
        self.parked_cars[license_plate] = enter_time
        return True, f"车辆{license_plate}已进入，时间{enter_time.strftime('%Y-%m-%d, %H:%M:%S')}"

    def car_exit(self, lincese_plate):
        if  lincese_plate not in self.parked_cars:
            return False, "车辆未在停车场内", 0.0
        enter_time = self.parked_cars.pop(lincese_plate)
        exit_time = datetime.now()
        duration = (exit_time - enter_time).total_seconds() / 3600.0
        duration = max(1.0, round(duration, 1))  # 最少按1小时计费
        fee = duration * self.rate
        self.history.append((
            lincese_plate,
            enter_time.strftime('%Y-%m-%d, %H:%M:%S'),
            exit_time.strftime('%Y-%m-%d, %H:%M:%S'),
            round(fee, 2),
        ))
        return True, f"车辆{lincese_plate}已离开，时间{exit_time.strftime('%Y-%m-%d, %H:%M:%S')}", fee
        
class ParkingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_plate = ""
        self.parking_system = ParkingSystem()
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle("停车管理系统")
        self.setGeometry(100,100,900,600)  # 设置窗口位置和大小

        # 主布局
        main_layout = QHBoxLayout()

        # 左侧面板
        left_panel = QVBoxLayout()

        # 车辆输入区域
        input_Group = QGroupBox("车辆输入区域")
        input_layout = QVBoxLayout()

        #==========1、省份选择==============
        province_layout = QHBoxLayout()
        province_label = QLabel("省份:")
        self.province_combo = QComboBox()
        # 省份合集
        provinces = ['京', '沪', '粤', '苏', '浙', '鲁', '晋', '冀', '豫', '云', 
                    '辽', '黑', '湘', '皖', '闽', '赣', '贵', '琼', '川', '甘', 
                    '陕', '吉', '蒙', '津', '渝', '澳', '台']
        self.province_combo.addItems(provinces)
        province_layout.addWidget(province_label)
        province_layout.addWidget(self.province_combo)
        input_layout.addLayout(province_layout)

        #===========2、字母选择==============
        letter_layout = QHBoxLayout()
        letter_label = QLabel("字母:")
        self.letter_combo = QComboBox()
        self.letter_combo.addItems([chr(ord('A') + i) for i in range(26)])
        letter_layout.addWidget(letter_label)
        letter_layout.addWidget(self.letter_combo)
        input_layout.addLayout(letter_layout)

        #===========3、后五位================
        number_layout = QVBoxLayout()
        number_label = QLabel()
        self.number_edit = QLineEdit()
        self.number_edit.setPlaceholderText("字母+数字，共五位")
        self.number_edit.setMaxLength(5)
        number_layout.addWidget(self.number_edit)
        number_layout.addWidget(number_label)
        input_layout.addLayout(number_layout)

        #============4、键盘输入区域===========
        keyboard_layout = QGridLayout()
        keyboard_layout.setSpacing(5)
        keys = [
            ['1', '2', 'A', 'B', 'C','D'],
            ['3', '4', 'E', 'F', 'G', 'H'],
            ['5', '6', 'I', 'J', 'K', 'L'],  
            ['7', '8', 'M', 'N', 'O', 'P'],
            ['9', '0', 'Q', 'R', 'S', 'T'],
            ['清除', '←', 'U', 'V', 'W', 'X'],
            ['', '', '', 'Y', 'Z', 'V']
        ]
        for row, key_row in enumerate(keys):
            for col, key in enumerate(key_row):
                print(row, col, key)
                if key:
                    btn = QPushButton(key)
                    btn.setMinimumHeight(30)
                    btn.setMaximumWidth(50)
                    btn.clicked.connect(lambda clicked, k=key: self.key_press(k))
                    keyboard_layout.addWidget(btn, row, col)
        input_layout.addLayout(keyboard_layout)
        
        #=============4、确认按钮===============
        self.verify_btn = QPushButton("确认车牌")
        self.verify_btn.clicked.connect(self.verify_plate)
        input_layout.addWidget(self.verify_btn)

        #=============5、当前车牌===============
        self.result_label = QLabel("当前车牌: 未输入")
        self.result_label.setFont(QFont('simhei', 12))
        self.result_label.setAlignment(Qt.AlignCenter)

        #=============6、车辆进出按钮============
        action_layout = QHBoxLayout()
        self.enter_btn = QPushButton("车辆进入")
        self.enter_btn.clicked.connect(self.car_enter)
        self.enter_btn.setEnabled(False)

        self.exit_btn = QPushButton("车辆离开")
        self.exit_btn.clicked.connect(self.car_exit)
        self.exit_btn.setEnabled(False)

        action_layout.addWidget(self.enter_btn)
        action_layout.addWidget(self.exit_btn)
        input_Group.setLayout(input_layout)
        input_Group.setMinimumHeight(500)

        # 先放入车牌输入区域，再放当前车牌和车辆进出按钮，
        # 否则它们会出现在输入区域的上方。
        left_panel.addWidget(input_Group)
        left_panel.addWidget(self.result_label)
        left_panel.addLayout(action_layout)

        # 右侧面板
        right_panel = QVBoxLayout()

        # 停车场状态区
        status_group = QGroupBox("停车场状态")
        status_layout = QFormLayout()

        # 状态标签先使用默认值，设置控件在下面的系统设置区域中创建。
        self.capacity_label = QLabel(str(self.parking_system.capacity))
        self.available_label = QLabel(str(self.parking_system.get_availabe_spots()))
        self.parked_label = QLabel(str(len(self.parking_system.parked_cars)))
        self.rate_label = QLabel(f"{self.parking_system.rate}元/小时")

        status_layout.addRow('总容量:', self.capacity_label) 
        status_layout.addRow('可用车位:', self.available_label) 
        status_layout.addRow('已停车数量:', self.parked_label) 
        status_layout.addRow('费率:', self.rate_label) 

        status_group.setLayout(status_layout)
        right_panel.addWidget(status_group)

        # 设置区域
        settings_group = QGroupBox("系统设置")
        settings_layout = QFormLayout()

        self.capacity_input = QSpinBox()
        self.capacity_input.setMinimum(1)
        self.capacity_input.setValue(50)
        self.capacity_input.setMaximumWidth(60)

        self.rate_input = QDoubleSpinBox()
        self.rate_input.setMinimum(0.1)
        self.rate_input.setValue(5.0)
        self.rate_input.setMaximumWidth(60)

        self.save_settings_btn = QPushButton("保存设置")
        self.save_settings_btn.setMaximumWidth(120)
        self.save_settings_btn.clicked.connect(self.save_settings)

        settings_layout.addRow('设置总容量', self.capacity_input)
        settings_layout.addRow('设置费率(元/小时)', self.rate_input)
        settings_layout.addRow(self.save_settings_btn)

        settings_group.setLayout(settings_layout)
        right_panel.addWidget(settings_group)\

        # 当前停放车辆
        parked_group = QGroupBox("当前停放车辆")
        parked_layout = QVBoxLayout()
        self.parked_list = QListWidget()
        self.parked_list.setMinimumWidth(700)
        parked_layout.addWidget(self.parked_list)
        parked_group.setLayout(parked_layout)
        right_panel.addWidget(parked_group)    

        #历史记录
        history_group = QGroupBox("历史记录")
        history_layout = QVBoxLayout()
        self.history_list = QListWidget()
        self.history_list.setMaximumWidth(700)
        history_layout.addWidget(self.history_list)
        history_group.setLayout(history_layout)
        right_panel.addWidget(history_group)  

        # 两侧使用相同的伸缩比例，避免布局根据控件内容把左侧撑得更宽。
        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)

        # 主要窗口部件
        central_wident = QWidget()
        central_wident.setLayout(main_layout)
        self.setCentralWidget(central_wident) # 设置主窗口的中央部件

    # 车牌输入事件
    def key_press(self, key):
        current_text = self.number_edit.text()
        if key == '清除':
            self.number_edit.clear()
        elif key == '←':
            self.number_edit.setText(current_text[:-1])
        else:
            # 如果当前输入长度小于5，则允许添加新字符
            if len(current_text) < 5:
                self.number_edit.setText(current_text + key)

    # 车牌确认事件
    def verify_plate(self):
        province = self.province_combo.currentText()
        letter = self.letter_combo.currentText()
        number_part = self.number_edit.text()

        if len(number_part) != 5:
            QMessageBox.warning(self, "输入错误", "后五位必须为5个字符")
            return
        
        for c in number_part:
            if not (c.isupper or c.islower):
                QMessageBox.warning(self, "输入错误", "输入必须为(A-Z)(0-9)")
                return

        self.current_plate = f"{province}{letter}{number_part}"
        self.result_label.setText(f'当前车牌：{self.current_plate}')    
        self.enter_btn.setEnabled(True)
        self.exit_btn.setEnabled(True)
        QMessageBox.information(self, "验证成功", f"车牌{self.current_plate}格式有效")

    def save_settings(self):
        new_capacity = self.capacity_input.value()
        new_rate = self.rate_input.value()

        if not self.parking_system.set_capacity(new_capacity):
            QMessageBox.warning(self, '警告', '容量设置无效')
            return
        if not self.parking_system.set_rate(new_rate):
            QMessageBox.warning(self, '警告', '容量设置无效')
            return
        
        QMessageBox.information(self, "提示", "已保存")
        self.update_display()

    def car_enter(self):
        if not self.current_plate:
            QMessageBox.warning(self, "警告", "请先确认车牌")
            return  
        success, message = self.parking_system.car_enter(self.current_plate)
        if success:
            QMessageBox.information(self, "提示", message)
        else:
            QMessageBox.warning(self, "警告", message)
        self.update_display()

    def car_exit(self):
        if not self.current_plate:
            QMessageBox.warning(self, "警告", "请先确认车牌")
            return
        success, message, fee = self.parking_system.car_exit(self.current_plate)
        if success:
            QMessageBox.information(self, "提示", f"{message}\n停车费用:{fee}元")
        else:
            QMessageBox.warning(self, "警告", message)
        self.update_display()

    def update_display(self):
        self.capacity_label.setText(str(self.parking_system.capacity))
        self.available_label.setText(str(self.parking_system.get_availabe_spots()))
        self.parked_label.setText(str(len(self.parking_system.parked_cars)))
        self.rate_label.setText(f"{self.parking_system.rate}元/小时")

        self.parked_list.clear()
        for plate, enter_time in self.parking_system.parked_cars.items():
            self.parked_list.addItem(f"{plate} - 进入 {enter_time.strftime('%Y-%m-%d, %H:%M:%S')}")

        self.history_list.clear()
        for record in reversed(self.parking_system.history[-10:]):
            plate, enter_time, exit_time, fee = record
            self.history_list.addItem(f"{plate} - 进入 {enter_time} - 离开 {exit_time} - 收费 {fee}元")
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())