import sys
import csv

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont

CSV_FILE = r"qt5\qt5窗口\student.csv"  # 从项目根目录运行时的CSV文件路径

class Student:
    """学生类，存储学生信息"""
    def __init__(self, id, name, gender, age, major):
        self.id = id
        self.name = name
        self.gender = gender
        self.age = age
        self.major = major

    def to_dict(self):
        """将学生信息转换为字典形式，便于存储和处理"""
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "major": self.major
        }
    
    def __str__(self):
        """返回学生信息的字符串表示形式，便于显示"""
        return f"ID: {self.id}, Name: {self.name}, Gender: {self.gender}, Age: {self.age}, Major: {self.major}"

class DataManager:
    """数据管理类，负责学生信息的读取和写入"""
    @staticmethod # 静态方法，不需要实例化类即可调用 例如 DataManager.read_students()
    def read_students():
        """从CSV文件中读取学生信息"""
        students = []
        try:
            with open(CSV_FILE, mode='r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)  # DictReader 类, 将csv文件的每一行转换为字典形式，键为表头，值为对应的单元格内容
                print(reader)
                for row in reader:
                    print(row)  # 打印每一行的字典形式
                    student = Student(
                        row['id'],
                        row['name'],
                        row['gender'],
                        row['age'],
                        row['major']
                    )
                    students.append(student)
        except FileNotFoundError:
            # 如果文件不存在，返回空列表
            pass
        return students

    @staticmethod
    def write_student(student):
        """将新的学生信息添加到CSV文件中"""
        try:
            with open(CSV_FILE, mode='a', newline='', encoding='utf-8-sig') as file:
                # 使用DictWriter类将学生信息写入CSV文件, fieldnames参数指定表头的顺序
                writer = csv.DictWriter(file, fieldnames=['id', 'name', 'gender', 'age', 'major'])
                # 如果文件为空，写入表头
                if file.tell() == 0:
                    writer.writeheader() # witeheader()方法用于写入表头, 只有在文件为空时才写入表头, 否则会重复写入表头
                print(student.to_dict())  # 打印学生信息的字典形式
                writer.writerow(student.to_dict()) 
            return True
        except Exception as e:
            print(f"Error writing to CSV: {e}")
            return False
        
    @staticmethod
    def add_student(student):
        """添加学生信息"""
        students = DataManager.read_students()
        # 检查学生ID是否已存在
        for s in students:
            if s.id == student.id:
                QMessageBox.warning(None, "错误", f"学生ID {student.id} 已存在")
                return False
        # 将新的学生信息写入CSV文件
        students.append(student)

        print(students)  # 打印所有学生信息
        return DataManager.write_student(student)

class StudentForm(QDialog):  # QDialog类用于创建对话框窗口，模态是指在对话框打开时，阻止用户与其他窗口交互，直到对话框关闭，QDialog.exec_()方法用于以模态方式显示对话框，阻塞主窗口，直到对话框关闭
    """学生信息表单，用于添加和编辑学生信息"""
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.student = student  # 如果是编辑操作，传入的学生对象不为None
        self.setWindowTitle("添加学生信息" if student is None else "编辑学生信息")
        self.setGeometry(100, 100, 300, 200)
        self.init_UI()

    def init_UI(self):
        layout = QFormLayout()

        # 学生ID输入框
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("请输入学生ID")
        layout.addRow("学生ID:", self.id_input)

        # 姓名输入框
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入学生姓名")
        layout.addRow("姓  名:", self.name_input)

        # 性别输入框
        self.gender_input = QComboBox()
        self.gender_input.addItems(["男", "女"])
        layout.addRow("性  别:", self.gender_input)

        # 年龄输入框
        self.age_input = QSpinBox()
        self.age_input.setRange(1, 100)  # 设置年龄范围为1
        layout.addRow("年  龄:", self.age_input)

        # 专业输入框
        self.major_input = QLineEdit()
        self.major_input.setPlaceholderText("请输入专业")
        layout.addRow("专  业:", self.major_input)

        # 按钮
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")

        self.ok_btn.clicked.connect(self.accept)  # 点击确定按钮时，调用accept()方法关闭对话框并返回QDialog.Accepted, 取消模态状态，不会返回表单数据，返回值为1
        self.cancel_btn.clicked.connect(self.reject)  # 点击取消按钮时，调用reject(),关闭对话框并返回QDialog.Rejected, 取消模态状态，关闭窗口，返回值为0
        
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addRow(button_layout)


        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        self.setLayout(main_layout)

    def get_student_data(self):
        """获取表单中的学生信息"""
        id = self.id_input.text().strip()
        name = self.name_input.text().strip()
        gender = self.gender_input.currentText()
        age = self.age_input.value()
        major = self.major_input.text().strip()

        if not id or not name or not major:
            QMessageBox.warning(self, "错误", "学生ID、姓名和专业不能为空")
            return None

        return Student(id, name, gender, age, major)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("停车管理系统")
        self.setGeometry(100,100,900,600)  # 设置窗口位置和大小

        self.init_UI()
        self.load_students()

    def init_UI(self):
        central_widget = QWidget()
        main_layput = QVBoxLayout(central_widget)

        # 搜索栏
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("请输入学生id")
        self.search_btn = QPushButton("搜素")
        self.reset_btn = QPushButton("重置")

        # 搜索按钮埋点
        # self.search_btn.clicked.connect(self.search_student)
        # self.reset_btn.clicked.connect(self.reset_search)


        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.reset_btn)
        main_layput.addLayout(search_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["学生ID", "姓名", "性别", "年龄", "专业"])
        # 表格自适应
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止编辑
        # self.table.cellClicked.connect(self.on_clicked) # 单元格被点击的行为,row为行号

        main_layput.addWidget(self.table)

        # 底部按钮
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加")
        self.edit_btn = QPushButton("编辑")
        self.delete_btn = QPushButton("删除")

        # 底部按钮埋点
        self.add_btn.clicked.connect(self.add_student)
        self.edit_btn.clicked.connect(self.edit_student)
        # self.delete_btn.clicked.connect(self.delete_student)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        main_layput.addLayout(button_layout)

        self.setCentralWidget(central_widget)

    # 加载学生数据
    def load_students(self, student_list=None):
        """加载学生数据到表格中"""
        if student_list is None:
            student_list = DataManager.read_students()

        self.table.setRowCount(len(student_list)) # 根据学生数量设置表格行数
        # 用enumerate遍历学生列表, row为行号, student为学生对象
        for row, student in enumerate(student_list):
            # 设置表格每一行的单元格内容, QTableWidgetItem类用于创建表格单元格
            self.table.setItem(row, 0, QTableWidgetItem(str(student.id)))
            self.table.setItem(row, 1, QTableWidgetItem(str(student.name)))
            self.table.setItem(row, 2, QTableWidgetItem(str(student.gender)))
            self.table.setItem(row, 3, QTableWidgetItem(str(student.age)))
            self.table.setItem(row, 4, QTableWidgetItem(str(student.major)))

        # 清楚选中状态
        # 标记表格中的所有行未被选中
        self.seleted_row = -1

    def add_student(self):
        """添加学生信息"""
        form = StudentForm(self)
        if form.exec_():  # 以模态方式显示表单, 阻塞主窗口, 直到表单关闭
            student = form.get_student_data()
            if student and DataManager.add_student(student):
                self.load_students()  # 重新加载学生数据
                QMessageBox.information(self, "成功", "学生信息添加成功")

    def edit_student(self):
        """编辑学生信息"""
        if self.seleted_row == -1:
            QMessageBox.warning(self, "错误", "请先选择要编辑的学生信息")
            return

        
       



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
