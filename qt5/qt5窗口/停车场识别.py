import sys
from datetime import datetime

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont

class ParkingApp(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.enter_btn.clicked.connect(self.car_exit)
        self.enter_btn.setEnabled(False)

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
        self.capacity_label = QLabel("50")
        self.available_label = QLabel("50")
        self.parked_label = QLabel("0")
        self.rate_label = QLabel("5.0 元/小时")

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
        # self.save_settings_btn.clicked.connect(self.save_settings)

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
            QMessageBox(self, "输入错误", "后五位必须为5个字符")
            return
        
        for c in number_part:
            if not (c.isupper() or c.islower()):
                QMessageBox(self, "输入错误", "输入必须为(A-Z)(0-9)")
                return

        self.current_late = f"{province}{letter}{number_part}"
        self.result_label.setText(f'当前车牌：{self.current_late}')    
        self.enter_btn.setEnabled(True)
        self.exit_btn.setEnabled(True)
        QMessageBox.information(self, "验证成功", f"车牌{self.current_late}格式有效")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParkingApp()
    window.show()
    sys.exit(app.exec_())