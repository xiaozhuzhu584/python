# -*- coding: utf-8 -*-
"""
学生出勤统计系统 - Flet 0.23.0 完整注释版
功能：学生管理、出勤登记、统计报表、数据导出
特点：每次启动自动清除旧数据，使用状态码避免 emoji 匹配问题
"""

# 导入 Flet GUI 框架
import flet as ft
# 导入日期时间模块，用于获取当前日期
from datetime import datetime
# 导入 JSON 模块，用于数据序列化
import json
# 导入操作系统模块，用于文件操作
import os

# ============ 全局配置 ============
# 数据文件存储路径
DATA_FILE = "attendance_data.json"

# 全局变量：学生名单列表
STUDENTS = []
# 全局变量：出勤记录字典（日期 -> 学生状态）
RECORDS = {}

# ============ 状态码定义（内部使用，避免 emoji 匹配问题）===========
# 出勤状态码
STATUS_PRESENT = "present"
# 缺勤状态码
STATUS_ABSENT = "absent"
# 迟到状态码
STATUS_LATE = "late"
# 请假状态码
STATUS_LEAVE = "leave"

# 状态码到显示文本的映射字典（用于界面显示）
STATUS_DISPLAY = {
    STATUS_PRESENT: "✅ 出勤",  # 出勤显示文本
    STATUS_ABSENT: "❌ 缺勤",  # 缺勤显示文本
    STATUS_LATE: "⚠️ 迟到",  # 迟到显示文本
    STATUS_LEAVE: "📝 请假",  # 请假显示文本
}


# ============ 数据操作函数 ============
def clear_old_data():
    """
    清除旧数据文件
    只在程序启动时调用一次，确保每次启动都是干净的数据
    """
    # 检查数据文件是否存在
    if os.path.exists(DATA_FILE):
        try:
            # 删除旧数据文件
            os.remove(DATA_FILE)
            # 打印调试信息
            print(f"[DEBUG] 已清除旧数据文件：{DATA_FILE}")
        except Exception as e:
            # 捕获并打印删除失败的异常信息
            print(f"[DEBUG] 清除失败：{e}")


def reload_data():
    """
    从文件重新加载数据
    用于按钮点击后同步最新数据，不清空现有数据
    """
    # 声明使用全局变量
    global STUDENTS, RECORDS
    # 检查数据文件是否存在
    if os.path.exists(DATA_FILE):
        try:
            # 打开数据文件读取
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                # 解析 JSON 数据
                data = json.load(f)
                # 加载学生名单（如果是列表则使用，否则为空列表）
                STUDENTS = data.get("students", [])
                # 加载出勤记录（如果是字典则使用，否则为空字典）
                RECORDS = data.get("records", {})
        except:
            # 加载失败时静默处理，保持当前数据不变
            pass


def save_data():
    """
    保存当前数据到文件
    每次数据变更后调用，确保持久化存储
    """
    # 打开文件写入模式（会覆盖原文件）
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        # 将学生名单和出勤记录打包为字典
        # ensure_ascii=False 确保中文正常显示
        # indent=2 使 JSON 格式美观易读
        json.dump({"students": STUDENTS, "records": RECORDS}, f, ensure_ascii=False, indent=2)


def get_today():
    """
    获取当前日期字符串
    返回格式：YYYY-MM-DD（如 2026-02-22）
    """
    # 获取当前日期并格式化为字符串
    return datetime.now().strftime('%Y-%m-%d')


# ============ 主应用函数 ============
def main(page: ft.Page):
    """
    主应用入口函数
    参数 page: Flet 页面对象，用于构建 UI 界面
    """
    # 设置窗口标题
    page.title = "学生出勤统计"
    # 设置主题模式为浅色模式
    page.theme_mode = ft.ThemeMode.LIGHT
    # 设置页面内边距为 30 像素
    page.padding = 30
    # 设置窗口宽度为 1400 像素（适配平板）
    page.window.width = 1400
    # 设置窗口高度为 900 像素（适配平板）
    page.window.height = 900

    # ========== 启动时清除旧数据 ==========
    # 调用清除函数，删除旧数据文件
    clear_old_data()
    # 打印启动调试信息
    print("[DEBUG] ===== 程序启动，旧数据已清除 =====")

    # ============ 辅助函数 ============
    def show_msg(msg):
        """
        显示提示消息（Snackbar）
        参数 msg: 要显示的消息文本
        """
        # 创建 SnackBar 组件显示消息
        snackbar = ft.SnackBar(ft.Text(msg))
        # 将 SnackBar 添加到页面覆盖层
        page.overlay.append(snackbar)
        # 设置 SnackBar 为打开状态（显示）
        snackbar.open = True
        # 更新页面显示
        page.update()

    def close_dlg(e=None):
        """
        关闭当前弹窗
        参数 e: 事件对象（可选）
        """
        # 检查页面是否有弹窗
        if page.dialog:
            # 设置弹窗为关闭状态
            page.dialog.open = False
            # 更新页面显示
            page.update()

    def open_dlg(dlg):
        """
        打开指定弹窗
        参数 dlg: AlertDialog 弹窗对象
        """
        # 将弹窗设置到页面
        page.dialog = dlg
        # 设置弹窗为打开状态
        dlg.open = True
        # 更新页面显示
        page.update()

    # ============ 学生管理功能 ============
    def student_manage(e):
        """
        打开学生管理弹窗
        功能：添加学生、删除学生
        参数 e: 按钮点击事件对象
        """
        # 重新加载最新数据
        reload_data()

        # 创建姓名输入框
        name_input = ft.TextField(
            hint_text="输入学生姓名",  # 占位提示文本
            text_size=25,  # 字体大小
            expand=True  # 横向占满可用空间
        )

        # 创建学生列表容器（可滚动）
        student_list = ft.Column(
            spacing=10,  # 子控件间距 10 像素
            scroll=ft.ScrollMode.AUTO,  # 自动显示滚动条
            height=400  # 固定高度 400 像素
        )

        def refresh():
            """刷新学生列表显示"""
            # 清空列表现有控件
            student_list.controls.clear()
            # 遍历学生名单
            for i, name in enumerate(STUDENTS):
                # 捕获当前学生姓名（避免闭包问题）
                n = name

                def delete(ev):
                    """删除学生处理函数"""
                    # 声明使用全局变量
                    global STUDENTS
                    # 检查学生是否存在
                    if n in STUDENTS:
                        # 从列表中移除
                        STUDENTS.remove(n)
                        # 保存到文件
                        save_data()
                        # 显示成功提示
                        show_msg("删除成功！")
                        # 关闭弹窗
                        close_dlg()
                        # 重新打开学生管理弹窗（刷新显示）
                        student_manage(None)

                # 创建学生列表项（姓名 + 删除按钮）
                student_list.controls.append(
                    ft.Row([
                        # 显示学生序号和姓名
                        ft.Text(f"{i + 1}. {n}", size=28, expand=True),
                        # 删除按钮（红色背景）
                        ft.ElevatedButton("🗑️ 删除", color=ft.colors.WHITE, bgcolor=ft.colors.RED_700, on_click=delete),
                    ])
                )
            # 更新页面显示
            page.update()

        def add(ev):
            """添加学生处理函数"""
            # 声明使用全局变量
            global STUDENTS
            # 获取输入框内容并去除首尾空格
            name = name_input.value.strip()
            # 检查姓名是否非空
            if name:
                # 检查学生是否已存在
                if name in STUDENTS:
                    # 显示已存在提示
                    show_msg("该学生已存在！")
                else:
                    # 添加到学生列表
                    STUDENTS.append(name)
                    # 保存到文件
                    save_data()
                    # 清空输入框
                    name_input.value = ""
                    # 显示成功提示
                    show_msg("添加成功！")
                    # 刷新列表显示
                    refresh()
            else:
                # 显示输入提示
                show_msg("请输入学生姓名！")

        # 初始刷新列表
        refresh()

        # 创建弹窗对话框
        dlg = ft.AlertDialog(
            title=ft.Text("👥 学生名单管理", size=35),  # 弹窗标题
            content=ft.Column([
                # 输入框和添加按钮行
                ft.Row([name_input, ft.ElevatedButton("➕ 添加", on_click=add, expand=True)]),
                # 分隔线
                ft.Divider(),
                # 学生列表
                student_list,
            ], spacing=15),  # 子控件间距
            actions=[ft.TextButton("❌ 关闭", on_click=close_dlg)],  # 关闭按钮
        )
        # 打开弹窗
        open_dlg(dlg)

    # ============ 出勤登记功能 ============
    def attendance_manage(e):
        """
        打开出勤登记弹窗
        功能：为每个学生设置出勤状态
        参数 e: 按钮点击事件对象
        """
        # 重新加载最新数据
        reload_data()

        # 获取今日日期
        today = get_today()

        # 检查今日记录是否存在，不存在则创建
        if today not in RECORDS:
            RECORDS[today] = {}

        # 打印调试信息
        print(f"[DEBUG] ===== 出勤登记 =====")
        print(f"[DEBUG] 日期：{today}")
        print(f"[DEBUG] 学生列表：{STUDENTS}")
        print(f"[DEBUG] 今日记录：{RECORDS.get(today, {})}")

        # 创建状态列表容器（可滚动）
        status_list = ft.Column(
            spacing=15,  # 子控件间距 15 像素
            scroll=ft.ScrollMode.AUTO,  # 自动显示滚动条
            height=350  # 固定高度 350 像素
        )

        # 创建统计文本显示控件
        stats_text = ft.Text("", size=25)

        def update_stats():
            """更新出勤统计显示"""
            # 获取今日记录
            r = RECORDS.get(today, {})

            # 初始化各状态计数器
            present_count = 0  # 出勤人数
            absent_count = 0  # 缺勤人数
            late_count = 0  # 迟到人数
            leave_count = 0  # 请假人数

            # 遍历今日所有学生记录
            for student_name, status in r.items():
                # 根据状态码累加计数
                if status == STATUS_PRESENT:
                    present_count += 1
                elif status == STATUS_ABSENT:
                    absent_count += 1
                elif status == STATUS_LATE:
                    late_count += 1
                elif status == STATUS_LEAVE:
                    leave_count += 1

            # 更新统计文本显示（包含迟到人数）
            stats_text.value = f"📊 出勤:{present_count} | 迟到:{late_count} | 缺勤:{absent_count} | 请假:{leave_count} | 总计:{len(STUDENTS)}"

            # 打印调试信息
            print(f"[DEBUG] 统计 - 出勤:{present_count}, 迟到:{late_count}, 缺勤:{absent_count}, 请假:{leave_count}")
            # 更新页面显示
            page.update()

        def make_btn(student_name):
            """
            为单个学生创建状态按钮组
            参数 student_name: 学生姓名
            返回：包含学生姓名和 4 个状态按钮的行控件
            """
            # 获取该学生当前状态（默认为出勤）
            current = RECORDS.get(today, {}).get(student_name, STATUS_PRESENT)

            def on_present(ev):
                """设置为出勤状态"""
                global RECORDS
                RECORDS[today][student_name] = STATUS_PRESENT
                save_data()
                reload_data()
                show_msg(f"{student_name} - 出勤")
                close_dlg()
                attendance_manage(None)

            def on_absent(ev):
                """设置为缺勤状态"""
                global RECORDS
                RECORDS[today][student_name] = STATUS_ABSENT
                save_data()
                reload_data()
                show_msg(f"{student_name} - 缺勤")
                close_dlg()
                attendance_manage(None)

            def on_late(ev):
                """设置为迟到状态"""
                global RECORDS
                RECORDS[today][student_name] = STATUS_LATE
                save_data()
                reload_data()
                show_msg(f"{student_name} - 迟到")
                close_dlg()
                attendance_manage(None)

            def on_leave(ev):
                """设置为请假状态"""
                global RECORDS
                RECORDS[today][student_name] = STATUS_LEAVE
                save_data()
                reload_data()
                show_msg(f"{student_name} - 请假")
                close_dlg()
                attendance_manage(None)

            # 创建学生姓名和按钮组行
            return ft.Row([
                # 学生姓名文本
                ft.Text(student_name, size=28, width=250),
                # 四个状态按钮
                ft.Row([
                    # 出勤按钮（绿色表示选中）
                    ft.ElevatedButton(STATUS_DISPLAY[STATUS_PRESENT],
                                      color=ft.colors.WHITE,
                                      bgcolor=ft.colors.GREEN if current == STATUS_PRESENT else ft.colors.GREY,
                                      on_click=on_present),
                    # 缺勤按钮
                    ft.ElevatedButton(STATUS_DISPLAY[STATUS_ABSENT],
                                      color=ft.colors.WHITE,
                                      bgcolor=ft.colors.GREEN if current == STATUS_ABSENT else ft.colors.GREY,
                                      on_click=on_absent),
                    # 迟到按钮
                    ft.ElevatedButton(STATUS_DISPLAY[STATUS_LATE],
                                      color=ft.colors.WHITE,
                                      bgcolor=ft.colors.GREEN if current == STATUS_LATE else ft.colors.GREY,
                                      on_click=on_late),
                    # 请假按钮
                    ft.ElevatedButton(STATUS_DISPLAY[STATUS_LEAVE],
                                      color=ft.colors.WHITE,
                                      bgcolor=ft.colors.GREEN if current == STATUS_LEAVE else ft.colors.GREY,
                                      on_click=on_leave),
                ], spacing=8),  # 按钮间距 8 像素
            ], spacing=15)  # 姓名与按钮组间距 15 像素

        def refresh():
            """刷新状态列表显示"""
            # 清空现有控件
            status_list.controls.clear()
            # 为每个学生创建按钮组
            for name in STUDENTS:
                status_list.controls.append(make_btn(name))
            # 更新统计显示
            update_stats()

        # 初始刷新列表
        refresh()

        # 创建弹窗对话框
        dlg = ft.AlertDialog(
            title=ft.Text("✅ 今日出勤登记", size=35),
            content=ft.Column([
                # 日期显示
                ft.Text(f"日期：{today}", size=28),
                # 分隔线
                ft.Divider(),
                # 状态列表
                status_list,
                # 分隔线
                ft.Divider(),
                # 统计文本
                stats_text,
            ], spacing=15),
            actions=[
                # 保存按钮
                ft.ElevatedButton("💾 保存", on_click=lambda e: (save_data(), close_dlg(), show_msg("已保存！"))),
                # 关闭按钮
                ft.TextButton("❌ 关闭", on_click=close_dlg),
            ],
        )
        # 打开弹窗
        open_dlg(dlg)

    # ============ 统计报表功能 ============
    def statistics_manage(e):
        """
        打开统计报表弹窗
        功能：显示最近 30 天的出勤统计
        参数 e: 按钮点击事件对象
        """
        # 重新加载最新数据
        reload_data()

        # 创建统计列表容器（可滚动）
        stats_list = ft.Column(
            spacing=15,  # 子控件间距 15 像素
            scroll=ft.ScrollMode.AUTO,  # 自动显示滚动条
            height=450  # 固定高度 450 像素
        )

        # 遍历最近 30 天的记录（按日期倒序）
        for date in sorted(RECORDS.keys(), reverse=True)[:30]:
            # 获取该日期的记录
            r = RECORDS[date]

            # 初始化各状态计数器
            present_count = 0
            absent_count = 0
            late_count = 0
            leave_count = 0

            # 统计各状态人数
            for status in r.values():
                if status == STATUS_PRESENT:
                    present_count += 1
                elif status == STATUS_ABSENT:
                    absent_count += 1
                elif status == STATUS_LATE:
                    late_count += 1
                elif status == STATUS_LEAVE:
                    leave_count += 1

            # 计算总人数
            total = len(r)
            # 计算出勤率（出勤 + 迟到）/ 总人数
            rate = ((present_count + late_count) / total * 100) if total > 0 else 0

            # 创建统计卡片
            stats_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        # 日期标题
                        ft.Text(f"📅 {date}", size=30, weight=ft.FontWeight.BOLD),
                        # 统计数据
                        ft.Text(f"✅:{present_count}  ⚠️:{late_count}  ❌:{absent_count}  📝:{leave_count}  📈:{rate:.1f}%",
                                size=24),
                    ], spacing=5),
                    padding=15,  # 内边距 15 像素
                    bgcolor=ft.colors.BLUE_50,  # 浅蓝色背景
                    border_radius=10,  # 圆角 10 像素
                )
            )

        # 创建弹窗对话框
        dlg = ft.AlertDialog(
            title=ft.Text("📊 出勤统计报表", size=35),
            content=ft.Container(content=stats_list, width=800, height=500),
            actions=[ft.TextButton("❌ 关闭", on_click=close_dlg)],
        )
        # 打开弹窗
        open_dlg(dlg)

    # ============ 导出数据功能 ============
    def export_manage(e):
        """
        打开导出数据弹窗
        功能：显示数据概览和完整记录
        参数 e: 按钮点击事件对象
        """
        # 重新加载最新数据
        reload_data()

        # 将状态码转换为显示文本（便于阅读）
        display_records = {}
        for date, records in RECORDS.items():
            # 遍历该日期的所有学生记录
            display_records[date] = {s: STATUS_DISPLAY.get(st, st) for s, st in records.items()}

        # 创建弹窗对话框
        dlg = ft.AlertDialog(
            title=ft.Text("📤 导出数据", size=35),
            content=ft.Column([
                # 说明文字
                ft.Text("数据已自动保存在本地存储中", size=28),
                # 分隔线
                ft.Divider(),
                # 数据概览标题
                ft.Text("📋 数据概览", size=30, weight=ft.FontWeight.BOLD),
                # 学生总数
                ft.Text(f"学生总数：{len(STUDENTS)}", size=28),
                # 记录天数
                ft.Text(f"记录天数：{len(RECORDS)}", size=28),
                # 分隔线
                ft.Divider(),
                # 完整记录标题
                ft.Text("完整记录:", size=24),
                # 完整记录内容（状态码转显示文本）
                ft.Text(str(display_records), size=16),
            ], spacing=10, scroll=ft.ScrollMode.AUTO),  # 可滚动
            actions=[ft.TextButton("❌ 关闭", on_click=close_dlg)],
        )
        # 打开弹窗
        open_dlg(dlg)

    # ============ 主界面构建 ============
    # 将所有控件添加到页面
    page.add(
        ft.Column([
            # 应用标题
            ft.Text("📚 学生出勤统计系统", size=50, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE,
                    text_align=ft.TextAlign.CENTER),
            # 当前日期显示
            ft.Text(f"日期：{get_today()}", size=30, color=ft.colors.GREY_700, text_align=ft.TextAlign.CENTER),
            # 透明分隔线（增加间距）
            ft.Divider(height=30, color=ft.colors.TRANSPARENT),

            # 第一行功能按钮（学生管理 + 出勤登记）
            ft.Row([
                ft.ElevatedButton("👥 学生管理", icon=ft.icons.PEOPLE, color=ft.colors.WHITE, bgcolor=ft.colors.BLUE,
                                  expand=True, height=60, on_click=student_manage),
                ft.ElevatedButton("✅ 出勤登记", icon=ft.icons.CHECK_CIRCLE, color=ft.colors.WHITE,
                                  bgcolor=ft.colors.GREEN_700, expand=True, height=60, on_click=attendance_manage),
            ], spacing=20),  # 按钮间距 20 像素

            # 第二行功能按钮（统计报表 + 导出数据）
            ft.Row([
                ft.ElevatedButton("📊 统计报表", icon=ft.icons.BAR_CHART, color=ft.colors.WHITE,
                                  bgcolor=ft.colors.ORANGE, expand=True, height=60, on_click=statistics_manage),
                ft.ElevatedButton("📤 导出数据", icon=ft.icons.UPLOAD, color=ft.colors.WHITE, bgcolor=ft.colors.PURPLE,
                                  expand=True, height=60, on_click=export_manage),
            ], spacing=20),

            # 透明分隔线
            ft.Divider(height=30, color=ft.colors.TRANSPARENT),

            # 今日概览卡片
            ft.Container(
                content=ft.Column([
                    # 卡片标题
                    ft.Text("📋 今日出勤概览", size=35, weight=ft.FontWeight.BOLD),
                    # 提示信息
                    ft.Text("每次启动自动清除旧数据", size=28, color=ft.colors.GREY),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),  # 子控件居中对齐
                padding=30,  # 内边距 30 像素
                bgcolor=ft.colors.BLUE_50,  # 浅蓝色背景
                border_radius=15,  # 圆角 15 像素
                expand=True,  # 占满剩余空间
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)  # 主列居中对齐
    )


# ============ 程序入口 ============
# 如果直接运行此文件（非导入），则启动应用
if __name__ == "__main__":
    # 启动 Flet 应用，main 函数作为入口
    ft.app(target=main)