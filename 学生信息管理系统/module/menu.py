import os
# 清屏
def clear_screen():
    # 清屏nt为win系统的‘cls’， 其他系统为‘clear’
    os.system("cls" if os.name == 'nt' else 'clear')

# 菜单界面
def menu():
    clear_screen()
    print("""
    ================学生信息管理系统================
          1. 输入学生信息
          2. 查询学生信息
          3. 删除学生信息
          4. 修改学生信息
          5. 排序学生信息
          6. 统计学生信息
          7. 显示学生信息
          0. 退出系统
    ==============================================
          """)