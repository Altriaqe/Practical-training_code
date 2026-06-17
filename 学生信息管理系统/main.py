from module.menu import menu
from module.component import Component
from module.component import pause
import time

def main():
    while True:
        menu()
        opt = input("请输入选项：").strip()
        if opt == '0':
            print("退出系统")
            break
        elif opt == '1': # 输入
            Component.instert_student()
        elif opt == '2': # 查询
            Component.search_student()
        elif opt == '3': # 删除
            Component.delete_student()
        elif opt == '4': # 修改
            Component.modify_student()
        elif opt == '5': # 排序
            Component.sort_student()
        elif opt == '6': # 统计
            Component.total_student()
        elif opt == '7': # 显示
            Component.show_student()
        else:
            print("输入错误，请重新输入！")
            pause()
            
if __name__ == '__main__':
    main()