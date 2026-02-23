# -*- coding: utf-8 -*-
# ==============================================================================
# 学生出勤统计系统 - Flet 平板优化版
# ==============================================================================
# 适用分辨率：2700x1740 平板
# Python 版本：3.12+
# Flet 版本：0.23.0
# 功能：学生管理、出勤登记、统计报表、数据导出
# 特点：每次启动自动清除旧数据，大屏优化布局，变量名清晰易懂
# ==============================================================================

# 导入 Flet GUI 框架模块，用于构建用户界面
import flet as ft
# 导入日期时间模块，用于获取当前日期
from datetime import datetime
# 导入 JSON 模块，用于数据的序列化和反序列化
import json
# 导入操作系统模块，用于文件操作（检查、删除、创建文件）
import os

# ==============================================================================
# 全局配置常量
# ==============================================================================
# 定义数据文件存储路径，所有学生数据和出勤记录保存在此文件中
DATA_FILE_PATH = "attendance_data.json"
# 定义全局列表变量，用于存储所有学生姓名
student_name_list = []
# 定义全局字典变量，用于存储出勤记录（日期 -> 学生状态）
attendance_record_dict = {}

# ==============================================================================
# 状态码定义（内部使用英文，避免 emoji 匹配问题）
# ==============================================================================
# 定义出勤状态码，表示学生正常出勤
STATUS_CODE_PRESENT = "present"
# 定义缺勤状态码，表示学生未出勤
STATUS_CODE_ABSENT = "absent"
# 定义迟到状态码，表示学生迟到
STATUS_CODE_LATE = "late"
# 定义请假状态码，表示学生请假
STATUS_CODE_LEAVE = "leave"

# 定义状态码到显示文本的映射字典，用于界面显示时转换
status_code_to_display_text_dict = {
    STATUS_CODE_PRESENT: "✅ 出勤",  # 出勤状态显示文本
    STATUS_CODE_ABSENT: "❌ 缺勤",  # 缺勤状态显示文本
    STATUS_CODE_LATE: "⚠️ 迟到",  # 迟到状态显示文本
    STATUS_CODE_LEAVE: "📝 请假",  # 请假状态显示文本
}


# ==============================================================================
# 数据操作函数
# ==============================================================================
def clear_old_data_file():
    """
    清除旧数据文件
    功能：每次程序启动时删除旧的数据文件，确保从空白状态开始
    """
    # 检查数据文件是否存在于当前目录
    if os.path.exists(DATA_FILE_PATH):
        # 尝试执行删除操作
        try:
            # 删除旧数据文件
            os.remove(DATA_FILE_PATH)
            # 在控制台打印成功信息
            print("[INFO] 已清除旧数据")
        # 捕获可能发生的异常（如文件被占用、权限不足等）
        except Exception as error_exception:
            # 打印警告信息，包含具体错误内容
            print(f"[WARN] 清除失败：{error_exception}")


def reload_data_from_file():
    """
    从文件重新加载数据
    功能：将 JSON 文件中的数据读取到全局变量 student_name_list 和 attendance_record_dict 中
    """
    # 声明使用全局变量 student_name_list 和 attendance_record_dict
    global student_name_list, attendance_record_dict
    # 检查数据文件是否存在
    if os.path.exists(DATA_FILE_PATH):
        # 尝试执行文件读取操作
        try:
            # 以只读模式打开数据文件，指定 UTF-8 编码
            with open(DATA_FILE_PATH, 'r', encoding='utf-8') as file_object:
                # 使用 json.load 解析文件内容为 Python 字典
                data_dict = json.load(file_object)
                # 从字典中获取学生列表，如果不是列表则默认为空列表
                student_name_list = data_dict.get("students", [])
                # 从字典中获取出勤记录，如果不是字典则默认为空字典
                attendance_record_dict = data_dict.get("records", {})
        # 捕获可能发生的异常（如文件格式错误、编码问题等）
        except Exception as error_exception:
            # 打印警告信息
            print(f"[WARN] 加载失败：{error_exception}")
            # 将学生列表重置为空
            student_name_list = []
            # 将出勤记录重置为空
            attendance_record_dict = {}


def save_data_to_file():
    """
    保存数据到文件
    功能：将全局变量 student_name_list 和 attendance_record_dict 写入 JSON 文件
    """
    # 尝试执行文件写入操作
    try:
        # 以写入模式打开数据文件，指定 UTF-8 编码
        with open(DATA_FILE_PATH, 'w', encoding='utf-8') as file_object:
            # 将学生列表和出勤记录打包为字典
            # ensure_ascii=False 确保中文正常显示（不转义为 Unicode）
            # indent=2 使 JSON 格式美观，每层缩进 2 个空格
            json.dump({"students": student_name_list, "records": attendance_record_dict}, file_object,
                      ensure_ascii=False, indent=2)
    # 捕获可能发生的异常（如磁盘空间不足、权限问题等）
    except Exception as error_exception:
        # 打印错误信息
        print(f"[ERROR] 保存失败：{error_exception}")


def get_current_date_string():
    """
    获取当前日期字符串
    返回：格式为 YYYY-MM-DD 的日期字符串（如 2026-02-23）
    """
    # 获取当前日期时间对象，并格式化为 YYYY-MM-DD 格式字符串
    return datetime.now().strftime('%Y-%m-%d')


# ==============================================================================
# 主应用程序函数
# ==============================================================================
def main_function(page_object: ft.Page):
    """
    主应用程序入口函数
    参数 page_object: Flet 页面对象，用于构建和更新 UI 界面
    """
    # 设置应用程序窗口标题，显示在窗口标题栏
    page_object.title = "学生出勤统计"
    # 设置页面主题模式为浅色模式（LIGHT 或 DARK）
    page_object.theme_mode = ft.ThemeMode.LIGHT
    # 设置页面内边距为 30 像素，控件与窗口边缘的距离
    page_object.padding = 30
    # 设置窗口宽度为 2400 像素，适配 2700x1740 平板分辨率
    page_object.window.width = 2400
    # 设置窗口高度为 1500 像素，充分利用平板屏幕空间
    page_object.window.height = 1500

    # 程序启动时清除旧数据文件，确保每次都是干净的状态
    clear_old_data_file()

    # ==========================================================================
    # 辅助函数定义
    # ==========================================================================
    def show_snackbar_message(message_text):
        """
        显示提示消息（Snackbar）
        参数 message_text: 要显示的消息文本字符串
        """
        # 尝试执行消息显示操作
        try:
            # 创建 SnackBar 组件，包含要显示的文本消息
            snackbar_control = ft.SnackBar(ft.Text(message_text))
            # 将 SnackBar 添加到页面覆盖层（overlay）中
            page_object.overlay.append(snackbar_control)
            # 设置 SnackBar 为打开状态，使其显示出来
            snackbar_control.open = True
            # 更新页面显示，使更改生效
            page_object.update()
        # 捕获可能发生的异常
        except Exception as error_exception:
            # 在控制台打印错误信息
            print(f"[ERROR] 消息显示失败：{error_exception}")

    def close_dialog_function(event=None):
        """
        关闭当前弹窗
        参数 event: 事件对象（可选，通常为按钮点击事件）
        """
        # 尝试执行关闭弹窗操作
        try:
            # 检查页面是否有活动的弹窗
            if page_object.dialog:
                # 设置弹窗为关闭状态
                page_object.dialog.open = False
                # 更新页面显示，使更改生效
                page_object.update()
        # 捕获可能发生的异常
        except Exception as error_exception:
            # 在控制台打印错误信息
            print(f"[ERROR] 关闭弹窗失败：{error_exception}")

    def open_dialog_function(dialog_control):
        """
        打开指定弹窗
        参数 dialog_control: AlertDialog 弹窗对象
        """
        # 尝试执行打开弹窗操作
        try:
            # 将弹窗对象设置到页面的 dialog 属性
            page_object.dialog = dialog_control
            # 设置弹窗为打开状态
            dialog_control.open = True
            # 更新页面显示，使更改生效
            page_object.update()
        # 捕获可能发生的异常
        except Exception as error_exception:
            # 在控制台打印错误信息
            print(f"[ERROR] 打开弹窗失败：{error_exception}")

    # ==========================================================================
    # 学生管理功能
    # ==========================================================================
    def open_student_manage_dialog(event):
        """
        打开学生管理弹窗
        功能：添加新学生、删除已有学生
        参数 event: 按钮点击事件对象
        """
        # 重新加载最新数据，确保显示的是最新学生列表
        reload_data_from_file()

        # 创建文本输入框控件，用于输入学生姓名
        student_name_input_field = ft.TextField(
            hint_text="输入学生姓名",  # 设置占位提示文本
            text_size=35,  # 设置字体大小为 35 像素（适配大屏）
            expand=True  # 设置横向占满可用空间
        )

        # 创建列容器控件，用于显示学生列表（支持滚动）
        student_list_column_control = ft.Column(
            spacing=15,  # 设置子控件间距为 15 像素
            scroll=ft.ScrollMode.AUTO,  # 设置自动显示滚动条
            height=600  # 设置固定高度为 600 像素
        )

        def refresh_student_list_display():
            """刷新学生列表显示"""
            # 清空列表现有所有控件
            student_list_column_control.controls.clear()
            # 遍历学生名单列表
            for index_number, current_student_name in enumerate(student_name_list):
                # 捕获当前学生姓名到局部变量（避免闭包问题）
                student_name_for_delete = current_student_name

                def delete_student_function(delete_event):
                    """删除学生处理函数"""
                    # 声明使用全局变量 student_name_list
                    global student_name_list
                    # 检查学生是否存在于列表中
                    if student_name_for_delete in student_name_list:
                        # 从列表中移除该学生
                        student_name_list.remove(student_name_for_delete)
                        # 保存更新后的数据到文件
                        save_data_to_file()
                        # 显示删除成功提示消息
                        show_snackbar_message("删除成功！")
                        # 关闭当前弹窗
                        close_dialog_function()
                        # 重新打开学生管理弹窗（刷新显示）
                        open_student_manage_dialog(None)

                # 创建学生列表项行控件（包含姓名和删除按钮）
                student_list_column_control.controls.append(
                    ft.Row([
                        # 显示学生序号和姓名的文本控件
                        ft.Text(f"{index_number + 1}. {student_name_for_delete}", size=35, expand=True),
                        # 删除按钮控件（红色背景，白色文字）
                        ft.ElevatedButton("🗑️ 删除", color=ft.colors.WHITE, bgcolor=ft.colors.RED_700,
                                          on_click=delete_student_function),
                    ])
                )
            # 更新页面显示，使列表更改生效
            page_object.update()

        def add_student_function(add_event):
            """添加学生处理函数"""
            # 声明使用全局变量 student_name_list
            global student_name_list
            # 获取输入框内容并去除首尾空格
            new_student_name = student_name_input_field.value.strip()
            # 检查姓名是否非空
            if new_student_name:
                # 检查学生是否已存在于列表中
                if new_student_name in student_name_list:
                    # 显示已存在提示消息
                    show_snackbar_message("该学生已存在！")
                else:
                    # 将新学生添加到列表末尾
                    student_name_list.append(new_student_name)
                    # 保存更新后的数据到文件
                    save_data_to_file()
                    # 清空输入框内容
                    student_name_input_field.value = ""
                    # 显示添加成功提示消息
                    show_snackbar_message("添加成功！")
                    # 刷新列表显示
                    refresh_student_list_display()
            else:
                # 显示输入提示消息
                show_snackbar_message("请输入学生姓名！")

        # 初始刷新列表，显示当前所有学生
        refresh_student_list_display()

        # 创建弹窗对话框对象
        student_manage_dialog = ft.AlertDialog(
            title=ft.Text("👥 学生名单管理", size=45),  # 设置弹窗标题，字体 45 像素
            content=ft.Column([
                # 输入框和添加按钮行控件
                ft.Row([student_name_input_field,
                        ft.ElevatedButton("➕ 添加", on_click=add_student_function, expand=True)]),
                # 分隔线控件
                ft.Divider(),
                # 学生列表控件
                student_list_column_control,
            ], spacing=20),  # 设置子控件间距为 20 像素
            actions=[ft.TextButton("❌ 关闭", on_click=close_dialog_function)],  # 关闭按钮
        )
        # 打开弹窗
        open_dialog_function(student_manage_dialog)

    # ==========================================================================
    # 出勤登记功能
    # ==========================================================================
    def open_attendance_register_dialog(event):
        """
        打开出勤登记弹窗
        功能：为每个学生设置当日出勤状态
        参数 event: 按钮点击事件对象
        """
        # 重新加载最新数据
        reload_data_from_file()

        # 获取今日日期字符串
        today_date_string = get_current_date_string()

        # 检查今日记录是否存在，不存在则创建空字典
        if today_date_string not in attendance_record_dict:
            attendance_record_dict[today_date_string] = {}

        # 创建状态列表容器（支持滚动）
        attendance_status_list_column = ft.Column(
            spacing=20,  # 设置子控件间距为 20 像素
            scroll=ft.ScrollMode.AUTO,  # 设置自动显示滚动条
            height=550  # 设置固定高度为 550 像素
        )

        # 创建统计文本显示控件
        attendance_stats_text_control = ft.Text("", size=35)

        def update_attendance_stats_display():
            """更新出勤统计显示"""
            # 获取今日记录字典
            today_record_dict = attendance_record_dict.get(today_date_string, {})

            # 初始化出勤人数计数器
            present_student_count = 0
            # 初始化缺勤人数计数器
            absent_student_count = 0
            # 初始化迟到人数计数器
            late_student_count = 0
            # 初始化请假人数计数器
            leave_student_count = 0

            # 遍历今日所有学生记录
            for each_student_status_value in today_record_dict.values():
                # 如果状态为出勤，出勤计数加 1
                if each_student_status_value == STATUS_CODE_PRESENT:
                    present_student_count += 1
                # 如果状态为缺勤，缺勤计数加 1
                elif each_student_status_value == STATUS_CODE_ABSENT:
                    absent_student_count += 1
                # 如果状态为迟到，迟到计数加 1
                elif each_student_status_value == STATUS_CODE_LATE:
                    late_student_count += 1
                # 如果状态为请假，请假计数加 1
                elif each_student_status_value == STATUS_CODE_LEAVE:
                    leave_student_count += 1

            # 更新统计文本显示（包含所有四种状态）
            attendance_stats_text_control.value = f"📊 出勤:{present_student_count} | 迟到:{late_student_count} | 缺勤:{absent_student_count} | 请假:{leave_student_count} | 总计:{len(student_name_list)}"
            # 更新页面显示
            page_object.update()

        def create_student_status_button_row(target_student_name):
            """
            为单个学生创建状态按钮组
            参数 target_student_name: 学生姓名
            返回：包含学生姓名和 4 个状态按钮的行控件
            """
            # 获取该学生当前状态（默认为出勤）
            current_student_status = attendance_record_dict.get(today_date_string, {}).get(target_student_name,
                                                                                           STATUS_CODE_PRESENT)

            def on_status_button_click(selected_status_code):
                """状态按钮点击处理函数"""
                # 声明使用全局变量 attendance_record_dict
                global attendance_record_dict
                # 设置该学生今日状态
                attendance_record_dict[today_date_string][target_student_name] = selected_status_code
                # 保存数据到文件
                save_data_to_file()
                # 重新加载数据
                reload_data_from_file()
                # 显示状态变更提示消息
                show_snackbar_message(
                    f"{target_student_name} - {status_code_to_display_text_dict[selected_status_code]}")
                # 关闭当前弹窗
                close_dialog_function()
                # 重新打开出勤登记弹窗（刷新显示）
                open_attendance_register_dialog(None)

            # 创建学生姓名和按钮组行控件
            return ft.Row([
                # 学生姓名文本控件
                ft.Text(target_student_name, size=35, width=400),
                # 四个状态按钮行控件
                ft.Row([
                    # 出勤按钮（绿色表示选中，灰色表示未选中）
                    ft.ElevatedButton("✅ 出勤", color=ft.colors.WHITE,
                                      bgcolor=ft.colors.GREEN if current_student_status == STATUS_CODE_PRESENT else ft.colors.GREY,
                                      on_click=lambda e, s=STATUS_CODE_PRESENT: on_status_button_click(s)),
                    # 缺勤按钮
                    ft.ElevatedButton("❌ 缺勤", color=ft.colors.WHITE,
                                      bgcolor=ft.colors.GREEN if current_student_status == STATUS_CODE_ABSENT else ft.colors.GREY,
                                      on_click=lambda e, s=STATUS_CODE_ABSENT: on_status_button_click(s)),
                    # 迟到按钮
                    ft.ElevatedButton("⚠️ 迟到", color=ft.colors.WHITE,
                                      bgcolor=ft.colors.GREEN if current_student_status == STATUS_CODE_LATE else ft.colors.GREY,
                                      on_click=lambda e, s=STATUS_CODE_LATE: on_status_button_click(s)),
                    # 请假按钮
                    ft.ElevatedButton("📝 请假", color=ft.colors.WHITE,
                                      bgcolor=ft.colors.GREEN if current_student_status == STATUS_CODE_LEAVE else ft.colors.GREY,
                                      on_click=lambda e, s=STATUS_CODE_LEAVE: on_status_button_click(s)),
                ], spacing=15),  # 按钮间距 15 像素
            ], spacing=20)  # 姓名与按钮组间距 20 像素

        def refresh_attendance_list_display():
            """刷新状态列表显示"""
            # 清空现有控件
            attendance_status_list_column.controls.clear()
            # 为每个学生创建按钮组
            for each_student_name in student_name_list:
                attendance_status_list_column.controls.append(create_student_status_button_row(each_student_name))
            # 更新统计显示
            update_attendance_stats_display()

        # 初始刷新列表
        refresh_attendance_list_display()

        # 创建弹窗对话框
        attendance_register_dialog = ft.AlertDialog(
            title=ft.Text("✅ 今日出勤登记", size=45),
            content=ft.Column([
                # 日期显示
                ft.Text(f"日期：{today_date_string}", size=35),
                # 分隔线
                ft.Divider(),
                # 状态列表
                attendance_status_list_column,
                # 分隔线
                ft.Divider(),
                # 统计文本
                attendance_stats_text_control,
            ], spacing=20),
            actions=[ft.TextButton("❌ 关闭", on_click=close_dialog_function)],
        )
        # 打开弹窗
        open_dialog_function(attendance_register_dialog)

    # ==========================================================================
    # 统计报表功能
    # ==========================================================================
    def open_statistics_report_dialog(event):
        """
        打开统计报表弹窗
        功能：显示最近 30 天的出勤统计
        参数 event: 按钮点击事件对象
        """
        # 重新加载最新数据
        reload_data_from_file()

        # 创建统计列表容器（支持滚动）
        statistics_report_list_column = ft.Column(
            spacing=20,  # 设置子控件间距为 20 像素
            scroll=ft.ScrollMode.AUTO,  # 设置自动显示滚动条
            height=700  # 设置固定高度为 700 像素
        )

        # 遍历最近 30 天的记录（按日期倒序排列）
        for each_date_string in sorted(attendance_record_dict.keys(), reverse=True)[:30]:
            # 获取该日期的记录字典
            each_date_record_dict = attendance_record_dict[each_date_string]

            # 初始化各状态计数器
            present_student_count = 0  # 出勤人数
            absent_student_count = 0  # 缺勤人数
            late_student_count = 0  # 迟到人数
            leave_student_count = 0  # 请假人数

            # 统计各状态人数
            for each_student_status_value in each_date_record_dict.values():
                if each_student_status_value == STATUS_CODE_PRESENT:
                    present_student_count += 1
                elif each_student_status_value == STATUS_CODE_ABSENT:
                    absent_student_count += 1
                elif each_student_status_value == STATUS_CODE_LATE:
                    late_student_count += 1
                elif each_student_status_value == STATUS_CODE_LEAVE:
                    leave_student_count += 1

            # 计算总人数
            total_student_count = len(each_date_record_dict)
            # 计算出勤率（出勤 + 迟到）/ 总人数 * 100
            attendance_rate_percentage = ((
                                                      present_student_count + late_student_count) / total_student_count * 100) if total_student_count > 0 else 0

            # 创建统计卡片容器
            statistics_report_list_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        # 日期标题
                        ft.Text(f"📅 {each_date_string}", size=40, weight=ft.FontWeight.BOLD),
                        # 统计数据
                        ft.Text(
                            f"✅:{present_student_count}  ⚠️:{late_student_count}  ❌:{absent_student_count}  📝:{leave_student_count}  📈:{attendance_rate_percentage:.1f}%",
                            size=35),
                    ], spacing=10),
                    padding=25,  # 内边距 25 像素
                    bgcolor=ft.colors.BLUE_50,  # 浅蓝色背景
                    border_radius=15,  # 圆角 15 像素
                )
            )

        # 创建弹窗对话框
        statistics_report_dialog = ft.AlertDialog(
            title=ft.Text("📊 出勤统计报表", size=45),
            content=ft.Container(content=statistics_report_list_column, width=1200, height=800),
            actions=[ft.TextButton("❌ 关闭", on_click=close_dialog_function)],
        )
        # 打开弹窗
        open_dialog_function(statistics_report_dialog)

    # ==========================================================================
    # 导出数据功能
    # ==========================================================================
    def open_export_data_dialog(event):
        """
        打开导出数据弹窗
        功能：显示数据概览和完整记录
        参数 event: 按钮点击事件对象
        """
        # 重新加载最新数据
        reload_data_from_file()

        # 创建弹窗对话框
        export_data_dialog = ft.AlertDialog(
            title=ft.Text("📤 导出数据", size=45),
            content=ft.Column([
                # 说明文字
                ft.Text("数据已保存在 attendance_data.json", size=35),
                # 分隔线
                ft.Divider(),
                # 数据概览标题
                ft.Text("📋 数据概览", size=40, weight=ft.FontWeight.BOLD),
                # 学生总数
                ft.Text(f"学生总数：{len(student_name_list)}", size=35),
                # 记录天数
                ft.Text(f"记录天数：{len(attendance_record_dict)}", size=35),
            ], spacing=20),
            actions=[ft.TextButton("❌ 关闭", on_click=close_dialog_function)],
        )
        # 打开弹窗
        open_dialog_function(export_data_dialog)

    # ==========================================================================
    # 主界面构建
    # ==========================================================================
    # 将所有控件添加到页面
    page_object.add(
        ft.Column([
            # 应用标题（超大字体适配平板）
            ft.Text("📚 学生出勤统计系统", size=70, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE,
                    text_align=ft.TextAlign.CENTER),
            # 当前日期显示
            ft.Text(f"日期：{get_current_date_string()}", size=45, color=ft.colors.GREY_700,
                    text_align=ft.TextAlign.CENTER),
            # 透明分隔线（增加间距）
            ft.Divider(height=50, color=ft.colors.TRANSPARENT),

            # 第一行功能按钮（2x2 网格布局）
            ft.Row([
                # 学生管理按钮（蓝色）
                ft.ElevatedButton("👥 学生管理", icon=ft.icons.PEOPLE, color=ft.colors.WHITE, bgcolor=ft.colors.BLUE,
                                  expand=True, height=120,
                                  style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                                  on_click=open_student_manage_dialog),
                # 出勤登记按钮（绿色）
                ft.ElevatedButton("✅ 出勤登记", icon=ft.icons.CHECK_CIRCLE, color=ft.colors.WHITE,
                                  bgcolor=ft.colors.GREEN_700, expand=True, height=120,
                                  style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                                  on_click=open_attendance_register_dialog),
            ], spacing=40),  # 按钮间距 40 像素

            # 第二行功能按钮
            ft.Row([
                # 统计报表按钮（橙色）
                ft.ElevatedButton("📊 统计报表", icon=ft.icons.BAR_CHART, color=ft.colors.WHITE,
                                  bgcolor=ft.colors.ORANGE, expand=True, height=120,
                                  style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                                  on_click=open_statistics_report_dialog),
                # 导出数据按钮（紫色）
                ft.ElevatedButton("📤 导出数据", icon=ft.icons.UPLOAD, color=ft.colors.WHITE, bgcolor=ft.colors.PURPLE,
                                  expand=True, height=120,
                                  style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                                  on_click=open_export_data_dialog),
            ], spacing=40),

            # 透明分隔线
            ft.Divider(height=50, color=ft.colors.TRANSPARENT),

            # 今日概览卡片
            ft.Container(
                content=ft.Column([
                    # 卡片标题
                    ft.Text("📋 今日出勤概览", size=55, weight=ft.FontWeight.BOLD),
                    # 提示信息
                    ft.Text("每次启动自动清除旧数据", size=40, color=ft.colors.GREY),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),  # 子控件居中对齐
                padding=50,  # 内边距 50 像素
                bgcolor=ft.colors.BLUE_50,  # 浅蓝色背景
                border_radius=25,  # 圆角 25 像素
                expand=True,  # 占满剩余空间
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)  # 主列居中对齐
    )


# ==============================================================================
# 程序入口
# ==============================================================================
# 如果直接运行此文件（非导入），则启动应用
if __name__ == "__main__":
    # 尝试启动 Flet 应用
    try:
        # 启动 Flet 应用，main_function 函数作为入口
        ft.app(target=main_function,view=ft.AppView.FLET_APP)
    # 捕获可能发生的异常
    except Exception as error_exception:
        # 打印错误信息
        print(f"[ERROR] 程序启动失败：{error_exception}")
        # 打印提示信息
        print("[提示] 请检查 Flet 是否正确安装")
        # 打印安装命令
        print("[命令] python -m pip install flet==0.23.0")