import os
import sys
from datetime import datetime

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import cv2
from paddleocr import PaddleOCR
from ultralytics import YOLO


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
            self.window = ParkingApp()  # 创建停车管理系统窗口
            self.window.show()  # 显示停车管理系统窗口

class YOLOv8LicenseDetector:
    """YOLOv8车牌检测与识别类"""
    
    def __init__(self, model_name='best.pt'):
        print(f"正在加载YOLO模型: {model_name}")
        self.model = YOLO(model_name)
        print("YOLO模型加载成功！")
        
        # 初始化OCR模型
        print("正在加载OCR模型...")
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
        print("OCR模型加载成功！")
    
    def detect_and_recognize(self, image_path, conf_threshold=0.3):
        """
        检测图片中的车牌并识别车牌号码
        返回: [(车牌号码, 置信度, 剪切图片路径), ...]
        """
        # 读取图片
        image = cv2.imread(image_path)
        if image is None:
            print(f"无法读取图片: {image_path}")
            return []
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_height, image_width = image_rgb.shape[:2]
        
        # 进行推理
        results = self.model(image_rgb, conf=conf_threshold)[0]
        
        # 获取检测结果
        boxes = results.boxes
        if boxes is None or len(boxes) == 0:
            print("未检测到任何车牌")
            return []
        
        # 创建临时保存目录
        temp_dir = 'temp_cropped'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        recognized_plates = []
        
        for idx, box in enumerate(boxes):
            # 获取边界框坐标
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # 确保坐标在图像范围内
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(image_width, x2), min(image_height, y2)
            
            # 获取置信度
            confidence = float(box.conf[0])
            
            # 剪切车牌区域
            plate_crop = image_rgb[y1:y2, x1:x2]
            
            if plate_crop.size == 0:
                continue
            
            # 保存临时剪切图片
            crop_filename = f"temp_plate_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx}.jpg"
            crop_path = os.path.join(temp_dir, crop_filename)
            from PIL import Image
            Image.fromarray(plate_crop).save(crop_path)
            
            # OCR识别
            try:
                result = self.ocr.ocr(crop_path, cls=True)
                if result and result[0]:
                    for line in result[0]:
                        text = line[1][0]
                        ocr_confidence = line[1][1]
                        # 过滤车牌格式（通常以中文省份简称开头）
                        if len(text) >= 6:
                            recognized_plates.append({
                                'plate_number': text,
                                'ocr_confidence': ocr_confidence,
                                'detection_confidence': confidence,
                                'crop_path': crop_path
                            })
                            print(f"识别到车牌: {text} (置信度: {ocr_confidence:.3f})")
            except Exception as e:
                print(f"OCR识别错误: {e}")
                continue
        
        # 按置信度排序，返回最可能的车牌
        if recognized_plates:
            recognized_plates.sort(key=lambda x: x['ocr_confidence'], reverse=True)
        
        return recognized_plates
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        temp_dir = 'temp_cropped'
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
            print("已清理临时文件")

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
        self.detector = None  # YOLO车牌检测器实例
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle("停车管理系统")
        self.setGeometry(100,100,900,600)  # 设置窗口位置和大小

        # 主布局
        main_layout = QHBoxLayout()

        # 左侧面板
        left_panel = QVBoxLayout()

        # 车辆输入区域
        input_Group = QGroupBox("车牌识别")
        input_layout = QVBoxLayout()

        #=============图片选择按钮==========
        self.select_image_btn = QPushButton("选择车牌图片")
        self.select_image_btn.setMinimumWidth(40)
        self.select_image_btn.clicked.connect(self.select_image)
        input_layout.addWidget(self.select_image_btn)

        #============图片浏览============
        self.image_label = QLabel('未选择图片\n请点击\"选择车牌图片\"按钮')
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(200)
        self.image_label.setMinimumWidth(300)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setScaledContents(True)  # 设置图片自适应标签大小
        input_layout.addWidget(self.image_label)

        #=============识别按钮============
        self.recognize_btn = QPushButton("识别车牌")
        self.recognize_btn.setMinimumWidth(40)
        self.recognize_btn.setEnabled(False)  # 初始状态下禁用识别按钮
        self.recognize_btn.clicked.connect(self.recognize_plate)
        input_layout.addWidget(self.recognize_btn)

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

        self.update_display()  # 初始化显示停车场状态和历史记录

        self.init_detection()  # 初始化YOLO车牌检测器

    def init_detection(self):
        """初始化YOLO车牌检测器"""
        try:
            self.detector = YOLOv8LicenseDetector(model_name='best.pt')
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载YOLO模型失败: {e}")
            sys.exit(1)

    def select_image(self):
        """选择车牌图片"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择车牌图片", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.current_image_path = file_path
            pixmap = QPixmap(file_path)
            sealed_pixmap = pixmap.scaled(
                self.image_label.width(), self.image_label.height(), 
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(sealed_pixmap)
            self.recognize_btn.setEnabled(True)  # 启用识别按钮
            self.result_label.setText("当前车牌: 等待识别")
            self.current_plate = ""
            self.enter_btn.setEnabled(False)
            self.exit_btn.setEnabled(False)

    def recognize_plate(self):
        """识别车牌"""
        # hasattr是内置函数，用来检查对象是否携带某个属性，返回True或False
        if not hasattr(self, 'current_image_path') or not self.current_image_path:
            QMessageBox.warning(self, "警告", "请先选择车牌图片")
            return
        # 检测是否初始化了车牌检测器
        if self.detector is None:
            QMessageBox.warning(self, "警告", "车牌检测器未初始化")
            return
        # 使用YOLO检测车牌并识别
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)  # 设置等待光标
            self.result_label.setText("正在识别车牌，请稍候...")
            result = self.detector.detect_and_recognize(self.current_image_path)

            if result:
                best_plate = result[0]  # 取置信度最高的结果
                self.current_plate = best_plate['plate_number']
                confidence = best_plate['ocr_confidence']
                self.result_label.setText(f"当前车牌: {self.current_plate}, 置信度: {confidence:.2%}")
                self.enter_btn.setEnabled(True)
                self.exit_btn.setEnabled(True)
                QMessageBox.information(self, "识别成功", f"识别到车牌: {self.current_plate}\n置信度: {confidence:.2%}")
            else:
                self.current_plate = ""
                self.result_label.setText("当前车牌: 未识别到车牌")
                self.enter_btn.setEnabled(False)
                self.exit_btn.setEnabled(False)
                QMessageBox.warning(self, "识别失败", "未识别到车牌，请检查图片或尝试其他图片")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"识别过程中发生错误: {e}")
            self.result_label.setText("当前车牌: 识别失败")
        finally:
            QApplication.restoreOverrideCursor()  # 恢复默认光标

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