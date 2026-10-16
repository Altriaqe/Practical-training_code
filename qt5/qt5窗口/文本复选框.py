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
        layout = QVBoxLayout()

        # 复选框
        title = QLabel("请选择你喜欢的课程：")
        layout.addWidget(title)

        self.python = QCheckBox("Python")
        self.java = QCheckBox("Java")
        self.cpp = QCheckBox("C++")

        layout.addWidget(self.python)
        layout.addWidget(self.java)
        layout.addWidget(self.cpp)

        self.python.stateChanged.connect(self.updata_selection)
        self.java.stateChanged.connect(self.updata_selection)
        self.cpp.stateChanged.connect(self.updata_selection)

        self.label1 = QLabel("选择了：",self)
        layout.addWidget(self.label1)

        self.setLayout(layout)

        self.show()

    def updata_selection(self):
        selected = []
        if self.python.isChecked():
            selected.append(self.python.text())
        if self.java.isChecked():
            selected.append(self.java.text())   
        if self.cpp.isChecked():
            selected.append(self.cpp.text())          
        self.label1.setText(f"已选择:{','.join(selected)}")             

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())