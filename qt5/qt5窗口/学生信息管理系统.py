import sys
import csv
from pathlib import Path

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib


BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "students-1.csv"
MODEL_FILE = BASE_DIR.parents[1] / "cgpa_rf_model.pkl"

class MlScorepredictor:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        try:
            self.model = joblib.load(MODEL_FILE)  # 加载随机森林模型
        except FileNotFoundError:
            QMessageBox.critical(None, "错误", "模型文件 cgpa_rf_model.pkl 未找到，请先训练模型。")
            sys.exit(1)

    def predict(self, gre, toefl, university_rating, sop, lor, research):
        """使用随机森林模型预测学生的录取分数"""
        if self.model is None:
            QMessageBox.critical(None, "错误", "模型未加载，请检查模型文件。")
            return 0.0

        # 将输入特征转换为二维数组，符合模型的输入要求
        features = [[gre, toefl, university_rating, sop, lor, research]]
        # predict 方法返回一个数组，取第一个元素作为预测结果,举例: 如果输入特征为 [330, 340, 4, 4.5, 4.5, 1]，则返回的预测结果可能为 [9.2]，取第一个元素 9.2 作为最终预测分数
        return round(self.model.predict(features)[0], 2)  # 返回预测结果，保留两位小数
    

class Student:
    """学生类，存储学生信息"""
    def __init__(self, id, name, gender, age, major, gre, toefl, university_rating, sop, lor, research, cgpa):
        self.id = id
        self.name = name
        self.gender = gender
        self.age = age
        self.major = major

        self.gre = gre
        self.toefl = toefl
        self.university_rating = university_rating
        self.sop = sop
        self.lor = lor
        self.research = research
        self.cgpa = cgpa

    def to_dict(self):
        """将学生信息转换为字典形式，便于存储和处理"""
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "major": self.major,
            "gre": self.gre,
            "toefl": self.toefl,
            "university_rating": self.university_rating,
            "sop": self.sop,
            "lor": self.lor,
            "research": self.research,
            "cgpa": self.cgpa
        }
    
    def __str__(self):
        """返回学生信息的字符串表示形式，便于显示"""
        return f"ID: {self.id}, Name: {self.name}, Gender: {self.gender}, Age: {self.age}, Major: {self.major}, GRE: {self.gre}, TOEFL: {self.toefl}, University Rating: {self.university_rating}, SOP: {self.sop}, LOR: {self.lor}, CGPA: {self.cgpa}"

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
                        row['major'],
                        row['gre'],
                        row['toefl'],
                        row['university_rating'],
                        row['sop'],
                        row['lor'],
                        row['research'],
                        row['cgpa']
                    )
                    students.append(student)
        except FileNotFoundError:
            QMessageBox.critical(None, "读取失败", f"找不到学生数据文件：\n{CSV_FILE}")
        except KeyError as error:
            QMessageBox.critical(None, "读取失败", f"CSV 文件缺少字段：{error}")
        return students

    @staticmethod
    def write_students(students):
        """写入所有学生信息"""
        try:
            with open(CSV_FILE, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        'id', 'name', 'gender', 'age', 'major', 'gre', 'toefl',
                        'university_rating', 'sop', 'lor', 'research', 'cgpa'
                    ]
                )
                writer.writeheader()
                for student in students:
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

        return DataManager.write_students(students)

    @staticmethod
    def delete_student(student_id):
        """删除学生信息"""
        students = DataManager.read_students()
        # 反向操作，使用列表推导式过滤掉要删除的学生，避免在遍历列表时修改列表
        new_students = [s for s in students if s.id != student_id]
        if len(new_students) == len(students):
            QMessageBox.warning(None, "警告", "未找到该学生!")
            return False

        return DataManager.write_students(new_students)

    @staticmethod
    def update_student(updated_student):
        """更新学生信息"""
        students = DataManager.read_students()
        for i, s in enumerate(students): #使用 enumerate 遍历学生列表，同时获取每个学生的索引（i，即列表中的位置）
            if s.id == updated_student.id:
                students[i] = updated_student
                print(f"Updated student: {updated_student}")  # 打印更新后的学生信息
                return DataManager.write_students(students)
        QMessageBox.warning(None, "警告", "未找到该学生!")
        return False

    @staticmethod
    def search_students(keyword):
        """搜索学生信息"""
        students = DataManager.read_students()
        if not keyword:
            return students
        
        results = []
        keyword_lower = keyword.lower()

        if keyword_lower.startswith("zy"):  # 关键字以 "zy" 开头时按专业搜索
            major_keyword = keyword_lower[2:].strip()
            if not major_keyword:
                return students
            for student in students:
                major = str(student.major).lower() 
                if major_keyword in major:
                    results.append(student)
        else:  # 否则按学生ID或姓名搜索
            for student in students:
                if (keyword_lower in student.id.lower()) or (keyword_lower in student.name.lower()):
                    results.append(student)

        return results

    @staticmethod
    def reset_search():
        """重置搜索，显示所有学生信息"""
        students = DataManager.read_students()
        return students
        
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
        if self.student:  # 如果是编辑操作，预填充学生ID
            self.id_input.setText(self.student.id)
            self.id_input.setReadOnly(True)  # 编辑时不允许修改学生ID
        layout.addRow("学生ID:", self.id_input)

        # 姓名输入框
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入学生姓名")
        if self.student:  # 如果是编辑操作，预填充姓名
            self.name_input.setText(self.student.name)
        layout.addRow("姓  名:", self.name_input)

        # 性别输入框
        self.gender_input = QComboBox()
        self.gender_input.addItems(["男", "女"])
        if self.student:  # 如果是编辑操作，预填充性别
            index = self.gender_input.findText(self.student.gender)
            if index != -1:
                self.gender_input.setCurrentIndex(index)
        layout.addRow("性  别:", self.gender_input)

        # 年龄输入框
        self.age_input = QSpinBox()
        self.age_input.setRange(1, 100)  # 设置年龄范围为1
        if self.student:  # 如果是编辑操作，预填充年龄
            self.age_input.setValue(int(self.student.age))
        layout.addRow("年  龄:", self.age_input)

        # 专业输入框
        self.major_input = QLineEdit()
        self.major_input.setPlaceholderText("请输入专业")
        if self.student:  # 如果是编辑操作，预填充专业
            self.major_input.setText(self.student.major)
        layout.addRow("专  业:", self.major_input)

        # gre输入框
        self.gre_input = QLineEdit()
        self.gre_input.setPlaceholderText("请输入GRE成绩")
        if self.student:  # 如果是编辑操作，预填充GRE成绩
            self.gre_input.setText(str(self.student.gre))
        layout.addRow("GRE:", self.gre_input)

        # toefl输入框
        self.toefl_input = QLineEdit()
        self.toefl_input.setPlaceholderText("请输入TOEFL成绩")
        if self.student:  # 如果是编辑操作，预填充TOEFL成绩
            self.toefl_input.setText(str(self.student.toefl))
        layout.addRow("TOEFL:", self.toefl_input)

        # 大学评级输入框
        self.university_rating_input = QLineEdit()
        self.university_rating_input.setPlaceholderText("请输入大学评级")
        if self.student:  # 如果是编辑操作，预填充大学评级
            self.university_rating_input.setText(str(self.student.university_rating))
        layout.addRow("大学评级:", self.university_rating_input)

        # sop输入框
        self.sop_input = QLineEdit()
        self.sop_input.setPlaceholderText("请输入SOP评分")
        if self.student:  # 如果是编辑操作，预填充SOP评分
            self.sop_input.setText(str(self.student.sop))
        layout.addRow("SOP:", self.sop_input)

        # lor输入框
        self.lor_input = QLineEdit()
        self.lor_input.setPlaceholderText("请输入LOR评分")
        if self.student:  # 如果是编辑操作，预填充LOR评分
            self.lor_input.setText(str(self.student.lor))
        layout.addRow("LOR:", self.lor_input)

        # research输入框
        self.research_input = QLineEdit()
        self.research_input.setPlaceholderText("请输入Research评分")
        if self.student:  # 如果是编辑操作，预填充Research评分
            self.research_input.setText(str(self.student.research))
        layout.addRow("Research:", self.research_input)

        # cgpa输入框
        self.cgpa_input = QLineEdit()
        self.cgpa_input.setPlaceholderText("请输入CGPA")
        if self.student:  # 如果是编辑操作，预填充CGPA
            self.cgpa_input.setText(str(self.student.cgpa))
        layout.addRow("CGPA:", self.cgpa_input)

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
        gre = self.gre_input.text().strip()
        toefl = self.toefl_input.text().strip()
        university_rating = self.university_rating_input.text().strip()
        sop = self.sop_input.text().strip()
        lor = self.lor_input.text().strip()
        research = self.research_input.text().strip()
        cgpa = self.cgpa_input.text().strip()

        if not id or not name or not major:
            QMessageBox.warning(self, "错误", "学生ID、姓名和专业不能为空")
            return None

        return Student(id, name, gender, age, major, gre, toefl, university_rating, sop, lor, research, cgpa)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("停车管理系统")
        self.setGeometry(200,200,1950,600)  # 设置窗口位置和大小

        self.init_UI()
        self.load_students()
        self.predictor = MlScorepredictor()  # 初始化模型预测器

    def init_UI(self):
        central_widget = QWidget()
        main_layput = QVBoxLayout(central_widget)

        # 底部按钮
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加")
        self.edit_btn = QPushButton("编辑")
        self.delete_btn = QPushButton("删除")
        self.predict_btn = QPushButton("预测")
        self.predict_all_btn = QPushButton("批量预测")

        # 底部按钮埋点
        self.add_btn.clicked.connect(self.add_student)
        self.edit_btn.clicked.connect(self.edit_student)
        self.delete_btn.clicked.connect(self.delete_student)
        self.predict_btn.clicked.connect(self.predict_student)
        self.predict_all_btn.clicked.connect(self.predict_all_students)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.predict_btn)
        button_layout.addWidget(self.predict_all_btn)
        main_layput.addLayout(button_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels(["学生ID", "姓名", "性别", "年龄", "专业", "GRE", "TOEFL", "大学评级", "SOP", "LOR", "Research", "CGPA"])
        # 表格自适应
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止编辑
        self.table.cellClicked.connect(self.on_clicked) # 单元格被点击的行为,row为行号

        main_layput.addWidget(self.table)




        self.setCentralWidget(central_widget)

    def on_clicked(self, row, column):
        """表格单元格点击事件"""
        self.seleted_row = row  # 记录选中的行号

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
            self.table.setItem(row, 5, QTableWidgetItem(str(student.gre)))
            self.table.setItem(row, 6, QTableWidgetItem(str(student.toefl)))
            self.table.setItem(row, 7, QTableWidgetItem(str(student.university_rating)))
            self.table.setItem(row, 8, QTableWidgetItem(str(student.sop)))
            self.table.setItem(row, 9, QTableWidgetItem(str(student.lor)))
            self.table.setItem(row, 10, QTableWidgetItem(str(student.research)))
            self.table.setItem(row, 11, QTableWidgetItem(str(student.cgpa)))

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

        student_id = self.table.item(self.seleted_row, 0).text()
        students = DataManager.read_students()
        student = next((s for s in students if s.id == student_id), None)

        if student:
            form = StudentForm(self, student)
            # 预填充表单数据
            if form.exec_():  # 以模态方式显示表单, 阻塞主窗口, 直到表单关闭
                updated_student = form.get_student_data()
                if updated_student and DataManager.update_student(updated_student):
                    QMessageBox.information(self, "成功", "学生信息更新成功")
                    self.load_students()  # 重新加载学生数据
                elif updated_student:
                    QMessageBox.warning(self, "错误", "学生信息更新失败")
                    
    def delete_student(self):
        """删除学生信息"""
        if self.seleted_row == -1:
            QMessageBox.warning(self, "错误", "请先选择要删除的学生信息")
            return

        student_id = self.table.item(self.seleted_row, 0).text()
        student_name = self.table.item(self.seleted_row, 1).text()

        # 弹出确认删除对话框, QMessageBox.question()方法用于创建一个带有问题的消息框, 返回用户点击的按钮
        reply = QMessageBox.question(self, "确认删除", f"确定要删除学生 {student_name} (ID: {student_id}) 吗?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if DataManager.delete_student(student_id):
                QMessageBox.information(self, "成功", "学生信息删除成功")
                self.load_students()  # 重新加载学生数据

    def search_student(self):
        """搜索学生信息"""
        keyword = self.search_input.text().strip()
        results = DataManager.search_students(keyword)
        self.load_students(results)  # 加载搜索结果到表格中

        if not results:
            QMessageBox.information(self, "提示", "未找到匹配的学生信息")
        
    def reset_search(self):
        """重置搜索，显示所有学生信息"""
        self.search_input.clear()
        self.load_students()  # 重新加载所有学生数据

    def predict_student(self):
        """预测学生CGPA"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "错误", "请先选择要预测的学生信息")
            return
        self.students = DataManager.read_students()
        s = self.students[row]
        try:
            gre = float(s.gre)
            toefl = float(s.toefl)
            university_rating = float(s.university_rating)
            sop = float(s.sop)
            lor = float(s.lor)
            research = float(s.research)
            cgpa = self.predictor.predict(gre, toefl, university_rating, sop, lor, research)
            s.cgpa = cgpa  # 更新学生的CGPA
            DataManager.write_students(self.students)  # 更新学生信息到CSV文件
            self.load_students()  # 重新加载学生数据
            QMessageBox.information(self, "预测结果", f"学生 {s.name} (ID: {s.id}) 的预测CGPA为: {cgpa}")
        except ValueError:
            QMessageBox.warning(self, "错误", "学生信息中存在非数字的GRE、TOEFL、大学评级、SOP、LOR或Research值，无法进行预测")

    def predict_all_students(self):
        """批量预测所有学生的CGPA"""
        self.students = DataManager.read_students()
        for s in self.students:
            try:
                gre = float(s.gre)
                toefl = float(s.toefl)
                university_rating = float(s.university_rating)
                sop = float(s.sop)
                lor = float(s.lor)
                research = float(s.research)
                cgpa = self.predictor.predict(gre, toefl, university_rating, sop, lor, research)
                s.cgpa = cgpa  # 更新学生的CGPA
            except:
                continue  # 如果某个学生信息有误，跳过该学生，继续预测其他学生
        DataManager.write_students(self.students)  # 更新学生信息到CSV文件
        self.load_students()  # 重新加载学生数据
        QMessageBox.information(self, "预测结果", "所有学生的CGPA预测已完成")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
