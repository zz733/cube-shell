import asyncio
import glob
import json
import os
import pickle
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import PySide6
import qdarktheme
import toml
from PySide6.QtCore import QTimer, Signal, Qt, QPoint, QRect, QEvent, QObject, Slot, QUrl, QCoreApplication, \
    QTranslator, QSize, QTimerEvent
from PySide6.QtGui import QIcon, QAction, QTextCursor, QCursor, QCloseEvent, QKeyEvent, QInputMethodEvent, QPixmap, \
    QDragEnterEvent, QDropEvent, QFont, QContextMenuEvent, QDesktopServices, QGuiApplication
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QDialog, QMessageBox, QTreeWidgetItem, \
    QInputDialog, QFileDialog, QTreeWidget, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTableWidgetItem, \
    QHeaderView, QStyle, QTabBar, QTextBrowser, QLineEdit, QListWidget, QStyledItemDelegate
from deepdiff import DeepDiff
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

from core.forwarder import ForwarderManager
from core.frequently_used_commands import TreeSearchApp
from core.mux import mux
from core.vars import ICONS, CONF_FILE, CMDS, KEYS
from function import util, about, theme, traversal
from function.ssh_func import SshClient
from function.util import format_file_size, has_valid_suffix
from style.style import updateColor
from ui import add_config, text_editor, confirm, main, auth
import icons.icons

keymap = {
    Qt.Key_Backspace: chr(127).encode(),
    Qt.Key_Escape: chr(27).encode(),
    Qt.Key_AsciiTilde: chr(126).encode(),
    Qt.Key_Up: b'\x1b[A',
    Qt.Key_Down: b'\x1b[B',
    Qt.Key_Left: b'\x1b[D',
    Qt.Key_Right: b'\x1b[C',
    Qt.Key_PageUp: "~1".encode(),
    Qt.Key_PageDown: "~2".encode(),
    Qt.Key_Home: "~H".encode(),
    Qt.Key_End: "~F".encode(),
    Qt.Key_Insert: "~3".encode(),
    Qt.Key_Delete: "~4".encode(),
    Qt.Key_F1: "~a".encode(),
    Qt.Key_F2: "~b".encode(),
    Qt.Key_F3: "~c".encode(),
    Qt.Key_F4: "~d".encode(),
    Qt.Key_F5: "~e".encode(),
    Qt.Key_F6: "~f".encode(),
    Qt.Key_F7: "~g".encode(),
    Qt.Key_F8: "~h".encode(),
    Qt.Key_F9: "~i".encode(),
    Qt.Key_F10: "~j".encode(),
    Qt.Key_F11: "~k".encode(),
    Qt.Key_F12: "~l".encode(),
}


def abspath(path):
    """
    获取当前脚本的绝对路径
    :param path:
    :return:
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'conf', path)


# 主界面逻辑
class MainDialog(QMainWindow):
    initSftpSignal = Signal()

    def __init__(self, qt_app):
        super().__init__()
        self.app = qt_app  # 将 app 传递并设置为类属性
        self.ui = main.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":logo.ico"))
        self.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.setAttribute(Qt.WA_KeyCompression, True)
        self.setFocusPolicy(Qt.WheelFocus)
        self.Shell = None
        
        # 设置标签页
        self.ui.ShellTab.setTabsClosable(True)  # 先设置所有标签页不可关闭
        icon = QIcon(":index.png")
        self.ui.ShellTab.tabBar().setTabIcon(0, icon)
        # 首页不显示关闭按钮
        self.ui.ShellTab.tabBar().setTabButton(0, QTabBar.RightSide, None)
        self.ui.ShellTab.tabBar().setTabButton(0, QTabBar.LeftSide, None)
        
        # 保存所有 QLineEdit 的列表
        self.line_edits = []

        init_config()

        # TODO 添加命令提示，还没有实现--start--
        # 自动完成提示命令行工具
        self.commands = None
        self.command_list = QListWidget(self)
        self.command_list.hide()  # 初始时隐藏
        # 示例命令
        self.commands = [
            # 文件和目录操作
            "ls", "cd", "mkdir", "rmdir", "rm", "cp", "mv", "chmod", "chown", "chgrp", "find",
            # 文本处理
            "grep", "sed", "awk", "cat", "less", "head", "tail", "cut", "paste", "sort", "uniq", "wc", "tr", "rev",
            "join", "split", "diff", "patch",
            # 编辑器
            "nano", "vim", "vi",
            # 系统信息
            "ps", "top", "htop", "kill", "pkill", "killall", "date", "cal", "uptime", "who", "w", "last", "lastlog",
            # 网络工具
            "ping", "ssh", "scp", "rsync", "netstat", "ss", "ifconfig", "ip", "route", "traceroute", "mtr", "nslookup",
            "dig", "host",
            # 文件压缩与解压
            "tar", "zip", "unzip", "gzip", "bzip2", "xz",
            # 环境配置
            "echo", "printenv", "export", "unset", "source", "alias", "unalias", "history", "source ~/.bashrc",
            "open ~/.bashrc", "nano ~/.bashrc", "vim ~/.bashrc", "vi ~/.bashrc",
            # Git 操作
            "git", "git clone", "git pull", "git push", "git add", "git commit", "git status", "git branch",
            "git checkout", "git merge", "git log", "git diff",
            # 其他
            "man", "info", "whatis", "apropos", "which", "whereis", "curl", "wget", "lynx", "telnet", "ftp", "df", "du",
            "mount", "umount"]
        self.command_list.installEventFilter(self)
        # TODO 添加命令提示，还没有实现--end--

        self.setDarkTheme()  # 默认设置为暗主题
        self.index_pwd()

        # 读取 JSON 文件内容
        util.THEME = util.read_json(abspath('theme.json'))

        # 设置拖放行为
        self.setAcceptDrops(True)

        # 菜单栏
        self.menuBarController()
        self.dir_tree_now = []
        self.file_name = ''
        self.fileEvent = ''

        # self.ssh_username, self.ssh_password, self.ssh_ip, self.key_type, self.key_file = None, None, None, None, None

        #self.ui.theme.clicked.connect(self.toggleTheme)
        self.ui.treeWidget.customContextMenuRequested.connect(self.treeRight)
        self.ui.treeWidget.doubleClicked.connect(self.cd)
        self.ui.ShellTab.currentChanged.connect(self.shell_tab_current_changed)
        # 设置选择模式为多选模式
        self.ui.treeWidget.setSelectionMode(QTreeWidget.ExtendedSelection)
        # 设置右键菜单策略
        self.ui.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        # 添加事件过滤器
        self.ui.treeWidget.viewport().installEventFilter(self)

        # 用于拖动选择的变量
        self.is_left_selecting = False
        self.start_pos = QPoint()
        self.selection_rect = QRect()

        # 安装事件过滤器来监控标签移动事件
        self.ui.ShellTab.tabBar().installEventFilter(self)
        self.homeTabPressed = False
        # 用于存储拖动开始时的标签索引
        self.originalIndex = -1

        # 连接标签页关闭信号
        self.ui.ShellTab.tabCloseRequested.connect(self.on_tab_close)

        self.isConnected = False
        self.timer_id = self.startTimer(50)
        # 连接信号和槽
        self.initSftpSignal.connect(self.on_initSftpSignal)


   
    # 删除标签页
    def _delete_tab(self):  # 删除标签页
        current_index = self.ui.ShellTab.currentIndex()
        current_index1 = self.ui.ShellTab.tabText(current_index)
        if current_index1 != "首页":
            self.ui.ShellTab.removeTab(current_index)

    # 根据标签页名字删除标签页
    def _remove_tab_by_name(self, name):
        for i in range(self.ui.ShellTab.count()):
            if self.ui.ShellTab.tabText(i) == name:
                self.ui.ShellTab.removeTab(i)
                break

    # 增加标签页
    def add_new_tab(self):
        """添加新标签页"""
        focus = self.ui.treeWidget.currentIndex().row()
        if focus != -1:
            name = self.ui.treeWidget.topLevelItem(focus).text(0)
            self.tab = QWidget()
            self.tab.setObjectName("tab")

            # 设置布局
            self.verticalLayout_index = QVBoxLayout(self.tab)
            self.verticalLayout_index.setSpacing(0)
            self.verticalLayout_index.setObjectName(u"verticalLayout_index")
            self.verticalLayout_index.setContentsMargins(0, 0, 0, 0)

            self.verticalLayout_shell = QVBoxLayout()
            self.verticalLayout_shell.setObjectName(u"verticalLayout_shell")

            # 创建文本浏览器
            self.Shell = QTextBrowser(self.tab)
            self.Shell.setReadOnly(True)
            self.Shell.setObjectName(u"Shell")
            self.Shell.setAttribute(Qt.WA_InputMethodEnabled, True)
            self.Shell.setAttribute(Qt.WA_KeyCompression, True)
            self.Shell.contextMenuEvent = self.showCustomContextMenu
            
            # 添加到布局
            self.verticalLayout_shell.addWidget(self.Shell)
            self.verticalLayout_index.addLayout(self.verticalLayout_shell)
            
            # 添加标签页
            tab_name = self.generate_unique_tab_name(name)
            tab_index = self.ui.ShellTab.addTab(self.tab, tab_name)
            self.ui.ShellTab.setCurrentIndex(tab_index)

            # 设置标签页可关闭
            if tab_index > 0:  # 不是首页
                self.ui.ShellTab.setTabsClosable(True)
                # 移除首页的关闭按钮
                #self.ui.ShellTab.tabBar().setTabButton(0, QTabBar.RightSide, None)
                #self.ui.ShellTab.tabBar().setTabButton(0, QTabBar.LeftSide, None)
            
            self.Shell.setAttribute(Qt.WA_InputMethodEnabled, True)
            self.Shell.setAttribute(Qt.WA_KeyCompression, True)
            self.Shell.contextMenuEvent = self.showCustomContextMenu

            # 连接信号和槽
            # self.Shell.cursorPositionChanged.connect(self.show_command_list)

            #if tab_index > 0:
                # 不再需要左侧的关闭按钮
            #    self.ui.ShellTab.tabBar().setTabButton(tab_index, QTabBar.LeftSide, None)
            #else:
            #    self.ui.ShellTab.tabBar().setTabButton(tab_index, QTabBar.LeftSide, None)

    # TODO 添加命令提示，还没有实现--start--
    def on_text_changed(self, text):
        # 更新命令列表
        if text:
            self.command_list.clear()
            for command in self.commands:
                if command.startswith(text):
                    self.command_list.addItem(command)
            if self.command_list.count() > 0:
                self.command_list.setCurrentRow(0)  # 选中第一个
                self.show_command_list()
            else:
                self.command_list.hide()
        else:
            self.command_list.hide()

    def show_command_list(self):
        current_index = self.ui.ShellTab.currentIndex()
        shell = self.get_text_browser_from_tab(current_index)

        # 假设 ssh_conn.screen 提供了光标的坐标
        ssh_conn = self.ssh()
        screen = ssh_conn.screen
        # 使用 filter() 函数过滤空行
        # 添加光标表示
        cursor_x = screen.cursor.x
        cursor_y = screen.cursor.y

        # 将局部坐标转换为全局坐标
        pos = shell.mapToGlobal(QPoint(cursor_x, cursor_y + 20 + shell.fontMetrics().height()))

        # 移动命令列表到计算的位置
        self.command_list.move(pos)
        max_height = min(self.command_list.sizeHint().height(), 200)  # 最大高度设为200像素
        self.command_list.resize(100, 100)
        self.command_list.show()
        shell.setFocus()  # 确保输入框始终有焦点

    def hide_command_list(self):
        self.command_list.hide()

    def select_command(self):
        # current_item = self.command_list.currentItem()
        # if current_item:
        #     self.input_box.setText(current_item.text())
        self.hide_command_list()

    # TODO 添加命令提示，还没有实现--end--

    # 生成标签名
    def generate_unique_tab_name(self, base_name):
        existing_names = [self.ui.ShellTab.tabText(i) for i in range(self.ui.ShellTab.count())]
        if base_name not in existing_names:
            return base_name

        # 如果名字相同，添加编号
        counter = 1
        new_name = f"{base_name} ({counter})"
        while new_name in existing_names:
            counter += 1
            new_name = f"{base_name} ({counter})"
        return new_name

    # 通过标签名获取标签页的 tabWhatsThis 属性
    def get_tab_whats_this_by_name(self, name):
        for i in range(self.ui.ShellTab.count()):
            if self.ui.ShellTab.tabText(i) == name:
                return self.ui.ShellTab.tabWhatsThis(i)
        return None

    def get_text_browser_from_tab(self, index):
        tab = self.ui.ShellTab.widget(index)
        if tab:
            return tab.findChild(QTextBrowser, "Shell")
        return None

    # 监听标签页切换
    def shell_tab_current_changed(self, index):
        current_index = self.ui.ShellTab.currentIndex()

        if mux.backend_index:
            current_text = self.ui.ShellTab.tabText(index)
            this = self.ui.ShellTab.tabWhatsThis(current_index)
            if this:
                ssh_conn = mux.backend_index[this]
                if current_text == "首页":
                    if ssh_conn:
                        ssh_conn.close_sig = 0
                    self.isConnected = False
                    self.ui.treeWidget.setColumnCount(1)
                    self.ui.treeWidget.setHeaderLabels(["设备列表"])
                    self.remove_last_line_edit()
                    self.ui.treeWidget.clear()
                    self.refreshConf()
                else:
                    if mux.backend_index:
                        ssh_conn.close_sig = 1
                        self.isConnected = True
                        self.refreshDirs()
            else:
                if current_text == "首页":
                    self.isConnected = False
                    self.ui.treeWidget.setColumnCount(1)
                    self.ui.treeWidget.setHeaderLabels(["设备列表"])
                    self.remove_last_line_edit()
                    self.ui.treeWidget.clear()
                    self.refreshConf()

    def index_pwd(self):
        if platform.system() == 'Darwin':
            pass
        else:
            self.ui.label_7.setText("添加配置 Shift+Ctrl+A")
            self.ui.label_11.setText("帮助 Shift+Ctrl+H")
            self.ui.label_12.setText("关于 Shift+Ctrl+B")
            self.ui.label_13.setText("查找命令行 Shift+Ctrl+C")
            self.ui.label_14.setText("导入配置 Shift+Ctrl+I")
            self.ui.label_15.setText("导出配置 Shift+Ctrl+E")

    # 进程列表初始化
    def processInitUI(self):
        # 创建表格部件
        self.ui.result.setColumnCount(6)
        # 展示表头标签
        self.ui.result.horizontalHeader().setVisible(True)
        self.ui.result.setHorizontalHeaderLabels(["PID", "用户", "内存", "CPU", "地址", "命令行"])
        header = self.ui.result.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        # 添加右键菜单
        self.ui.result.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.result.customContextMenuRequested.connect(self.showContextMenu)

        # 搜索
        self.ui.search_box.textChanged.connect(self.apply_filter)
        self.update_process_list()

    # 进程管理开始
    def showContextMenu(self, pos):
        # 获取所有选中的索引
        selected_indexes = self.ui.result.selectedIndexes()
        if not selected_indexes:
            return

        # 获取所有选中行的第一列值
        first_column_values = set()
        for index in selected_indexes:
            if index.column() == 0:
                first_column_values.add(index.data(Qt.DisplayRole))

        # 创建菜单
        menu = QMenu()
        kill_action = QAction(QIcon(':kill.png'), 'Kill 进程', self)
        menu.setCursor(QCursor(Qt.PointingHandCursor))
        kill_action.triggered.connect(lambda: self.kill_process(list(first_column_values)))
        menu.addAction(kill_action)
        menu.exec(self.ui.result.viewport().mapToGlobal(pos))

    # 进程管理结束

    def keyPressEvent(self, event):
        text = str(event.text())
        key = event.key()

        modifiers = event.modifiers()
        ctrl = modifiers == Qt.ControlModifier
        if ctrl and key == Qt.Key_Plus:
            self.zoom_in()
        elif ctrl and key == Qt.Key_Minus:
            self.zoom_out()
        else:
            if text and key != Qt.Key_Backspace:
                focus_widget = QApplication.focusWidget()
                # QLineEdit回车之后不发送命令
                if not isinstance(focus_widget, QLineEdit):
                    self.send(text.encode("utf-8"))
            else:
                s = keymap.get(key)
                if s:
                    self.send(s)

        # self.on_text_changed(text)
        event.accept()

    def keyReleaseEvent(self, event: QKeyEvent):
        if mux.backend_index:
            text = str(event.text())
            key = event.key()
            ssh_conn = self.ssh()

            if text and key == Qt.Key_Space:
                self.send(text.encode("utf-8"))
            elif text and key == Qt.Key_Tab:
                self.send(text.encode("utf-8"))
            elif key == Qt.Key_Up:
                # 点击上键查询历史命令
                self.send(b'\x1b[A')
            elif key == Qt.Key_Down:
                # 点击下键查询历史命令
                self.send(b'\x1b[B')
            elif key == Qt.Key_Left:
                ssh_conn.buffer_write = b'\x1b[D'
                self.send(b'\x1b[D')
            elif key == Qt.Key_Right:
                ssh_conn.buffer_write = b'\x1b[C'
                self.send(b'\x1b[C')

    def showEvent(self, event):
        self.center()
        super().showEvent(event)

    def center(self):
        # 获取窗口的矩形框架
        qr = self.frameGeometry()
        # 获取屏幕的中心点
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        center_point = screen_geometry.center()
        # 将窗口的中心点设置为屏幕的中心点
        qr.moveCenter(center_point)
        # 将窗口移动到新的位置
        self.move(qr.topLeft())

   

    def menuBarController(self):
        # 创建菜单栏
        menubar = self.menuBar()

        file_menu = menubar.addMenu("文件")
        # 创建“设置”菜单
        setting_menu = menubar.addMenu("设置")
        # 创建“帮助”菜单
        help_menu = menubar.addMenu("帮助")

        # 创建“新建”动作
        new_action = QAction(QIcon(":icons8-ssh-48.png"), "&新增配置", self)
        new_action.setIconVisibleInMenu(True)
        new_action.setShortcut("Shift+Ctrl+A")
        new_action.setStatusTip("添加配置")
        file_menu.addAction(new_action)
        new_action.triggered.connect(self.showAddConfig)
        # 创建“导出配置”动作
        export_configuration = QAction(QIcon(':export.png'), "&导出设备配置", self)
        export_configuration.setIconVisibleInMenu(True)
        export_configuration.setShortcut("Shift+Ctrl+E")
        export_configuration.setStatusTip("导出设备配置")
        file_menu.addAction(export_configuration)
        export_configuration.triggered.connect(self.export_configuration)

        import_configuration = QAction(QIcon(':import.png'), "&导入设备配置", self)
        import_configuration.setIconVisibleInMenu(True)
        import_configuration.setShortcut("Shift+Ctrl+I")
        import_configuration.setStatusTip("导入设备配置")
        file_menu.addAction(import_configuration)
        import_configuration.triggered.connect(self.import_configuration)

        # 创建“主题设置”动作
        theme_action = QAction(QIcon(":undo.png"), "&主题设置", self)
        theme_action.setShortcut("Shift+Ctrl+T")
        theme_action.setStatusTip("设置主题")
        setting_menu.addAction(theme_action)
        theme_action.triggered.connect(self.theme)
        #
        # # 创建“重做”动作
        # redo_action = QAction(QIcon(":redo.png"), "&Redo", self)
        # redo_action.setShortcut("Ctrl+Y")
        # redo_action.setStatusTip("Redo last undone action")
        # setting_menu.addAction(redo_action)

        # 创建“关于”动作
        about_action = QAction(QIcon(":about.png"), "&关于", self)
        about_action.setShortcut("Shift+Ctrl+B")
        about_action.setStatusTip("cubeShell 有关信息")
        help_menu.addAction(about_action)
        about_action.triggered.connect(self.about)

        linux_action = QAction(QIcon(":about.png"), "&Linux常用命令", self)
        linux_action.setShortcut("Shift+Ctrl+P")
        linux_action.setStatusTip("最常用的Linux命令查找")
        help_menu.addAction(linux_action)
        linux_action.triggered.connect(self.linux)

        help_action = QAction(QIcon(":about.png"), "&帮助", self)
        help_action.setShortcut("Shift+Ctrl+H")
        help_action.setStatusTip("cubeShell使用说明")
        help_menu.addAction(help_action)
        help_action.triggered.connect(self.help)

    # 关于
    def about(self):
        self.about_dialog = about.AboutDialog()
        self.about_dialog.show()

    def theme(self):
        self.theme_dialog = theme.MainWindow()
        self.theme_dialog.show()

    # linux 常用命令
    def linux(self):
        self.tree_search_app = TreeSearchApp()

        # 读取 JSON 数据并填充模型
        self.tree_search_app.load_data_from_json(abspath('linux_commands.json'))
        self.tree_search_app.show()

    # 帮助
    def help(self):
        url = QUrl(
            "https://mp.weixin.qq.com/s?__biz=MzA5ODQ5ODgxOQ==&mid=2247485218&idx=1&sn"
            "=f7774a9a56c1f1ae6c73d6bf6460c155&chksm"
            "=9091e74ea7e66e5816daad88313c8c559eb1d60f8da8b1d38268008ed7cff9e89225b8fe32fd&token=1771342232&lang"
            "=zh_CN#rd")
        QDesktopServices.openUrl(url)

    def eventFilter(self, source, event):
        """
        重写事件过滤器：
        treeWidget 处理鼠标左键长按拖动和鼠标左键单击
        :param source: 作用对象，这里为treeWidget
        :param event: 事件，这里为鼠标按钮按键事件
        :return:
        """
        if source is self.ui.treeWidget.viewport():
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self.start_pos = event.position().toPoint()
                    # 记录左键按下时间
                    self.left_click_time = event.timestamp()
                    return False  # 允许左键单击和双击事件继续处理
            elif event.type() == QEvent.MouseMove:
                if self.is_left_selecting:
                    self.selection_rect.setBottomRight(event.position().toPoint())
                    self.selectItemsInRect(self.selection_rect)
                    return True
            elif event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    if event.timestamp() - self.left_click_time < 200:  # 判断是否为单击
                        self.is_left_selecting = False
                        item = self.ui.treeWidget.itemAt(event.position().toPoint())
                        if item:
                            self.ui.treeWidget.clearSelection()
                            item.setSelected(True)
                        return False  # 允许左键单击事件继续处理
                    self.is_left_selecting = False
                    return True
        if source == self.ui.ShellTab.tabBar():
            if event.type() == QEvent.MouseButtonPress:
                self.originalIndex = self.ui.ShellTab.tabBar().tabAt(event.position().toPoint())
                if self.ui.ShellTab.tabText(self.originalIndex) == "首页":
                    self.homeTabPressed = True
                else:
                    self.homeTabPressed = False
            elif event.type() == QEvent.MouseMove:
                if self.homeTabPressed:
                    return True  # 忽略拖动事件
            elif event.type() == QEvent.MouseButtonRelease:
                target_index = self.ui.ShellTab.tabBar().tabAt(event.position().toPoint())
                if target_index == 0 and self.originalIndex != 0:
                    # 恢复原始位置
                    self.ui.ShellTab.tabBar().moveTab(self.ui.ShellTab.currentIndex(), self.originalIndex)
                self.homeTabPressed = False

        return super().eventFilter(source, event)

    # 在矩形内选择项目
    def selectItemsInRect(self, rect):
        # 清除所有选择
        for i in range(self.ui.treeWidget.topLevelItemCount()):
            item = self.ui.treeWidget.topLevelItem(i)
            item.setSelected(False)

        # 选择矩形内的项目
        rect = self.ui.treeWidget.visualRect(self.ui.treeWidget.indexAt(rect.topLeft()))
        rect = rect.united(self.ui.treeWidget.visualRect(self.ui.treeWidget.indexAt(rect.bottomRight())))
        for i in range(self.ui.treeWidget.topLevelItemCount()):
            item = self.ui.treeWidget.topLevelItem(i)
            if self.ui.treeWidget.visualItemRect(item).intersects(rect):
                item.setSelected(True)

    # 自定义右键菜单
    def showCustomContextMenu(self, event: QContextMenuEvent):
        # 创建一个 QMenu 对象
        menu = QMenu(self.Shell)
        menu.setStyleSheet("""
                QMenu::item {
                    padding-left: 5px;  /* 调整图标和文字之间的间距 */
                }
                QMenu::icon {
                    padding-right: 0px; /* 设置图标右侧的间距 */
                }
            """)

        # 创建复制和粘贴的 QAction 对象
        copy_action = QAction(QIcon(":copy.png"), '复制', self)
        copy_action.setIconVisibleInMenu(True)
        paste_action = QAction(QIcon(":paste.png"), '粘贴', self)
        paste_action.setIconVisibleInMenu(True)
        clear_action = QAction(QIcon(":clear.png"), '清屏', self)
        clear_action.setIconVisibleInMenu(True)

        # 绑定槽函数到 QAction 对象
        copy_action.triggered.connect(self.copy)
        paste_action.triggered.connect(self.paste)
        clear_action.triggered.connect(self.clear)

        # 将 QAction 对象添加到菜单中
        menu.addAction(copy_action)
        menu.addAction(paste_action)
        menu.addAction(clear_action)

        # 显示菜单
        menu.exec(event.globalPos())

    # 复制文本
    def copy(self):
        ssh_conn = self.ssh()

        # 获取当前选中的文本，并复制到剪贴板
        selected_text = ssh_conn.Shell.textCursor().selectedText()
        clipboard = QApplication.clipboard()
        clipboard.setText(selected_text)

    # 粘贴文本
    def paste(self):
        # 从剪贴板获取文本，并粘贴到 QTextBrowser
        clipboard = QApplication.clipboard()
        clipboard_text = clipboard.text()
        self.send(clipboard_text.encode('utf8'))

    def clear(self):
        self.send('clear'.encode('utf8') + b'\n')

    # 连接服务器
    def run(self):
        focus = self.ui.treeWidget.currentIndex().row()
        if focus != -1:
            name = self.ui.treeWidget.topLevelItem(focus).text(0)

            with open(abspath('config.dat'), 'rb') as c:
                conf = pickle.loads(c.read())[name]
                c.close()

            username, password, host, key_type, key_file = '', '', '', '', ''

            if len(conf) == 3:
                username, password, host = conf[0], conf[1], conf[2]
            else:
                username, password, host, key_type, key_file = conf[0], conf[1], conf[2], conf[3], conf[4]

            # 检查服务器是否可以连接
            if not util.check_server_accessibility(host.split(':')[0], int(host.split(':')[1])):
                # 删除当前的 tab 并显示警告消息
                self._delete_tab()
                QMessageBox.warning(self, "连接超时", "服务器无法连接，请检查网络或服务器状态。")
                return

            try:
                ssh_conn = SshClient(host.split(':')[0], int(host.split(':')[1]), username, password,
                                     key_type, key_file)

                # 启动一个线程来异步执行 SSH 连接
                threading.Thread(target=self.connect_ssh_thread, args=(ssh_conn,), daemon=True).start()
                self.ssh_username, self.ssh_password, self.ssh_ip, self.key_type, self.key_file = username, password, \
                    host, key_type, key_file
            except Exception as e:
                print(str(e))
                self.Shell.setPlaceholderText(str(e))
        else:
            self.alarm('请选择一台设备！')

    # 获取当前标签页的backend
    def ssh(self):
        current_index = self.ui.ShellTab.currentIndex()
        this = self.ui.ShellTab.tabWhatsThis(current_index)
        return mux.backend_index[this]

    def connect_ssh_thread(self, ssh_conn):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.async_connect_ssh(ssh_conn))
        finally:
            loop.close()

    async def async_connect_ssh(self, ssh_conn):
        # 创建一个线程池执行器
        executor = ThreadPoolExecutor(max_workers=1)

        # 在线程池中执行同步的 connect 方法
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, ssh_conn.connect)

        current_index = self.ui.ShellTab.currentIndex()
        ssh_conn.Shell = self.Shell
        self.ui.ShellTab.setTabWhatsThis(current_index, ssh_conn.id)

        # 异步初始化 SFTP
        self.initSftpSignal.emit()

    # 初始化sftp和控制面板
    def initSftp(self):
        ssh_conn = self.ssh()

        self.isConnected = True
        # 启动一个线程来获取系统信息
        threading.Thread(target=ssh_conn.get_datas, daemon=True).start()
        self.flushSysInfo()
        self.refreshDirs()

    def on_initSftpSignal(self):
        self.initSftp()

    # 后台获取信息，不打印至程序界面
    def getData2(self, cmd='', pty=False):
        try:
            ssh_conn = self.ssh()
            ack = ssh_conn.exec(cmd=cmd, pty=pty)
            return ack
        except Exception as e:
            self.ui.result.append(e)
            return 'error'

    # 选择文件夹
    def cd(self):
        if self.isConnected:
            focus = self.ui.treeWidget.currentIndex().row()
            if focus != -1 and self.dir_tree_now[focus][0].startswith('d'):
                ssh_conn = self.ssh()
                ssh_conn.pwd = self.getData2(
                    'cd ' + ssh_conn.pwd + '/' + self.ui.treeWidget.topLevelItem(focus).text(0) +
                    ' && pwd')[:-1]
                self.refreshDirs()
            else:
                self.editFile()
                # self.alarm('文件无法前往，右键编辑文件！')
        elif not self.isConnected:
            self.add_new_tab()
            self.run()

    # 回车获取目录
    def on_return_pressed(self):
        # 获取布局中小部件的数量
        count = self.ui.gridLayout.count()
        # 获取最后一个小部件
        if count > 0:
            latest_widget = self.ui.gridLayout.itemAt(count - 1).widget()
            # 检查是否为 QLineEdit
            if isinstance(latest_widget, QLineEdit):
                ssh_conn = self.ssh()
                text = latest_widget.text()
                ssh_conn.pwd = text
                self.refreshDirs()

    # 断开服务器
    def _off(self, name):
        this = self.get_tab_whats_this_by_name(name)
        if this and this in mux.backend_index:
            ssh_conn = mux.backend_index[this]
            if hasattr(ssh_conn, 'timer1') and ssh_conn.timer1:
                try:
                    ssh_conn.timer1.stop()
                except:
                    pass
            if hasattr(ssh_conn, 'timer2') and ssh_conn.timer2:
                try:
                    ssh_conn.timer2.stop()
                except:
                    pass
            ssh_conn.term_data = b''
            try:
                ssh_conn.close()
            except:
                pass
            self.isConnected = False
            self.ssh_username, self.ssh_password, self.ssh_ip, self.key_type, self.key_file = None, None, None, None, None
            self.ui.networkUpload.setText('')
            self.ui.networkDownload.setText('')
            self.ui.operatingSystem.setText('')

            self.ui.treeWidget.setColumnCount(1)
            self.ui.treeWidget.setHeaderLabels(["设备列表"])
            self.remove_last_line_edit()
            ssh_conn.pwd = ''
            if hasattr(self.ui, 'result'):
                self.ui.result.clear()
                # 隐藏顶部的列头
                self.ui.result.horizontalHeader().setVisible(False)
                self.ui.result.setRowCount(0)  # 设置行数为零


            self.ui.cpuRate.setValue(0)
            self.ui.diskRate.setValue(0)
            self.ui.memRate.setValue(0)

            try:
                ssh_conn.close()
            except:
                pass
            self.refreshConf()

    # 断开服务器并删除tab
    def off(self, index, name):
        self._off(name)
        self._remove_tab_by_name(name)

    # 关闭当前连接
    def disc_off(self):
        current_index = self.ui.ShellTab.currentIndex()
        name = self.ui.ShellTab.tabText(current_index)
        if name != "首页":
            self._off(name)
            self._remove_tab_by_name(name)

    def timerEvent(self, event: QTimerEvent):
        if event.timerId() == self.timer_id:
            try:
                ssh_conn = self.ssh()
                if not ssh_conn.screen.dirty:
                    if ssh_conn.buffer_write:
                        self.updateTerminal(ssh_conn)
                        ssh_conn.buffer_write = b''
                    return
                self.updateTerminal(ssh_conn)
                self.update()
            except Exception as e:
                pass
        else:
            # 确保处理其他定时器事件
            super().timerEvent(event)

    # 更新终端输出
    def updateTerminal(self, ssh_conn):
        current_index = self.ui.ShellTab.currentIndex()
        shell = self.get_text_browser_from_tab(current_index)

        font_ = util.THEME['font']
        theme_ = util.THEME['theme']
        color_ = util.THEME['theme_color']

        font = QFont(font_, 14)
        shell.setFont(font)

        shell.moveCursor(QTextCursor.End)
        screen = ssh_conn.screen
        # 使用 filter() 函数过滤空行
        # 添加光标表示
        cursor_x = screen.cursor.x
        cursor_y = screen.cursor.y
        lines = screen.display
        if cursor_y < len(lines):
            line = lines[cursor_y]
            lines[cursor_y] = line[:cursor_x] + '▉' + line[cursor_x:]
        filtered_lines = list(filter(lambda x: x.strip(), lines))

        terminal_str = '\n'.join(filtered_lines)

        shell.clear()
        # 使用Pygments进行语法高亮
        formatter = HtmlFormatter(style=theme_, noclasses=True, bg_color='#ffffff')
        shell.setStyleSheet("background-color: " + color_ + ";")
        filtered_data = terminal_str.rstrip().replace("\0", " ")

        pattern = r'\s+(?=\n)'
        result = re.sub(pattern, '', filtered_data)
        special_lines = util.remove_special_lines(result)
        replace = special_lines.replace("                        ", "")

        # 第一次打开渲染banner
        if "Last login:" in terminal_str:
            # 高亮代码
            highlighted2 = highlight(util.BANNER + replace, PythonLexer(), formatter)
        else:
            # 高亮代码
            highlighted2 = highlight(replace, PythonLexer(), formatter)

        # 将HTML插入QTextBrowser
        shell.setHtml(highlighted2)

        shell.moveCursor(QTextCursor.End)

        # 如果没有这串代码，执行器就会疯狂执行代码
        ssh_conn.screen.dirty.clear()

    def send(self, data):
        if mux.backend_index:
            ssh_conn = self.ssh()
            ssh_conn.write(data)

    def do_killall_ssh(self):
        for tunnel in self.tunnels:
            tunnel.stop_tunnel()
        if os.name == 'nt':
            os.system(CMDS.SSH_KILL_WIN)
        else:
            os.system(CMDS.SSH_KILL_NIX)

    def closeEvent(self, event):
        # 关闭定时起动器
        if self.timer_id is not None:
            self.killTimer(self.timer_id)
            self.timer_id = None
        """
         窗口关闭事件 当存在通道的时候关闭通道
         不存在时结束多路复用器的监听
        :param event: 关闭事件
        :return: None
        """
        # ssh_conn = self.ssh()
        # if mux.backend_index:
        #     for key, ssh_conn in mux.backend_index.items():
        #         if ssh_conn:
        #             ssh_conn.close()
        mux.stop()

        """
        该函数处理窗口关闭事件，主要功能包括：
        遍历所有隧道（tunnel）并收集其配置信息。
        检查收集到的配置与原始数据是否有差异。
        如果有差异，则备份当前配置文件，并将新配置写入。
        限制备份文件数量不超过10个，多余备份将被删除。
        最终接受关闭事件。
        :param event:
        :return:
        """
        data = {}
        
        event.accept()

    def inputMethodEvent(self, a0: QInputMethodEvent) -> None:
        cmd = a0.commitString()
        if cmd != '':
            self.send(cmd.encode('utf8'))

    # 创建左侧列表树右键菜单函数
    def treeRight(self):
        if not self.isConnected:
            # 菜单对象
            self.ui.tree_menu = QMenu(self)
            self.ui.tree_menu.setStyleSheet("""
                QMenu::item {
                    padding-left: 5px;  /* 调整图标和文字之间的间距 */
                }
                QMenu::icon {
                    padding-right: 0px; /* 设置图标右侧的间距 */
                }
            """)
            # 创建菜单选项对象
            self.ui.action = QAction(QIcon(':addConfig.png'), '添加配置', self)
            self.ui.action.setIconVisibleInMenu(True)
            self.ui.action1 = QAction(QIcon(':addConfig.png'), '编辑配置', self)
            self.ui.action1.setIconVisibleInMenu(True)
            self.ui.action2 = QAction(QIcon(':delConf.png'), '删除配置', self)
            self.ui.action2.setIconVisibleInMenu(True)
            # 把动作选项对象添加到菜单self.groupBox_menu上
            self.ui.tree_menu.addAction(self.ui.action)
            self.ui.tree_menu.addAction(self.ui.action1)
            self.ui.tree_menu.addAction(self.ui.action2)
            # 将动作A触发时连接到槽函数 button
            self.ui.action.triggered.connect(self.showAddConfig)

            selected_items = self.ui.treeWidget.selectedItems()
            if selected_items:
                self.ui.action.setVisible(False)
                self.ui.action1.setVisible(True)
            else:
                self.ui.action.setVisible(True)
                self.ui.action1.setVisible(False)
                self.ui.action2.setVisible(False)

            self.ui.action1.triggered.connect(self.editConfig)
            self.ui.action2.triggered.connect(self.delConf)

            # 声明当鼠标在groupBox控件上右击时，在鼠标位置显示右键菜单   ,exec_,popup两个都可以，
            self.ui.tree_menu.popup(QCursor.pos())
        elif self.isConnected:
            self.ui.tree_menu = QMenu(self)
            # 设置菜单样式表来调整图标和文字之间的间距
            self.ui.tree_menu.setStyleSheet("""
                QMenu::item {
                    padding-left: 5px;  /* 调整图标和文字之间的间距 */
                }
                QMenu::icon {
                    padding-right: 0px; /* 设置图标右侧的间距 */
                }
            """)

            self.ui.action1 = QAction(QIcon(':Download.png'), '下载文件', self)
            self.ui.action1.setIconVisibleInMenu(True)
            self.ui.action2 = QAction(QIcon(':Upload.png'), '上传文件', self)
            self.ui.action2.setIconVisibleInMenu(True)
            self.ui.action3 = QAction(QIcon(':Edit.png'), '编辑文本', self)
            self.ui.action3.setIconVisibleInMenu(True)
            self.ui.action4 = QAction(QIcon(':createdirector.png'), '创建文件夹', self)
            self.ui.action4.setIconVisibleInMenu(True)
            self.ui.action5 = QAction(QIcon(':createfile.png'), '创建文件', self)
            self.ui.action5.setIconVisibleInMenu(True)
            self.ui.action6 = QAction(QIcon(':refresh.png'), '刷新', self)
            self.ui.action6.setIconVisibleInMenu(True)
            self.ui.action7 = QAction(QIcon(':remove.png'), '删除', self)
            self.ui.action7.setIconVisibleInMenu(True)
            self.ui.action8 = QAction(QIcon(':icons-rename-48.png'), '重命名', self)
            self.ui.action8.setIconVisibleInMenu(True)

            self.ui.action9 = QAction(QIcon(':icons-unzip-48.png'), '解压', self)
            self.ui.action9.setIconVisibleInMenu(True)
            self.ui.action10 = QAction(QIcon(':icons8-zip-48.png'), '新建压缩', self)
            self.ui.action10.setIconVisibleInMenu(True)

            self.ui.tree_menu.addAction(self.ui.action1)
            self.ui.tree_menu.addAction(self.ui.action2)
            self.ui.tree_menu.addAction(self.ui.action3)
            self.ui.tree_menu.addAction(self.ui.action4)
            self.ui.tree_menu.addAction(self.ui.action5)
            self.ui.tree_menu.addAction(self.ui.action6)

            # 在子菜单中添加动作
            file_action = QAction("权限", self)
            file_action.setIcon(QIcon(":permissions-48.png"))
            file_action.setIconVisibleInMenu(True)
            file_action.triggered.connect(self.show_auth)
            self.ui.tree_menu.addAction(file_action)

            # 添加分割线,做标记区分
            bottom_separator = QAction(self)
            bottom_separator.setSeparator(True)
            self.ui.tree_menu.addAction(bottom_separator)
            self.ui.tree_menu.addAction(self.ui.action7)
            self.ui.tree_menu.addAction(self.ui.action8)

            # 添加分割线,做标记区分
            bottom_separator = QAction(self)
            bottom_separator.setSeparator(True)
            self.ui.tree_menu.addAction(bottom_separator)

            self.ui.tree_menu.addAction(self.ui.action9)
            self.ui.tree_menu.addAction(self.ui.action10)

            self.ui.action1.triggered.connect(self.downloadFile)
            self.ui.action2.triggered.connect(self.uploadFile)
            self.ui.action3.triggered.connect(self.editFile)
            self.ui.action4.triggered.connect(self.createDir)
            self.ui.action5.triggered.connect(self.createFile)
            self.ui.action6.triggered.connect(self.refresh)
            self.ui.action7.triggered.connect(self.remove)
            self.ui.action8.triggered.connect(self.rename)
            self.ui.action9.triggered.connect(self.unzip)
            self.ui.action10.triggered.connect(self.zip)

            # 声明当鼠标在groupBox控件上右击时，在鼠标位置显示右键菜单   ,exec_,popup两个都可以，
            self.ui.tree_menu.popup(QCursor.pos())


    # 打开增加配置界面
    def showAddConfig(self):
        self.ui.addconfwin = AddConfigUi()
        self.ui.addconfwin.show()
        self.ui.addconfwin.dial.pushButton.clicked.connect(self.refreshConf)
        self.ui.addconfwin.dial.pushButton_2.clicked.connect(self.ui.addconfwin.close)

    # 打开编辑配置界面
    def editConfig(self):
        selected_items = self.ui.treeWidget.selectedItems()
        self.ui.addconfwin = AddConfigUi()
        # 检查是否有选中的项
        if selected_items:
            if len(selected_items) > 1:
                QMessageBox.warning(self, '警告', '只能编辑一个设备')
                return
            # 遍历选中的项
            for item in selected_items:
                # 获取项的内容
                name = item.text(0)
                with open(abspath('config.dat'), 'rb') as c:
                    conf = pickle.loads(c.read())[name]

                if len(conf) == 3:
                    username, password, host = conf[0], conf[1], conf[2]
                else:
                    username, password, host, key_type, key_file = conf[0], conf[1], conf[2], conf[3], conf[4]
                    self.ui.addconfwin.dial.comboBox.setCurrentText(key_type)
                    self.ui.addconfwin.dial.lineEdit.setText(key_file)

                self.ui.addconfwin.dial.configName.setText(name)
                self.ui.addconfwin.dial.usernamEdit.setText(username)
                self.ui.addconfwin.dial.passwordEdit.setText(password)
                self.ui.addconfwin.dial.ipEdit.setText(host.split(':')[0])
                self.ui.addconfwin.dial.protEdit.setText(host.split(':')[1])

        self.ui.addconfwin.show()
        self.ui.addconfwin.dial.pushButton.clicked.connect(self.refreshConf)
        self.ui.addconfwin.dial.pushButton_2.clicked.connect(self.ui.addconfwin.close)

  

    # 导出配置
    def export_configuration(self):
        src_path = abspath('config.dat')
        # 选择保存文件夹
        directory = QFileDialog.getExistingDirectory(
            None,  # 父窗口，这里为None表示没有父窗口
            '选择保存文件夹',  # 对话框标题
            '',  # 默认打开目录
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks  # 显示选项
        )
        if directory:
            os.makedirs(f'{directory}/config', exist_ok=True)
            # 复制文件
            shutil.copy2(str(src_path), f'{directory}/config/config.dat')
            self.success("导出成功")

    # 导入配置
    def import_configuration(self):
        config = abspath('config.dat')

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "所有文件 (*);;json 文件 (*.json)",
        )
        if file_name:
            # 如果目标文件存在，则删除它
            if os.path.exists(config):
                os.remove(config)
            # 复制文件
            shutil.copy2(str(file_name), str(config))

        self.refreshConf()

    # 刷新设备列表
    def refreshConf(self):
        config = abspath('config.dat')
        with open(config, 'rb') as c:
            dic = pickle.loads(c.read())
            c.close()
        i = 0
        self.ui.treeWidget.clear()

        self.ui.treeWidget.headerItem().setText(0, QCoreApplication.translate("MainWindow", "设备列表"))

        for k in dic.keys():
            self.ui.treeWidget.addTopLevelItem(QTreeWidgetItem(0))
            # 设置字体为加粗
            bold_font = QFont()
            bold_font.setPointSize(14)  # 设置字体大小为16
            # Mac 系统设置，其他系统不设置，否则会很大
            if platform.system() == 'Darwin':
                # 设置字体为加粗
                bold_font.setPointSize(15)  # 设置字体大小为16
                bold_font.setBold(True)
            self.ui.treeWidget.topLevelItem(i).setFont(0, bold_font)
            self.ui.treeWidget.topLevelItem(i).setText(0, k)
            self.ui.treeWidget.topLevelItem(i).setIcon(0, QIcon(':icons8-ssh-48.png'))
            i += 1

    def add_line_edit(self, q_str):
        # 创建一个新的 QLineEdit
        line_edit = QLineEdit()
        line_edit.setFocusPolicy(Qt.ClickFocus)
        line_edit.setText(q_str)
        # 保存新创建的 QLineEdit
        self.line_edits.append(line_edit)
        # 将 QLineEdit 添加到布局中
        self.ui.gridLayout.addWidget(line_edit, 0, 0, 1, 1)
        line_edit.returnPressed.connect(self.on_return_pressed)

    # 删除 QLineEdit
    def remove_last_line_edit(self):
        if self.line_edits:
            for line_edit in self.line_edits:
                self.ui.gridLayout.removeWidget(line_edit)
                line_edit.deleteLater()
            # 清空 QLineEdit 列表
            self.line_edits.clear()

    # 当前目录列表刷新
    def refreshDirs(self):
        ssh_conn = self.ssh()
        ssh_conn.pwd, files = self.getDirNow()
        self.dir_tree_now = files[1:]
        self.ui.treeWidget.setHeaderLabels(["文件名", "文件大小", "修改日期", "权限", "所有者/组"])
        self.add_line_edit(ssh_conn.pwd)  # 添加一个初始的 QLineEdit
        self.ui.treeWidget.clear()
        i = 0
        for n in files[1:]:
            self.ui.treeWidget.addTopLevelItem(QTreeWidgetItem(0))
            self.ui.treeWidget.topLevelItem(i).setText(0, n[8])
            size_in_bytes = int(n[4].replace(",", ""))
            self.ui.treeWidget.topLevelItem(i).setText(1, format_file_size(size_in_bytes))
            self.ui.treeWidget.topLevelItem(i).setText(2, n[5] + ' ' + n[6] + ' ' + n[7])
            self.ui.treeWidget.topLevelItem(i).setText(3, n[0])
            self.ui.treeWidget.topLevelItem(i).setText(4, n[3])
            # 设置图标
            if n[0].startswith('d'):
                # 获取默认的文件夹图标
                folder_icon = util.get_default_folder_icon()
                self.ui.treeWidget.topLevelItem(i).setIcon(0, folder_icon)
            elif n[0][0] in ['l', '-', 's']:
                file_icon = util.get_default_file_icon(n[8])
                self.ui.treeWidget.topLevelItem(i).setIcon(0, file_icon)
            i += 1

    # 获取当前目录列表
    def getDirNow(self):
        ssh_conn = self.ssh()
        pwd = self.getData2('cd ' + ssh_conn.pwd.replace("//", "/") + ' && pwd')
        dir_info = self.getData2(cmd='cd ' + ssh_conn.pwd.replace("//", "/") + ' && ls -al').split('\n')
        dir_n_info = []
        for d in dir_info:
            d_list = ssh_conn.del_more_space(d)
            if d_list:
                dir_n_info.append(d_list)
            else:
                pass
        return pwd[:-1], dir_n_info

    # 打开文件编辑窗口
    def editFile(self):
        items = self.ui.treeWidget.selectedItems()
        if len(items) > 1:
            self.alarm('只能编辑一个文件！')
            return
        focus = self.ui.treeWidget.currentIndex().row()
        if focus != -1 and self.dir_tree_now[focus][0].startswith('-'):
            self.file_name = self.ui.treeWidget.currentItem().text(0)
            if has_valid_suffix(self.file_name):
                self.alarm('不支持编辑此文件！')
                return
            ssh_conn = self.ssh()
            text = self.getData2('cat ' + ssh_conn.pwd + '/' + self.file_name)
            if text != 'error' and text != '\n':
                self.ui.addTextEditWin = TextEditor(title=self.file_name, old_text=text)
                self.ui.addTextEditWin.show()
                self.ui.addTextEditWin.save_tex.connect(self.getNewText)
            elif text == 'error' or text == '\n':
                self.alarm('无法编辑文件，请确认！')
        elif focus != -1 and self.dir_tree_now[focus][0].startswith('lr'):
            self.alarm('此文件不能直接编辑！')
        else:
            self.alarm('文件夹不能被编辑！')

    def createDir(self):
        ssh_conn = self.ssh()
        dialog = QInputDialog(self)
        dialog.setWindowTitle('创建文件夹')
        dialog.setLabelText('文件夹名字:')
        dialog.setFixedSize(400, 150)

        # 显示对话框并获取结果
        ok = dialog.exec()
        text = dialog.textValue()

        if ok:
            sftp = ssh_conn.open_sftp()
            pwd_text = ssh_conn.pwd + '/' + text

            # 如果路径不存在，则创建目录
            if not util.check_remote_directory_exists(sftp, pwd_text):
                try:
                    # 目录不存在，创建目录
                    sftp.mkdir(pwd_text)
                    self.refreshDirs()
                except Exception as create_error:
                    print(f"An error occurred: {create_error}")
                    self.alarm('创建文件夹失败，请联系开发作者')
            else:
                self.alarm('文件夹已存在')

    # 创建文件
    def createFile(self):
        ssh_conn = self.ssh()
        dialog = QInputDialog(self)
        dialog.setWindowTitle('创建文件')
        dialog.setLabelText('文件名字:')
        dialog.setFixedSize(400, 150)

        # 显示对话框并获取结果
        ok = dialog.exec()
        text = dialog.textValue()

        if ok:
            sftp = ssh_conn.open_sftp()
            pwd_text = ssh_conn.pwd + '/' + text
            try:
                with sftp.file(pwd_text, 'w'):
                    pass  # 不写入任何内容
                self.refreshDirs()
            except IOError as e:
                print(f"创建文件出现异常: {e}")
                self.alarm('创建文件失败，请联系开发作者')

    # 获取返回信息，并保存文件
    def getNewText(self, new_list):
        ssh_conn = self.ssh()
        nt, sig = new_list[0], new_list[1]
        # 将双引号转义为转义字符
        escaped_string = nt.replace("\"", '\\"')
        if sig == 0:
            self.getData2('echo -e "' + escaped_string + '" > ' + ssh_conn.pwd + '/' + self.file_name)
            self.ui.addTextEditWin.new_text = self.ui.addTextEditWin.old_text
            self.ui.addTextEditWin.te.chk.close()
            self.ui.addTextEditWin.close()
        elif sig == 1:
            self.getData2('echo -e "' + escaped_string + '" > ' + ssh_conn.pwd + '/' + self.file_name)
            self.ui.addTextEditWin.old_text = nt

    # 删除设备配置文件
    def delConf(self):
        # 创建消息框
        reply = QMessageBox()
        reply.setWindowTitle('确认删除')
        reply.setText(f'您确定要删除选中设备吗？这将无法恢复！')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # 设置按钮文本为中文
        yes_button = reply.button(QMessageBox.Yes)
        no_button = reply.button(QMessageBox.No)
        yes_button.setText("确定")
        no_button.setText("取消")
        # 显示对话框并等待用户响应
        reply.exec()
        if reply.clickedButton() == yes_button:
            selected_items = self.ui.treeWidget.selectedItems()
            # 检查是否有选中的项
            if selected_items:
                # 遍历选中的项
                for item in selected_items:
                    # 获取项的内容
                    name = item.text(0)
                    config = abspath('config.dat')
                    with open(config, 'rb') as c:
                        conf = pickle.loads(c.read())
                    with open(config, 'wb') as c:
                        del conf[name]
                        c.write(pickle.dumps(conf))
                self.refreshConf()

    # 定时刷新设备状态信息
    def flushSysInfo(self):
        ssh_conn = self.ssh()

        timer1 = QTimer()
        timer1.start(1000)
        ssh_conn.timer1 = timer1
        ssh_conn.timer1.timeout.connect(self.refreshSysInfo)

    # 刷新设备状态信息功能
    def refreshSysInfo(self):
        if self.isConnected:
            current_index = self.ui.ShellTab.currentIndex()
            this = self.ui.ShellTab.tabWhatsThis(current_index)
            if this and this in mux.backend_index:
                ssh_conn = mux.backend_index[this]
                if hasattr(ssh_conn, 'system_info_dict'):
                    system_info_dict = ssh_conn.system_info_dict
                    cpu_use = ssh_conn.cpu_use if hasattr(ssh_conn, 'cpu_use') else 0
                    mem_use = ssh_conn.mem_use if hasattr(ssh_conn, 'mem_use') else 0
                    dissk_use = ssh_conn.disk_use if hasattr(ssh_conn, 'disk_use') else 0
                    # 上行
                    transmit_speed = ssh_conn.transmit_speed if hasattr(ssh_conn, 'transmit_speed') else 0
                    # 下行
                    receive_speed = ssh_conn.receive_speed if hasattr(ssh_conn, 'receive_speed') else 0

                    self.ui.cpuRate.setValue(cpu_use)
                    self.ui.cpuRate.setStyleSheet(updateColor(cpu_use))
                    self.ui.memRate.setValue(mem_use)
                    self.ui.memRate.setStyleSheet(updateColor(mem_use))
                    self.ui.diskRate.setValue(dissk_use)
                    self.ui.diskRate.setStyleSheet(updateColor(dissk_use))

                    # 自定义显示格式
                    self.ui.networkUpload.setText(util.format_speed(transmit_speed))
                    self.ui.networkDownload.setText(util.format_speed(receive_speed))
                    if 'Operating System' in system_info_dict:
                        self.ui.operatingSystem.setText(system_info_dict['Operating System'])

        else:
            self.ui.cpuRate.setValue(0)
            self.ui.memRate.setValue(0)
            self.ui.diskRate.setValue(0)
            self.ui.networkUpload.setText('')
            self.ui.networkDownload.setText('')
            self.ui.operatingSystem.setText('')

    # 下载文件
    def downloadFile(self):
        try:
            # 选择保存文件夹
            directory = QFileDialog.getExistingDirectory(
                None,  # 父窗口，这里为None表示没有父窗口
                '选择保存文件夹',  # 对话框标题
                '',  # 默认打开目录
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks  # 显示选项
            )
            if directory:
                ssh_conn = self.ssh()
                items = self.ui.treeWidget.selectedItems()
                sftp = ssh_conn.open_sftp()
                for item in items:
                    item_text = item.text(0)
                    sftp.get(ssh_conn.pwd + '/' + item_text, f'{directory}/{item_text}')

            self.success("下载文件")
        except Exception as e:
            print(e)
            self.alarm('无法下载文件，请确认！')

    # 上传文件
    def uploadFile(self):
        # 打开文件对话框让用户选择文件
        files, _ = QFileDialog.getOpenFileNames(self, "选择文件", "", "所有文件 (*)")
        if files:
            for file_path in files:
                if os.path.isfile(file_path):
                    self.fileEvent = file_path
                    ssh_conn = self.ssh()
                    sftp = ssh_conn.open_sftp()
                    try:
                        sftp.put(file_path, ssh_conn.pwd + '/' + os.path.basename(file_path))
                    except IOError as e:
                        print(f"Failed to upload file: {e}")
            self.refreshDirs()

    # 刷新
    def refresh(self):
        self.refreshDirs()

    def show_auth(self):
        self.ui.auth = Auth(self)
        selected_items = self.ui.treeWidget.selectedItems()
        # 先取出所有选中项目
        for item in selected_items:
            # 去掉第一个字符
            trimmed_str = item.text(3)[1:]
            # 转换为列表
            permission_list = list(trimmed_str)
            self.ui.auth.dial.checkBoxUserR.setChecked(permission_list[0] != '-')
            self.ui.auth.dial.checkBoxUserW.setChecked(permission_list[1] != '-')
            self.ui.auth.dial.checkBoxUserX.setChecked(permission_list[2] != '-')
            self.ui.auth.dial.checkBoxGroupR.setChecked(permission_list[3] != '-')
            self.ui.auth.dial.checkBoxGroupW.setChecked(permission_list[4] != '-')
            self.ui.auth.dial.checkBoxGroupX.setChecked(permission_list[5] != '-')
            self.ui.auth.dial.checkBoxOtherR.setChecked(permission_list[6] != '-')
            self.ui.auth.dial.checkBoxOtherW.setChecked(permission_list[7] != '-')
            self.ui.auth.dial.checkBoxOtherX.setChecked(permission_list[8] != '-')
            break
        self.ui.auth.show()

    # 删除
    def remove(self):
        ssh_conn = self.ssh()
        # 创建消息框
        reply = QMessageBox()
        reply.setWindowTitle('确认删除')
        reply.setText(f'确定删除选中项目吗？这将无法恢复！')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # 设置按钮文本为中文
        yes_button = reply.button(QMessageBox.Yes)
        no_button = reply.button(QMessageBox.No)
        yes_button.setText("是")
        no_button.setText("否")
        # 显示对话框并等待用户响应
        reply.exec()

        if reply.clickedButton() == yes_button:
            rm_dict = dict()
            selected_items = self.ui.treeWidget.selectedItems()
            # 先取出所有选中项目
            for item in selected_items:
                # key：为文件名 value：是否为文件夹
                rm_dict[item.text(0)] = item.text(3).startswith('d')
            sftp = ssh_conn.open_sftp()
            # 批量删除
            for key, value in rm_dict.items():
                try:
                    if value:
                        util.deleteFolder(sftp, ssh_conn.pwd + '/' + key)
                    else:
                        sftp.remove(ssh_conn.pwd + '/' + key)
                except IOError as e:
                    print(f"Failed to remove file: {e}")
            rm_dict.clear()
            self.refreshDirs()

    # 压缩 tar
    def zip(self):
        ssh_conn = self.ssh()
        selected_items = self.ui.treeWidget.selectedItems()
        # 要压缩的远程文件列表
        remote_files = []
        # 压缩文件名
        output_file = ""
        # 先取出所有选中项目
        for item in selected_items:
            item_text = item.text(0)
            remote_files.append(ssh_conn.pwd + '/' + item_text)
            s = str(item_text).lstrip('.')
            base_name, ext = os.path.splitext(s)
            output_file = f'{ssh_conn.pwd}/{base_name}.tar.gz'

        # 构建压缩命令
        files_str = ' '.join(remote_files)
        compress_command = f"tar -czf {output_file} {files_str}"
        ssh_conn.exec(compress_command)
        self.refreshDirs()

    def rename(self):
        ssh_conn = self.ssh()
        selected_items = self.ui.treeWidget.selectedItems()
        for item in selected_items:
            item_text = item.text(0)
            new_name = QInputDialog.getText(self, '重命名', '请输入新的文件名：', QLineEdit.Normal, item_text)
            if new_name[1]:
                new_name = new_name[0]
                ssh_conn.exec(f'mv {ssh_conn.pwd}/{item_text} {ssh_conn.pwd}/{new_name}')
                self.refreshDirs()

    # 解压 tar
    def unzip(self):
        ssh_conn = self.ssh()
        selected_items = self.ui.treeWidget.selectedItems()
        # 构建解压命令
        decompress_commands = []
        for item in selected_items:
            item_text = item.text(0)
            tar_file = ssh_conn.pwd + '/' + item_text
            decompress_commands.append(f"tar -xzvf {tar_file} -C {ssh_conn.pwd}")

        # 合并解压命令
        combined_command = " && ".join(decompress_commands)
        ssh_conn.exec(combined_command)
        self.refreshDirs()

    # 停止docker容器
    def stopDockerContainer(self):
        focus = self.ui.treeWidgetDocker.currentIndex().row()
        if focus != -1:
            text = self.ui.treeWidgetDocker.topLevelItem(focus).text(0)
            # 取出前12位字符串
            container_id = text[:12]
            data_ = self.getData2('docker stop ' + container_id)
            print('stop----', data_)
            time.sleep(1)  # 延迟一秒
            self.refreshDokerInfo()

   

    # 删除文件夹
    def removeDir(self):
        ssh_conn = self.ssh()
        focus = self.ui.treeWidget.currentIndex().row()
        if focus != -1:
            text = self.ui.treeWidget.topLevelItem(focus).text(0)
            sftp = ssh_conn.open_sftp()
            try:
                sftp.rmdir(ssh_conn.pwd + '/' + text)
                self.refreshDirs()
            except IOError as e:
                print(f"Failed to remove directory: {e}")
        pass

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    # 拖拉拽上传文件
    def dropEvent(self, event: QDropEvent):
        ssh_conn = self.ssh()
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            for url in mime_data.urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    self.fileEvent = file_path
                    sftp = ssh_conn.open_sftp()
                    try:
                        sftp.put(file_path, ssh_conn.pwd + '/' + os.path.basename(file_path))
                    except IOError as e:
                        print(f"Failed to upload file: {e}")
            self.refreshDirs()

    # 信息提示窗口
    def alarm(self, alart):
        """
        创建一个错误消息框，并设置自定义图标
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('操作失败')
        msg_box.setText(f'{alart}')

        # 加载自定义图标
        custom_icon = QIcon(':icons8-fail-48.png')
        pixmap = QPixmap(custom_icon.pixmap(32, 32))

        # 设置消息框图标
        msg_box.setIconPixmap(pixmap)

        # 显示消息框
        msg_box.exec()

    # 成功提示窗口
    def success(self, alart):
        """
        创建一个成功消息框，并设置自定义图标
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('操作成功')
        msg_box.setText(f'{alart}成功')

        # 加载自定义图标
        custom_icon = QIcon(':icons8-success-48.png')  # 替换为你的图标路径
        pixmap = QPixmap(custom_icon.pixmap(32, 32))

        # 设置消息框图标
        msg_box.setIconPixmap(pixmap)

        # 显示消息框
        msg_box.exec()

    def inputMethodQuery(self, a0):
        pass
        # print(a0)

    # 设置主题
    def setDarkTheme(self):
        # self.app.setStyleSheet(qdarkstyle.load_stylesheet(palette=DarkPalette))
        self.app.setStyleSheet(
            qdarktheme.load_stylesheet(
                custom_colors={
                    "[dark]": {
                        "primary": "#00A1FF",
                    }
                },
            )
        )

    def setLightTheme(self):
        # self.app.setStyleSheet(qdarkstyle.load_stylesheet(palette=LightPalette))
        self.app.setStyleSheet(
            qdarktheme.load_stylesheet(
                theme="light",
                custom_colors={
                    "[light]": {
                        "primary": "#E05B00",
                    }
                },
            )
        )

    def toggleTheme(self):
        sheet = self.app.styleSheet()
        stylesheet = qdarktheme.load_stylesheet(custom_colors={"[dark]": {"primary": "#00A1FF", }}, )
        if self.app.styleSheet() == stylesheet:
            self.setLightTheme()
        else:
            self.setDarkTheme()


    # 处理标签页关闭事件
    def on_tab_close(self, index):
        """
        处理标签页关闭事件
        """
        tab_name = self.ui.ShellTab.tabText(index)
        if tab_name != "首页":
            self.off(index, tab_name)


# 权限确认
class Auth(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dial = auth.Ui_Dialog()
        if platform.system() == 'Darwin':
            # 保持弹窗置顶
            # Mac 不设置，弹层会放主窗口的后面
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.dial.setupUi(self)
        self.setWindowIcon(QIcon("Resources/icon.ico"))
        # 同意
        self.dial.buttonBox.accepted.connect(self.ok_auth)
        self.dial.buttonBox.rejected.connect(self.reject)

    # 确认权限
    def ok_auth(self):
        ssh_conn = self.parent().ssh()

        user_r = "r" if self.dial.checkBoxUserR.isChecked() else "-"
        user_w = "w" if self.dial.checkBoxUserW.isChecked() else "-"
        user_x = "x" if self.dial.checkBoxUserX.isChecked() else "-"
        group_r = "r" if self.dial.checkBoxGroupR.isChecked() else "-"
        group_w = "w" if self.dial.checkBoxGroupW.isChecked() else "-"
        group_x = "x" if self.dial.checkBoxGroupX.isChecked() else "-"
        other_r = "r" if self.dial.checkBoxOtherR.isChecked() else "-"
        other_w = "w" if self.dial.checkBoxOtherW.isChecked() else "-"
        other_x = "x" if self.dial.checkBoxOtherX.isChecked() else "-"

        trimmed_new = user_r + user_w + user_x + group_r + group_w + group_x + other_r + other_w + other_x
        # 转换为八进制
        octal = util.symbolic_to_octal(trimmed_new)

        selected_items = self.parent().ui.treeWidget.selectedItems()
        decompress_commands = []
        trimmed_old = ""
        # 先取出所有选中项目
        for item in selected_items:
            # 名字
            item_text = item.text(0)
            # 权限
            trimmed_old = item.text(3)[1:]
            decompress_commands.append(f"chmod {octal} {ssh_conn.pwd}/{item_text}")

        # 有修改才更新
        if trimmed_new != trimmed_old:
            # 合并命令
            combined_command = " && ".join(decompress_commands)
            ssh_conn.exec(combined_command)
            print("更新了--------------")
        self.close()
        self.parent().refreshDirs()


# 增加配置逻辑
class AddConfigUi(QDialog):

    def __init__(self):
        super().__init__()
        self.dial = add_config.Ui_addConfig()
        self.dial.setupUi(self)
        if platform.system() == 'Darwin':
            # 保持弹窗置顶
            # Mac 不设置，弹层会放主窗口的后面
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.dial.pushButton_3.setEnabled(False)
        self.dial.lineEdit.setEnabled(False)
        self.setWindowIcon(QIcon("Resources/icon.ico"))
        self.dial.pushButton.clicked.connect(self.addDev)
        self.dial.pushButton_3.clicked.connect(self.addKeyFile)

        self.dial.comboBox.currentIndexChanged.connect(self.handleComboBox)

    def addDev(self):
        name, username, password, ip, prot, private_key_file, private_key_type = self.dial.configName.text(), \
            self.dial.usernamEdit.text(), self.dial.passwordEdit.text(), self.dial.ipEdit.text(), \
            self.dial.protEdit.text(), self.dial.lineEdit.text(), self.dial.comboBox.currentText()

        if name == '':
            self.alarm('配置名称不能为空！')
        elif username == '':
            self.alarm('用户名不能为空！')
        elif password == '' and private_key_type == '':
            self.alarm('密码或者密钥必须提供一个！')
        elif private_key_type != '' and private_key_file == '':
            self.alarm('请上传私钥文件！')
        elif ip == '':
            self.alarm('ip地址不能为空！')
        else:
            config = abspath('config.dat')
            with open(config, 'rb') as c:
                conf = pickle.loads(c.read())
                c.close()
            with open(config, 'wb') as c:
                conf[name] = [username, password, f"{ip}:{prot}", private_key_type, private_key_file]
                c.write(pickle.dumps(conf))
                c.close()
            self.close()

    def addKeyFile(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "所有文件 (*);;Python 文件 (*.py);;文本文件 (*.txt)",
        )
        if file_name:
            self.dial.lineEdit.setText(file_name)

    def handleComboBox(self):
        if self.dial.comboBox.currentText():
            self.dial.pushButton_3.setEnabled(True)
            self.dial.lineEdit.setEnabled(True)
        else:
            self.dial.pushButton_3.setEnabled(False)
            self.dial.lineEdit.clear()
            self.dial.lineEdit.setEnabled(False)

    def alarm(self, alart):
        self.dial.alarmbox = QMessageBox()
        self.dial.alarmbox.setWindowIcon(QIcon("Resources/icon.ico"))
        self.dial.alarmbox.setText(alart)
        self.dial.alarmbox.setWindowTitle('错误提示')
        self.dial.alarmbox.show()


# 在线文本编辑
class TextEditor(QMainWindow):
    save_tex = Signal(list)

    def __init__(self, title: str, old_text: str):
        super().__init__()
        self.te = text_editor.Ui_MainWindow()
        self.te.setupUi(self)
        self.setWindowIcon(QIcon("Resources/icon.ico"))
        self.setWindowTitle(title)

        self.old_text = old_text

        # 使用Pygments进行语法高亮
        formatter = HtmlFormatter(style='fruity', noclasses=True)
        # 高亮代码
        highlighted = highlight(old_text, PythonLexer(), formatter)

        self.te.textEdit.setHtml(highlighted)
        self.te.textEdit.setStyleSheet('background-color: rgb(17, 17, 17);')
        self.new_text = self.te.textEdit.toPlainText()

        self.timer1 = None
        self.flushNewText()

        self.te.action.triggered.connect(lambda: self.saq(1))
        self.te.action_2.triggered.connect(lambda: self.daq(1))

    def flushNewText(self):
        self.timer1 = QTimer()
        self.timer1.start(100)
        self.timer1.timeout.connect(self.autosave)

    def autosave(self):
        text = self.te.textEdit.toPlainText()
        self.new_text = text

    def closeEvent(self, a0: QCloseEvent) -> None:
        if self.new_text != self.old_text:
            a0.ignore()
            self.te.chk = Confirm()
            self.te.chk.cfm.save.clicked.connect(lambda: self.saq(0))
            self.te.chk.cfm.drop.clicked.connect(lambda: self.daq(0))
            self.te.chk.show()
        else:
            pass

    def saq(self, sig):
        self.save_tex.emit([self.new_text, sig])

    def daq(self, sig):
        if sig == 0:
            self.new_text = self.old_text
            self.te.chk.close()
            self.close()
        elif sig == 1:
            self.close()


# 文本编辑确认框
class Confirm(QDialog):
    def __init__(self):
        super().__init__()
        self.cfm = confirm.Ui_confirm()
        self.cfm.setupUi(self)
        self.setWindowIcon(QIcon("Resources/icon.ico"))


class Communicate(QObject):
    # 定义一个无参数的信号，用于通知父窗口刷新
    refresh_parent = Signal()


class CustomWidget(QWidget):
    def __init__(self, item, ssh_conn, parent=None):
        super().__init__(parent)

        self.docker = None

        self.layout = QVBoxLayout()

        # 创建图标标签
        icon_label = QLabel(self)
        icon = QIcon(item['icon'])  # 替换为你的图标路径
        pixmap = icon.pixmap(100, 100)  # 获取图标的 QPixmap
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(icon_label)

        # 创建按钮布局
        self.button_layout = QHBoxLayout()

        cmd = "docker ps -a | grep " + item['containerName']
        ack = ssh_conn.exec(cmd=cmd, pty=False)
        if not ack:
            # 安装按钮
            self.install_button = QPushButton("安装", self)
            self.install_button.setCursor(QCursor(Qt.PointingHandCursor))
            self.install_button.clicked.connect(lambda: self.installAction(item, ssh_conn))
            self.button_layout.addWidget(self.install_button)
        else:
            # 安装按钮
            self.install_button = QPushButton("已安装", self)
            self.install_button.setCursor(QCursor(Qt.PointingHandCursor))
            self.install_button.setStyleSheet("background-color: rgb(102, 221, 121);")
            self.install_button.setDisabled(True)
            self.button_layout.addWidget(self.install_button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

        # 设置样式表为小块添加边框
        self.setStyleSheet("""
            QWidget {
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: rgb(50,115,245);
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:pressed {
                background-color: darkgray;
            }
        """)


class CommandDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            painter.setPen(option.palette.highlightedText().color())
        else:
            painter.setPen(option.palette.text().color())

        painter.drawText(option.rect, Qt.AlignLeft | Qt.AlignVCenter, index.data())


def open_data(ssh):
    with open(abspath('config.dat'), 'rb') as c:
        conf = pickle.loads(c.read())[ssh]
    username, password, host, key_type, key_file = '', '', '', '', ''
    if len(conf) == 3:
        return username, password, host, '', ''
    else:
        return conf[0], conf[1], conf[2], conf[3], conf[4]


# 初始化配置文件
def init_config():
    config = abspath('config.dat')
    if not os.path.exists(config):
        with open(config, 'wb') as c:
            start_dic = {}
            c.write(pickle.dumps(start_dic))
            c.close()


if __name__ == '__main__':
    print("PySide6 version:", PySide6.__version__)
    qdarktheme.enable_hi_dpi()
    app = QApplication(sys.argv)
    translator = QTranslator()
    # 加载编译后的 .qm 文件
    translator.load("translations.qm")

    # 安装翻译
    app.installTranslator(translator)

    window = MainDialog(app)

    window.show()
    window.refreshConf()
    sys.exit(app.exec())
