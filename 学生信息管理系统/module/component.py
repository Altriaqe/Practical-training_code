import json
import os
filename = '学生信息管理系统\module\students.txt'

def read_students():
    if not os.path.exists(filename):
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        # json.loads()将字符串转换为Python对象，json.dumps()将Python对象转换为字符串
        return [json.loads(line.strip()) for line in f if line.strip()] # if line.strip()用于过滤掉空行，避免json.loads()解析空字符串时报错
        # 类型变化：字符串 -> Python对象（字典）

def save_students(students):
    with open(filename, 'w', encoding='utf-8') as f:
        for student in students:
            # ensure_ascii=False参数可以让json.dumps()输出中文字符而不是Unicode编码
            f.write(json.dumps(student, ensure_ascii=False) + '\n')

# 断点，让程序暂停，等待用户输入后继续执行
def pause():
    input("按任意键继续...")

# 获取成绩总分
def get_total_score(student):
    return student['english'] + student['python'] + student['c']

# 显示学生信息的函数，接收一个学生列表作为参数，并以表格形式输出学生信息
def show_students(students):
    if not students:
        print("没有学生信息，请先添加学生！")
        pause()
        return
    print("-" * 80)
    print(f"{'学生ID':<10} {'姓名':<20} {'英语':<10} {'Python':<10} {'C语言':<10}{'共计':<10}")
    for student in students:
        print(f"{student['id']:<10} {student['name']:<20} {student['english']:<10} {student['python']:<10} {student['c']:<10}{get_total_score(student):<10}")
    print("-" * 80)

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

# 定义一个Component类，包含学生信息的属性和相关方法
class Component:
    def instert_student():
        students = read_students() 
        if not students:
            print("没有学生信息，请先添加学生！")
            pause()
            return
        while True:
            print("===============输入学生信息================")
            sid = input("请输入学生ID：").strip()
            # any函数用于判断给定的可迭代对象中是否有满足条件的元素，如果有则返回True，否则返回False
            if any(student['id'] == sid for student in students):
                print("学生ID已存在，请重新输入！")
                continue
            name = input("请输入学生姓名：").strip()
            if not name:
                print("学生姓名不能为空，请重新输入！")
                continue
            english = input_score("请输入英语成绩：")
            python = input_score("请输入Python成绩：")
            c = input_score("请输入C语言成绩：")
            # 将输入信息整合为一个学生字典，并添加到学生列表中，最后保存到文件
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
            # 建立一个列表，确保有重名的学生也可以被查询到，避免使用next()函数只返回第一个匹配的学生信息
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
                pause()
            else:
                print("未找到学生信息！")
            if input("是否继续查询？(y/n)：").strip().lower() != 'y':
                break
            pause()
            
        

    def delete_student():
        students = read_students()
        if not students:
            print("没有学生信息，请先添加学生！")
            pause()
            return
        while True:
            print("===============删除学生信息================")
            sid = input("请输入学生ID：").strip()
            # next()函数用于从可迭代对象中获取下一个元素，满足条件的学生信息将被返回，如果没有找到则返回None
            """
            比如：students = [{'id': '001', 'name': '张三'}, {'id': '002', 'name': '李四'}]
            sid = '001'
            student = next((s for s in students if s['id'] == sid), None)
            这段代码会遍历students列表，找到id为'001'的学生信息，并将其赋值给student变量。
            如果找到了，student将是{'id': '001', 'name': '张三'}；如果没有找到，student将是None。
            enumerate()函数用于将一个可迭代对象转换为一个索引序列，同时列出数据和数据下标，常用于在循环中获取元素的索引。
            比如：students = [{'id': '001', 'name': '张三'}, {'id': '002', 'name': '李四'}]
            sid = '001'
                for index, student in enumerate(students):
                    if student['id'] == sid:
                        print(f"学生信息索引：{index}, 学生信息：{student}")
                        break
            """
            # student = next((i for i,j in enumerate(student) if j['id'] == sid),none) 
            # 如果需要获取索引，可以使用enumerate()函数来实现,通过索引来删除学生信息
            student = next((s for s in students if s['id'] == sid), None)
            if student:
                # del students[student] # 通过索引删除学生信息
                students.remove(student) # remove()方法用于从列表中删除指定的元素，如果元素不存在则会引发ValueError异常
                # 若要用坐标students.remove(index(student))，则需要先获取索引位置，可以使用enumerate()函数来代替直接使用del
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
            student = next((s for s in students if s['id'] == sid), None)
            # or 的短路特性，如果用户输入了新的姓名，就使用新的姓名，否则保持原来的姓名不变
            """
            比如：原本名字为李华、输入李华保持不变，输入新的名字张华则修改为张华
            """
            if student:
                name = input(f"请输入学生姓名（当前：{student['name']}）：").strip() or student['name']
                english = input_score(f"请输入英语成绩（当前：{student['english']}）：") or student['english']
                python = input_score(f"请输入Python成绩（当前：{student['python']}）：") or student['python']
                c = input_score(f"请输入C语言成绩（当前：{student['c']}）：") or student['c']
                student['name'] = name 
                student['english'] = english
                student['python'] = python
                student['c'] = c
                save_students(students)
                print("学生信息修改成功！")
                print("当前学生信息列表：")
                show_students(students)
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
            print("4. 按总成绩排序")
            reverse = input("请选择排序方式（升序请输入0，降序请输入1）：").strip() == '1'
            mode = input("请选择排序科目：").strip()

            key_dict = {
                "1": lambda s: s['english'],
                "2": lambda s: s['python'],
                "3": lambda s: s['c'],
                "4": get_total_score
            }

            key_func = key_dict.get(mode, lambda s: s['id'])  # 默认按ID排序

            students.sort(key=key_func, reverse=reverse)
            print("排序完成！当前学生信息列表：")
            show_students(students)
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
        pause()

    def show_student():
        students = read_students()
        if not students:
            print("没有学生信息，请先添加学生！")
            pause()
            return
        print("===============显示学生信息================")
        show_students(students)
        pause()
