# 导入系统库
import sys  # 提供对Python解释器使用或维护的一些变量的访问
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QGridLayout, QLabel, QPushButton, QLineEdit, QComboBox,
                               QRadioButton, QGroupBox, QTableWidget, QTableWidgetItem,
                               QHeaderView, QMessageBox, QScrollArea, QAbstractItemView)  # 导入PySide6 GUI组件
from PySide6.QtCore import Qt  # 导入Qt核心功能
from PySide6.QtGui import QFont, QColor  # 导入字体和颜色类
import datetime  # 导入日期时间模块

# 全局变量存储数据
students = []  # 存储学生列表
daily_attendance = {}  # 存储每日考勤数据，格式为 {日期: {学生名: 状态}}
weekly_attendance = {}  # 存储每周考勤数据，格式为 {日期: {学生名: 状态}}


def cleanup_old_data():
    """清理旧数据"""
    global students, daily_attendance, weekly_attendance  # 声明使用全局变量
    students = []  # 清空学生列表
    daily_attendance = {}  # 清空每日考勤数据
    weekly_attendance = {}  # 清空每周考勤数据


def add_student(window):
    """添加学生"""
    global students  # 声明使用全局变量
    name = window.student_name_input.text().strip()  # 获取输入框中的学生姓名并去除首尾空格
    if not name:  # 如果姓名为空
        QMessageBox.warning(window, "警告", "请输入学生姓名")  # 显示警告消息
        return  # 返回，不执行后续操作

    if name in students:  # 如果学生已存在
        QMessageBox.warning(window, "警告", "该学生已存在")  # 显示警告消息
        return  # 返回，不执行后续操作

    students.append(name)  # 将学生添加到列表中
    update_student_combo(window)  # 更新下拉菜单
    window.student_name_input.clear()  # 清空输入框
    refresh_weekly_display(window)  # 刷新周考勤显示


def delete_student(window):
    """删除学生"""
    global students  # 声明使用全局变量
    selected = window.student_combo.currentText()  # 获取当前选中的学生
    if not selected:  # 如果没有选中学生
        QMessageBox.warning(window, "警告", "请选择要删除的学生")  # 显示警告消息
        return  # 返回，不执行后续操作

    reply = QMessageBox.question(window, "确认", f"确定要删除学生 {selected} 吗？",  # 弹出确认对话框
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)  # 提供是/否选项
    if reply == QMessageBox.StandardButton.Yes:  # 如果用户点击"是"
        students.remove(selected)  # 从学生列表中移除选中的学生
        update_student_combo(window)  # 更新下拉菜单
        refresh_weekly_display(window)  # 刷新周考勤显示


def update_student_combo(window):
    """更新学生选择下拉菜单"""
    window.student_combo.clear()  # 清空下拉菜单
    window.student_combo.addItems(students)  # 将学生列表添加到下拉菜单


def record_attendance(window):
    """记录考勤"""
    global daily_attendance, weekly_attendance  # 声明使用全局变量
    selected = window.student_combo.currentText()  # 获取当前选中的学生
    if not selected:  # 如果没有选中学生
        QMessageBox.warning(window, "警告", "请选择学生")  # 显示警告消息
        return  # 返回，不执行后续操作

    status = "出勤" if window.present_radio.isChecked() else "缺勤"  # 根据单选按钮状态确定考勤状态
    today = datetime.date.today().strftime("%Y-%m-%d")  # 获取今天的日期字符串

    # 记录今日考勤
    if today not in daily_attendance:  # 如果今天还没有考勤记录
        daily_attendance[today] = {}  # 创建今天的考勤字典
    daily_attendance[today][selected] = status  # 记录该学生的考勤状态

    # 记录周考勤
    for i in range(7):  # 循环7天
        date = (datetime.date.today() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")  # 计算第i天前的日期
        if date not in weekly_attendance:  # 如果该日期还没有考勤记录
            weekly_attendance[date] = {}  # 创建该日期的考勤字典
        if selected not in weekly_attendance[date]:  # 如果该学生在该日期还没有记录
            weekly_attendance[date][selected] = "未记录"  # 设置为未记录

    # 更新当天考勤状态
    weekly_attendance[today][selected] = status  # 更新该学生今天的考勤状态

    calculate_attendance_rate(window)  # 计算出勤率
    refresh_weekly_display(window)  # 刷新周考勤显示


def calculate_attendance_rate(window):
    """计算出勤率"""
    today = datetime.date.today().strftime("%Y-%m-%d")  # 获取今天的日期字符串
    if today not in daily_attendance:  # 如果今天没有考勤记录
        window.attendance_rate_label.setText("今日出勤率: --%")  # 显示默认出勤率
        return  # 返回，不执行后续操作

    total_students = len(students)  # 获取总学生数
    present_count = sum(1 for status in daily_attendance[today].values() if status == "出勤")  # 计算出勤人数

    if total_students > 0:  # 如果有学生
        rate = round((present_count / total_students) * 100, 2)  # 计算出勤率并保留两位小数
        window.attendance_rate_label.setText(f"今日出勤率: {rate}%")  # 更新出勤率标签
    else:  # 如果没有学生
        window.attendance_rate_label.setText("今日出勤率: --%")  # 显示默认出勤率


def refresh_weekly_display(window):
    """刷新周考勤显示"""
    table = window.table  # 获取表格对象
    table.setRowCount(len(students))  # 设置表格行数为学生数量

    for row, student in enumerate(students):  # 遍历学生列表
        # 设置学生姓名
        name_item = QTableWidgetItem(student)  # 创建姓名单元格
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置文字居中对齐
        table.setItem(row, 0, name_item)  # 将姓名单元格添加到表格

        # 设置考勤记录
        for col in range(1, 8):  # 遍历7天
            i = 6 - (col - 1)  # 计算天数差（从6天前到今天）
            date = (datetime.date.today() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")  # 计算具体日期

            status = "未记录"  # 默认状态为未记录
            if date in weekly_attendance and student in weekly_attendance[date]:  # 如果该学生在该日期有记录
                status = weekly_attendance[date][student]  # 获取实际状态

            item = QTableWidgetItem(status)  # 创建状态单元格
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置文字居中对齐

            # 根据状态设置颜色
            if status == "出勤":  # 如果是出勤状态
                item.setBackground(QColor("#d4edda"))  # 设置背景色为绿色
                item.setForeground(QColor("#155724"))  # 设置前景色（文字颜色）为深绿
            elif status == "缺勤":  # 如果是缺勤状态
                item.setBackground(QColor("#f8d7da"))  # 设置背景色为红色
                item.setForeground(QColor("#721c24"))  # 设置前景色（文字颜色）为深红
            elif status == "未记录":  # 如果是未记录状态
                item.setBackground(QColor("#fff3cd"))  # 设置背景色为黄色
                item.setForeground(QColor("#856404"))  # 设置前景色（文字颜色）为深黄

            table.setItem(row, col, item)  # 将状态单元格添加到表格


def export_today_data(window):
    """导出今日考勤数据"""
    global students, daily_attendance  # 声明使用全局变量
    today = datetime.date.today().strftime("%Y-%m-%d")  # 获取今天的日期字符串
    filename = f"考勤数据_{today}.txt"  # 生成文件名

    with open(filename, "w", encoding="utf-8") as file:  # 以写入模式打开文件
        file.write(f"日期: {today}\n")  # 写入日期信息
        file.write("学生考勤情况:\n")  # 写入标题
        file.write("-" * 30 + "\n")  # 写入分隔线

        if today in daily_attendance:  # 如果今天有考勤记录
            for student, status in daily_attendance[today].items():  # 遍历今天的考勤记录
                file.write(f"{student}: {status}\n")  # 写入学生考勤状态
        else:  # 如果今天没有考勤记录
            file.write("今日暂无考勤记录\n")  # 写入提示信息

        total = len(students)  # 获取总学生数
        present = sum(1 for s in daily_attendance.get(today, {}).values() if s == "出勤")  # 计算出勤人数
        if total > 0:  # 如果有学生
            rate = round((present / total) * 100, 2)  # 计算出勤率
            file.write(f"\n出勤率: {rate}% ({present}/{total})\n")  # 写入出勤率信息
        else:  # 如果没有学生
            file.write("\n出勤率: --%\n")  # 写入默认出勤率

    QMessageBox.information(window, "导出成功", f"今日考勤数据已导出至: {filename}")  # 显示导出成功的消息


def create_main_window():
    """创建主窗口"""
    window = QMainWindow()  # 创建主窗口对象
    window.setWindowTitle("学生出勤管理系统")  # 设置窗口标题
    window.setGeometry(100, 100, 1400, 900)  # 设置窗口位置和大小

    # 创建中央部件
    central_widget = QWidget()  # 创建中央部件
    window.setCentralWidget(central_widget)  # 将中央部件设置为主窗口的中央部件

    # 创建主布局
    main_layout = QVBoxLayout(central_widget)  # 创建垂直布局

    # 标题
    title_label = QLabel("🎓 学生出勤管理系统")  # 创建标题标签
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置标签文字居中对齐
    title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))  # 设置字体
    title_label.setStyleSheet("color: #2c3e50; padding: 20px;")  # 设置样式
    main_layout.addWidget(title_label)  # 将标题标签添加到主布局

    # 创建主要内容区域
    content_widget = QWidget()  # 创建内容部件
    content_layout = QVBoxLayout(content_widget)  # 创建内容垂直布局

    # 学生管理区域
    student_group = QGroupBox("👥 学生管理")  # 创建学生管理组
    student_layout = QGridLayout(student_group)  # 创建网格布局

    # 添加学生
    student_layout.addWidget(QLabel("学生姓名:"), 0, 0)  # 添加标签到第0行第0列
    window.student_name_input = QLineEdit()  # 创建输入框
    student_layout.addWidget(window.student_name_input, 0, 1)  # 添加输入框到第0行第1列

    add_button = QPushButton("➕ 添加学生")  # 创建添加按钮
    add_button.clicked.connect(lambda: add_student(window))  # 连接按钮点击事件到添加学生函数
    student_layout.addWidget(add_button, 0, 2)  # 添加按钮到第0行第2列

    # 删除学生
    student_layout.addWidget(QLabel("选择学生:"), 1, 0)  # 添加标签到第1行第0列
    window.student_combo = QComboBox()  # 创建下拉选择框
    student_layout.addWidget(window.student_combo, 1, 1)  # 添加下拉选择框到第1行第1列

    delete_button = QPushButton("🗑️ 删除学生")  # 创建删除按钮
    delete_button.clicked.connect(lambda: delete_student(window))  # 连接按钮点击事件到删除学生函数
    student_layout.addWidget(delete_button, 1, 2)  # 添加删除按钮到第1行第2列

    content_layout.addWidget(student_group)  # 将学生管理组添加到内容布局

    # 考勤操作区域
    attendance_group = QGroupBox("📋 考勤操作")  # 创建考勤操作组
    attendance_layout = QHBoxLayout(attendance_group)  # 创建水平布局

    # 考勤状态选择
    attendance_layout.addWidget(QLabel("考勤状态:"))  # 添加标签

    window.present_radio = QRadioButton("✅ 出勤")  # 创建出勤单选按钮
    window.present_radio.setChecked(True)  # 设置为默认选中
    attendance_layout.addWidget(window.present_radio)  # 添加出勤按钮到布局

    window.absent_radio = QRadioButton("❌ 缺勤")  # 创建缺勤单选按钮
    attendance_layout.addWidget(window.absent_radio)  # 添加缺勤按钮到布局

    # 记录考勤按钮
    record_button = QPushButton("📝 记录考勤")  # 创建记录考勤按钮
    record_button.clicked.connect(lambda: record_attendance(window))  # 连接按钮点击事件到记录考勤函数
    attendance_layout.addWidget(record_button)  # 添加按钮到布局
    attendance_layout.addStretch()  # 添加弹性空间

    content_layout.addWidget(attendance_group)  # 将考勤操作组添加到内容布局

    # 统计区域
    stats_group = QGroupBox("📊 出勤统计")  # 创建统计组
    stats_layout = QHBoxLayout(stats_group)  # 创建水平布局

    window.attendance_rate_label = QLabel("今日出勤率: --%")  # 创建出勤率标签
    window.attendance_rate_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))  # 设置字体
    window.attendance_rate_label.setStyleSheet("color: #27ae60;")  # 设置样式
    stats_layout.addWidget(window.attendance_rate_label)  # 添加标签到布局

    export_button = QPushButton("📤 导出今日数据")  # 创建导出按钮
    export_button.clicked.connect(lambda: export_today_data(window))  # 连接按钮点击事件到导出函数
    stats_layout.addWidget(export_button)  # 添加按钮到布局
    stats_layout.addStretch()  # 添加弹性空间

    content_layout.addWidget(stats_group)  # 将统计组添加到内容布局

    # 近一周考勤显示区域
    weekly_group = QGroupBox("📅 近一周考勤状况")  # 创建周考勤显示组
    weekly_layout = QVBoxLayout(weekly_group)  # 创建垂直布局

    # 创建表格
    window.table = QTableWidget()  # 创建表格控件
    window.table.setColumnCount(8)  # 设置表格列数（学生姓名+7天）
    headers = ["学生姓名"] + [f"{i}天前" for i in range(6, -1, -1)]  # 创建表头
    window.table.setHorizontalHeaderLabels(headers)  # 设置表头标签

    # 设置表格样式
    window.table.setAlternatingRowColors(True)  # 设置交替行颜色
    window.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
    header = window.table.horizontalHeader()  # 获取水平表头
    header.setSectionResizeMode(QHeaderView.Stretch)  # 设置表头自适应宽度

    weekly_layout.addWidget(window.table)  # 添加表格到周考勤布局
    content_layout.addWidget(weekly_group)  # 将周考勤组添加到内容布局

    # 添加内容到滚动区域
    scroll_area = QScrollArea()  # 创建滚动区域
    scroll_area.setWidget(content_widget)  # 设置滚动区域的内容
    scroll_area.setWidgetResizable(True)  # 设置内容可调整大小
    main_layout.addWidget(scroll_area)  # 将滚动区域添加到主布局

    # 应用样式
    window.setStyleSheet("""
        QMainWindow {
            background-color: #ecf0f1;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            margin-top: 1ex;
            padding-top: 10px;
            background-color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #2c3e50;
        }
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #21618c;
        }
        QLineEdit, QComboBox {
            padding: 8px;
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            font-size: 14px;
        }
        QLineEdit:focus, QComboBox:focus {
            border-color: #3498db;
        }
        QTableWidget {
            background-color: #ffffff;
            alternate-background-color: #f8f9fa;
            gridline-color: #ecf0f1;
            border: 1px solid #bdc3c7;
        }
        QTableWidget::item {
            padding: 8px;
            border-right: 1px solid #ecf0f1;
            border-bottom: 1px solid #ecf0f1;
        }
        QHeaderView::section {
            background-color: #3498db;
            color: white;
            padding: 8px;
            border: 1px solid #2980b9;
            font-weight: bold;
        }
        QRadioButton, QLabel {
            color: #2c3e50;
        }
    """)

    # 设置表格行高
    window.table.verticalHeader().setDefaultSectionSize(40)  # 设置表格行高

    # 初始化数据
    cleanup_old_data()  # 清理旧数据
    update_student_combo(window)  # 更新下拉菜单
    calculate_attendance_rate(window)  # 计算出勤率
    refresh_weekly_display(window)  # 刷新周考勤显示

    return window  # 返回主窗口对象


def main():
    """主函数"""
    app = QApplication(sys.argv)  # 创建应用程序对象
    window = create_main_window()  # 创建主窗口
    window.show()  # 显示窗口
    sys.exit(app.exec())  # 启动应用程序事件循环


if __name__ == "__main__":  # 如果直接运行此脚本
    main()  # 调用主函数