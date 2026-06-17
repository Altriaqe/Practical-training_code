import json
import os
filename = '学生信息管理系统\module\students.txt'

def read_students():
    if not os.path.exists(filename):
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        # json.loads()将字符串转换为Python对象，json.dumps()将Python对象转换为字符串
        return [json.loads(line.strip()) for line in f if line.strip()]
        # 类型变化：字符串 -> Python对象（字典）

def save_students(students):
    with open(filename, 'w', encoding='utf-8') as f:
        for student in students:
            # ensure_ascii=False参数可以让json.dumps()输出中文字符而不是Unicode编码
            f.write(json.dumps(student, ensure_ascii=False) + '\n')

# 断点，让程序暂停，等待用户输入后继续执行
def pause():
    input("按任意键继续...")

# 显示学生信息的函数，接收一个学生列表作为参数，并以表格形式输出学生信息
def show_students(students):
    if not students:
        print("没有学生信息，请先添加学生！")
        pause()
        return
    print("-" * 80)
    print(f"{'学生ID':<10} {'姓名':<20} {'英语':<10} {'Python':<10} {'C语言':<10}")
    for student in students:
        print(f"{student['id']:<10} {student['name']:<20} {student['english']:<10} {student['python']:<10} {student['c']:<10}")
    print("-" * 80)

class Component:
    def __init__(self, id, name, english, python, c):
        self.id = id
        self.name = name
        self.english = english
        self.python = python
        self.c = c

    # 定义一个通用方法来输入成绩，并进行验证， prompt参数用于提示用户输入哪个科目的成绩
    def input_score(prompt):
        while True:
            try:
                score = int(input(prompt).strip())
                if 0 <= score <= 100:
                    return score
                print("成绩必须在0到100之间，请重新输入！")
            except ValueError:
                print("输入无效，请输入一个数字！")
                


    def instert_student():
        global input_score
        students = read_students() 
        while True:
            print("===============输入学生信息================")
            sid = input("请输入学生ID：").strip()
            if any(student['id'] == sid for student in students):
                print("学生ID已存在，请重新输入！")
                continue
            name = input("请输入学生姓名：").strip()
            if not name:
                print("学生姓名不能为空，请重新输入！")
                continue
            english = Component.input_score("请输入英语成绩：")
            python = Component.input_score("请输入Python成绩：")
            c = Component.input_score("请输入C语言成绩：")
            student = {
                'id': sid,
                'name': name,
                'english': english,
                'python': python,
                'c': c
            }
            students.append(student)
            save_students(students)
            print("学生信息添加成功！")
            print("当前学生信息列表：")
            show_students(students)
            if input("是否继续添加？(y/n)：").strip().lower() != 'y':
                break
            pause()


    def search_student():
        students = read_students()
        if not students:
            print("没有学生信息，请先添加学生！")
            pause()
            return
        while True:
            print("===============查询学生信息================")
            mode = input("按ID查询请输入1，按姓名查询请输入2：").strip()
            results = []
            if mode == '1':
                sid = input("请输入学生ID：").strip()
                results = [s for s in students if s['id'] == sid]
            elif mode == '2':
                name = input("请输入学生姓名：").strip()
                results = [s for s in students if s['name'] == name]
            else:
                print("无效的选择，请重新输入！")
                pause()
                continue
            if results:
                print("查询结果：")
                show_students(results)
            else:
                print("未找到学生信息！")
            if input("是否继续查询？(y/n)：").strip().lower() != 'y':
                break
            
        

    def delete_student():
        students = read_students()
        if not students:
            print("没有学生信息，请先添加学生！")
            pause()
            return
        while True:
            print("===============删除学生信息================")
            sid = input("请输入学生ID：").strip()
            student = next((s for s in students if s['id'] == sid), None)
            if student:
                students.remove(student)
                save_students(students)
                print("学生信息删除成功！")
                print("当前学生信息列表：")
                show_students(students)
            else:
                print("未找到该学生信息！")
            if input("是否继续删除？(y/n)：").strip().lower() != 'y':
                break
            pause()


    def modify_student():
        students = read_students()
        if not students:
            print("没有学生信息，请先添加学生！")
            pause()
            return
        while True:
            print("===============修改学生信息================")
            sid = input("请输入学生ID：").strip()
            # next()函数用于从可迭代对象中获取下一个元素，满足条件的学生信息将被返回，如果没有找到则返回None
            """
            比如：students = [{'id': '001', 'name': '张三'}, {'id': '002', 'name': '李四'}]
            sid = '001'
            student = next((s for s in students if s['id'] == sid), None)
            这段代码会遍历students列表，找到id为'001'的学生信息，并将其赋值给student变量。
            如果找到了，student将是{'id': '001', 'name': '张三'}；如果没有找到，student将是None。
            """
            student = next((s for s in students if s['id'] == sid), None)
            if student:
                name = input(f"请输入学生姓名（当前：{student['name']}）：").strip()
                english = Component.input_score(f"请输入英语成绩（当前：{student['english']}）：")
                python = Component.input_score(f"请输入Python成绩（当前：{student['python']}）：")
                c = Component.input_score(f"请输入C语言成绩（当前：{student['c']}）：")
                student['name'] = name or student['name']
                student['english'] = english
                student['python'] = python
                student['c'] = c
                save_students(students)
                print("学生信息修改成功！")
            else:
                print("未找到该学生信息！")
            if input("是否继续修改？(y/n)：").strip().lower() != 'y':
                break
            pause()

    def sort_student():
        students = read_students()
        if not students:
            print("没有学生信息，请先添加学生！")
            pause()
            return
        while True:
            print("===============排序学生信息================")
            print("1. 按英语成绩排序")
            print("2. 按Python成绩排序")
            print("3. 按C语言成绩排序")
            choice = input("请选择排序方式：").strip()
            if choice == '1':
                students.sort(key=lambda s: s['english'], reverse=True)
            elif choice == '2':
                students.sort(key=lambda s: s['python'], reverse=True)
            elif choice == '3':
                students.sort(key=lambda s: s['c'], reverse=True)
            else:
                print("无效的选择，请重新输入！")
                continue
            for student in students:
                print(f"学生ID：{student['id']}，姓名：{student['name']}，英语：{student['english']}，Python：{student['python']}，C语言：{student['c']}")
            if input("是否继续排序？(y/n)：").strip().lower() != 'y':
                break
            pause()
            
    def total_student():
        students = read_students()
        if not students:
            print("没有学生信息，请先添加学生！")
            pause()
            return
        print("===============统计学生信息================")
        print(f"总学生数：{len(students)}")
        avg_english = sum(s['english'] for s in students) / len(students)
        avg_python = sum(s['python'] for s in students) / len(students)
        avg_c = sum(s['c'] for s in students) / len(students)
        print(f"平均英语成绩：{avg_english:.2f}")
        print(f"平均Python成绩：{avg_python:.2f}")
        print(f"平均C语言成绩：{avg_c:.2f}")
        pause()

    def show_student():
        students = read_students()
        if not students:
            print("没有学生信息，请先添加学生！")
            pause()
            return
        print("===============显示学生信息================")
        for student in students:
            print(f"学生ID：{student['id']}，姓名：{student['name']}，英语：{student['english']}，Python：{student['python']}，C语言：{student['c']}")
        pause()
