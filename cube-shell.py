import glob
import json
import os
import pickle
import platform
import re
import shutil
import sys
import threading
import time

import PySide6
import qdarkstyle
from PySide6.QtCore import QTimer, Signal, Qt, QPoint, QRect, QEvent, QObject, Slot, QUrl, QCoreApplication, QTranslator
from PySide6.QtGui import QIcon, QAction, QTextCursor, QCursor, QCloseEvent, QKeyEvent, QInputMethodEvent, QPixmap, \
    QDragEnterEvent, QDropEvent, QFont, QContextMenuEvent, QDesktopServices, QGuiApplication
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QDialog, QMessageBox, QTreeWidgetItem, \
    QInputDialog, QFileDialog, QTreeWidget, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from deepdiff import DeepDiff
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
from qdarkstyle import DarkPalette, LightPalette

from core.forwarder import ForwarderManager
from core.frequently_used_commands import TreeSearchApp
from core.mux import mux
from core.vars import ICONS, CONF_FILE, CMDS, KEYS
from function import get_running_data, util, about, theme
from function.ssh_func import SshClient
from function.util import format_file_size, has_valid_suffix
from style.style import updateColor
from ui import add_config, text_editor, confirm, main, docker_install
from ui.add_tunnel_config import Ui_AddTunnelConfig
from ui.tunnel import Ui_Tunnel
from ui.tunnel_config import Ui_TunnelConfig

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


# 主界面逻辑
class MainDialog(QMainWindow):
    def __init__(self, qt_app):
        super().__init__()
        self.app = qt_app  # 将 app 传递并设置为类属性
        self.ui = main.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon("icons/logo.ico"))
        self.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.setAttribute(Qt.WA_KeyCompression, True)
        self.setFocusPolicy(Qt.WheelFocus)

        self.setDarkTheme()  # 默认设置为暗主题

        file_path = 'conf/theme.json'
        # 读取 JSON 文件内容
        util.THEME = util.read_json(file_path)

        self.data = None
        self.tunnels = []
        self.tunnel_refresh()

        # 设置拖放行为
        self.setAcceptDrops(True)

        self.ui.Shell.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.ui.Shell.setAttribute(Qt.WA_KeyCompression, True)

        # 重写 contextMenuEvent 方法
        self.ui.Shell.contextMenuEvent = self.showCustomContextMenu

        # 菜单栏
        self.menuBarController()

        self.ssh_conn = None
        self.timer1, self.timer2 = None, None
        self.getsysinfo = None
        self.dir_tree_now = []
        self.pwd = ''
        self.file_name = ''
        self.fileEvent = ''

        self.buffer = ""
        self.prompt_pos = 0
        self.prompt = ""

        self.ssh_username, self.ssh_password, self.ssh_ip, self.key_type, self.key_file = None, None, None, None, None

        self.ui.discButton.clicked.connect(self.disconnect)
        self.ui.showServiceProcess.clicked.connect(self.getRunData)
        self.ui.setWan.clicked.connect(self.getRunData)
        self.ui.setLan.clicked.connect(self.getRunData)
        self.ui.init.clicked.connect(self.getRunData)
        self.ui.reset.clicked.connect(self.getRunData)
        self.ui.theme.clicked.connect(self.toggleTheme)
        self.ui.timezoneButton.clicked.connect(self.getRunData)
        self.ui.treeWidget.customContextMenuRequested.connect(self.treeRight)
        self.ui.treeWidget.doubleClicked.connect(self.cd)
        # 设置选择模式为多选模式
        self.ui.treeWidget.setSelectionMode(QTreeWidget.ExtendedSelection)
        # 添加事件过滤器
        self.ui.treeWidget.viewport().installEventFilter(self)

        # 用于拖动选择的变量
        self.is_left_selecting = False
        self.start_pos = QPoint()
        self.selection_rect = QRect()

        self.ui.treeWidgetDocker.customContextMenuRequested.connect(self.treeDocker)

        self.isConnected = False
        self.startTimer(50)

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

    # 隧道刷新
    def tunnel_refresh(self):
        self.data = util.read_json(CONF_FILE)
        self.tunnels = []

        # 展示ssh隧道列表
        if self.data:
            i = 0
            for i, name in enumerate(sorted(self.data.keys())):
                tunnel = Tunnel(name, self.data[name], self)
                self.tunnels.append(tunnel)
                self.ui.gridLayout_tunnel_tabs.addWidget(tunnel, i, 0)
            self.kill_button = QPushButton('关闭所有隧道')
            self.kill_button.setIcon(QIcon(ICONS.KILL_SSH))
            self.kill_button.setFocusPolicy(Qt.NoFocus)
            self.kill_button.clicked.connect(self.do_killall_ssh)
            self.ui.gridLayout_kill_all.addWidget(self.kill_button, i + 1, 0)

    def menuBarController(self):
        # 创建菜单栏
        menubar = self.menuBar()

        file_menu = menubar.addMenu("文件")
        # 创建“设置”菜单
        setting_menu = menubar.addMenu("设置")
        # 创建“帮助”菜单
        help_menu = menubar.addMenu("帮助")

        # 创建“新建”动作
        new_action = QAction(QIcon("icons/icons8-ssh-48.png"), "&新增配置", self)
        new_action.setShortcut("Shift+Ctrl+A")
        new_action.setStatusTip("添加配置")
        file_menu.addAction(new_action)
        new_action.triggered.connect(self.showAddConfig)

        new_ssh_tunnel_action = QAction(QIcon(ICONS.TUNNEL), "&新增SSH隧道", self)
        new_ssh_tunnel_action.setShortcut("Shift+Ctrl+S")
        new_ssh_tunnel_action.setStatusTip("新增SSH隧道")
        file_menu.addAction(new_ssh_tunnel_action)
        new_ssh_tunnel_action.triggered.connect(self.showAddSshTunnel)

        # 创建“主题设置”动作
        theme_action = QAction(QIcon("icons/undo.png"), "&主题设置", self)
        theme_action.setShortcut("Shift+Ctrl+T")
        theme_action.setStatusTip("设置主题")
        setting_menu.addAction(theme_action)
        theme_action.triggered.connect(self.theme)
        #
        # # 创建“重做”动作
        # redo_action = QAction(QIcon("icons/redo.png"), "&Redo", self)
        # redo_action.setShortcut("Ctrl+Y")
        # redo_action.setStatusTip("Redo last undone action")
        # setting_menu.addAction(redo_action)

        # 创建“关于”动作
        about_action = QAction(QIcon("icons/about.png"), "&关于", self)
        about_action.setShortcut("Shift+Ctrl+B")
        about_action.setStatusTip("cubeShell 有关信息")
        help_menu.addAction(about_action)
        about_action.triggered.connect(self.about)

        linux_action = QAction(QIcon("icons/about.png"), "&Linux常用命令", self)
        linux_action.setShortcut("Shift+Ctrl+P")
        linux_action.setStatusTip("最常用的Linux命令查找")
        help_menu.addAction(linux_action)
        linux_action.triggered.connect(self.linux)

        help_action = QAction(QIcon("icons/about.png"), "&帮助", self)
        help_action.setShortcut("Shift+Ctrl+P")
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
                    self.start_pos = event.pos()
                    self.left_click_time = event.timestamp()  # 记录左键按下时间
                    return False  # 允许左键单击和双击事件继续处理
            elif event.type() == QEvent.MouseMove:
                if self.is_left_selecting:
                    self.selection_rect.setBottomRight(event.pos())
                    self.selectItemsInRect(self.selection_rect)
                    return True
            elif event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    if event.timestamp() - self.left_click_time < 200:  # 判断是否为单击
                        self.is_left_selecting = False
                        item = self.ui.treeWidget.itemAt(event.pos())
                        if item:
                            self.ui.treeWidget.clearSelection()
                            item.setSelected(True)
                        return False  # 允许左键单击事件继续处理
                    self.is_left_selecting = False
                    return True

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
        menu = QMenu(self.ui.Shell)
        menu.setStyleSheet("""
                QMenu::item {
                    padding-left: 5px;  /* 调整图标和文字之间的间距 */
                }
                QMenu::icon {
                    padding-right: 0px; /* 设置图标右侧的间距 */
                }
            """)

        # 创建复制和粘贴的 QAction 对象
        copy_action = QAction(QIcon("icons/copy.png"), '复制', self)
        paste_action = QAction(QIcon("icons/paste.png"), '粘贴', self)
        clear_action = QAction(QIcon("icons/clear.png"), '清屏', self)

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
        # 获取当前选中的文本，并复制到剪贴板
        selected_text = self.ui.Shell.textCursor().selectedText()
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
    def connect(self):

        focus = self.ui.treeWidget.currentIndex().row()
        if focus != -1:
            name = self.ui.treeWidget.topLevelItem(focus).text(0)
            with open('conf/config.dat', 'rb') as c:
                conf = pickle.loads(c.read())[name]
                c.close()

            username, password, host, key_type, key_file = '', '', '', '', ''

            if len(conf) == 3:
                username, password, host = conf[0], conf[1], conf[2]
            else:
                username, password, host, key_type, key_file = conf[0], conf[1], conf[2], conf[3], conf[4]

            # 检查服务器是否可以连接
            if not util.check_server_accessibility(host.split(':')[0], int(host.split(':')[1])):
                QMessageBox.warning(self, "连接超时", "服务器无法连接，请检查网络或服务器状态。")
                return

            try:
                self.ssh_conn = SshClient(host.split(':')[0], int(host.split(':')[1]), username, password,
                                          key_type, key_file)
                # 创建一个线程来处理 SSH 连接，以避免阻塞主线程。
                threading.Thread(target=self.ssh_conn.connect).start()

                self.ssh_username, self.ssh_password, self.ssh_ip, self.key_type, self.key_file = username, password, \
                    host, key_type, key_file
                self.initSftp()

            except Exception as e:
                self.ui.Shell.setPlaceholderText(str(e))
        else:
            self.alarm('请选择一台设备！')

    # 初始化sftp和控制面板
    def initSftp(self):
        self.isConnected = True
        self.ui.discButton.setEnabled(True)
        self.ui.showServiceProcess.setEnabled(True)
        self.ui.result.setEnabled(True)
        self.ui.lanIP.setEnabled(True)
        self.ui.wanIP.setEnabled(True)
        self.ui.gateway.setEnabled(True)
        self.ui.setWan.setEnabled(True)
        self.ui.setLan.setEnabled(True)
        self.ui.initKey.setEnabled(True)
        self.ui.init.setEnabled(True)
        self.ui.theme.setEnabled(True)
        self.ui.reset.setEnabled(True)
        self.ui.iport.setEnabled(True)
        self.ui.Shell.setEnabled(True)
        self.ui.timezoneButton.setEnabled(True)
        self.getsysinfo = get_running_data.DevicInfo(username=self.ssh_username, password=self.ssh_password,
                                                     host=self.ssh_ip, key_type=self.key_type,
                                                     key_file=self.key_file)

        threading.Thread(target=self.getsysinfo.get_datas, daemon=True).start()
        time.sleep(0.02)
        self.flushSysInfo()
        self.refreshDokerInfo()
        self.flushDokerInfo()
        self.refreshDirs()

        # 读取json文件
        items = util.read_json_file("conf/docker.json")
        # 每行最多四个小块
        max_columns = 4
        # 遍历列表，创建小块并添加到网格布局中
        for index, item in enumerate(items):
            row = index // max_columns
            col = index % max_columns

            # 创建外部容器
            container_widget = QWidget()
            container_layout = QVBoxLayout()
            container_widget.setLayout(container_layout)
            container_layout.setContentsMargins(0, 0, 0, 0)  # 去掉布局的内边距
            container_widget.setStyleSheet("background-color: rgb(187, 232, 221);")

            # 创建自定义小块并添加到外部容器
            widget = CustomWidget(item, self.ssh_conn)
            container_layout.addWidget(widget)

            self.ui.gridLayout_7.addWidget(container_widget, row, col)

    # 后台获取信息，不打印至程序界面
    def getData2(self, cmd='', pty=False):
        try:
            ack = self.ssh_conn.exec(cmd=cmd, pty=pty)
            return ack
        except Exception as e:
            self.ui.result.append(e)
            return 'error'

    # 选择文件夹
    def cd(self):
        if self.isConnected:
            focus = self.ui.treeWidget.currentIndex().row()
            if focus != -1 and self.dir_tree_now[focus][0].startswith('d'):
                self.pwd = self.getData2('cd ' + self.pwd + '/' + self.ui.treeWidget.topLevelItem(focus).text(0) +
                                         ' && sudo pwd')[:-1]
                self.refreshDirs()
            else:
                self.alarm('文件无法前往，右键编辑文件！')
        elif not self.isConnected:
            self.connect()

    # 断开服务器
    def disconnect(self):
        self.timer1.stop()
        self.timer2.stop()

        self.ssh_conn.term_data = b''
        self.ssh_conn.disconnect()
        self.ssh_conn.close()
        self.isConnected = False
        self.ssh_username, self.ssh_password, self.ssh_ip, self.key_type, self.key_file = None, None, None, None, None
        self.ui.discButton.setDisabled(True)
        self.ui.showServiceProcess.setDisabled(True)
        self.ui.result.setDisabled(True)
        self.ui.Shell.setDisabled(True)
        self.ui.Shell.setText('')

        self.ui.treeWidget.setColumnCount(1)
        self.ui.treeWidget.setHeaderLabels(["设备列表"])
        self.ui.remove_last_line_edit()
        self.pwd = ''

        self.ui.iport.setDisabled(True)
        self.ui.lanIP.setDisabled(True)
        self.ui.wanIP.setDisabled(True)
        self.ui.gateway.setDisabled(True)
        self.ui.setWan.setDisabled(True)
        self.ui.setLan.setDisabled(True)
        self.ui.initKey.setDisabled(True)
        self.ui.init.setDisabled(True)
        self.ui.reset.setDisabled(True)
        self.ui.timezoneButton.setDisabled(True)

        self.ui.treeWidgetDocker.clear()
        self.ui.result.clear()

        util.clear_grid_layout(self.ui.gridLayout_7)

        self.ui.cpuRate.setValue(0)
        self.ui.diskRate.setValue(0)
        self.ui.memRate.setValue(0)

        self.getsysinfo.disconnect()
        self.refreshConf()

    def timerEvent(self, event):
        try:
            if not self.ssh_conn.screen.dirty:
                if self.ssh_conn.buffer_write:
                    self.updateTerminal()
                    self.ssh_conn.buffer_write = b''
                return

            self.updateTerminal()
            self.update()
        except:
            pass
            # traceback.print_exc()

    # 更新终端输出
    def updateTerminal(self):
        font_ = util.THEME['font']
        theme_ = util.THEME['theme']
        color_ = util.THEME['theme_color']

        font = QFont(font_, 14)
        self.ui.Shell.setFont(font)

        self.ui.Shell.moveCursor(QTextCursor.End)
        screen = self.ssh_conn.screen
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

        self.ui.Shell.clear()
        # 使用Pygments进行语法高亮
        formatter = HtmlFormatter(style=theme_, noclasses=True, bg_color='#ffffff')
        self.ui.Shell.setStyleSheet("background-color: " + color_ + ";")
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
        self.ui.Shell.setHtml(highlighted2)

        self.ui.Shell.moveCursor(QTextCursor.End)

        # 如果没有这串代码，执行器就会疯狂执行代码
        self.ssh_conn.screen.dirty.clear()

    def keyPressEvent(self, event: QKeyEvent):
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
                self.send(text.encode("utf-8"))
            else:
                s = keymap.get(key)
                if s:
                    self.send(s)
        event.accept()

    def keyReleaseEvent(self, event: QKeyEvent):
        text = str(event.text())
        key = event.key()

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
            self.ssh_conn.buffer_write = b'\x1b[D'
            self.send(b'\x1b[D')
            # self.ssh_conn.screen.cursor.x = self.ssh_conn.screen.cursor.x - 1
        elif key == Qt.Key_Right:
            self.ssh_conn.buffer_write = b'\x1b[C'
            self.send(b'\x1b[C')
            # self.ssh_conn.screen.cursor.x = self.ssh_conn.screen.cursor.x + 1

    def send(self, data):
        self.ssh_conn.write(data)

    def do_killall_ssh(self):
        for tunnel in self.tunnels:
            tunnel.stop_tunnel()
        if os.name == 'nt':
            os.system(CMDS.SSH_KILL_WIN)
        else:
            os.system(CMDS.SSH_KILL_NIX)

    def closeEvent(self, event):
        """
         窗口关闭事件 当存在通道的时候关闭通道
         不存在时结束多路复用器的监听
        :param event: 关闭事件
        :return: None
        """
        if self.ssh_conn:
            self.ssh_conn.close()
        else:
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
        for tunnel in self.tunnels:
            name = tunnel.ui.name.text()
            data[name] = tunnel.tunnelconfig.as_dict()

        # DeepDiff 库用于比较两个复杂数据结构（如字典、列表、集合等）之间的差异，
        # 能够识别并报告添加、删除或修改的数据项。
        # 它支持多级嵌套结构的深度比较，适用于调试或数据同步场景。
        changed = DeepDiff(self.data, data, ignore_order=True)
        if changed:
            timestamp = int(time.time())
            shutil.copy(CONF_FILE, F"{CONF_FILE}-{timestamp}")
            with open(CONF_FILE, "w") as fp:
                json.dump(data, fp)
            backup_configs = glob.glob(F"{CONF_FILE}-*")
            if len(backup_configs) > 10:
                for config in sorted(backup_configs, reverse=True)[10:]:
                    os.remove(config)
        event.accept()

    def inputMethodEvent(self, a0: QInputMethodEvent) -> None:
        cmd = a0.commitString()
        if cmd != '':
            self.send(cmd.encode('utf8'))

    # 服务器运行命令并获取输出
    def getRunData(self, cmd=''):
        sender = self.sender()
        cmd = cmd
        if sender.objectName() == 'showServiceProcess':
            cmd = 'sudo ps -aux'
        elif sender.objectName() == 'init':
            cmd = self.ui.initKey.toPlainText()
        elif sender.objectName() == 'setWan':
            ip, gateway = self.ui.wanIP.text(), self.ui.gateway.text()
            cmd = 'sudo nmcli connection modify eth0 ipv4.addresses ' + ip + ' ipv4.gateway ' + gateway + \
                  ' && nmcli connection show eth0'
        elif sender.objectName() == 'setLan':
            ip = self.ui.lanIP.text()
            cmd = 'sudo nmcli connection modify eth0 +ipv4.addresses ' + ip + \
                  ' && nmcli connection show eth0'
        elif sender.objectName() == 'reset':
            # ip = self.ui.iport.text()
            # cmd = 'sudo nmap -PN ' + ip
            self.ui.initKey.clear()
            cmd = 'sudo clear'
        elif sender.objectName() == 'timezoneButton':
            cmd = 'sudo timedatectl set-timezone "Asia/Shanghai" && sudo hwclock'
        else:
            pass
        self.ui.progressBar.setValue(20)
        self.ui.result.append(cmd)
        if self.isConnected is True:
            try:
                self.ui.progressBar.setValue(50)
                ack = self.ssh_conn.exec(cmd=cmd, pty=False)

                formatter = HtmlFormatter(style='rrt', noclasses=True)
                # 高亮代码
                highlighted = highlight(ack, PythonLexer(), formatter)

                self.ui.result.setHtml(highlighted)
                self.ui.result.setStyleSheet('background-color: rgb(17, 17, 17);')

                # self.ui.result.append(highlighted)
                # self.ui.result.append(highlighted)
                self.ui.progressBar.setValue(80)
                time.sleep(0.1)
                # ssh.close()
                self.ui.progressBar.setValue(100)
                return ack
            except Exception as e:
                self.ui.result.append(str(e))
                self.ui.progressBar.setValue(100)
        else:
            self.ui.result.append('请先连接设备!')
            self.ui.progressBar.setValue(100)

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
            self.ui.action = QAction(QIcon('icons/addConfig.png'), '添加配置', self)
            self.ui.action2 = QAction(QIcon('icons/delConf.png'), '删除配置', self)
            # 把动作选项对象添加到菜单self.groupBox_menu上
            self.ui.tree_menu.addAction(self.ui.action)
            self.ui.tree_menu.addAction(self.ui.action2)
            # 将动作A触发时连接到槽函数 button
            self.ui.action.triggered.connect(self.showAddConfig)
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

            self.ui.action1 = QAction(QIcon('icons/Download.png'), '下载文件', self)
            self.ui.action2 = QAction(QIcon('icons/Upload.png'), '上传文件', self)
            self.ui.action3 = QAction(QIcon('icons/Edit.png'), '编辑文本', self)
            self.ui.action4 = QAction(QIcon('icons/createdirector.png'), '创建文件夹', self)
            self.ui.action5 = QAction(QIcon('icons/createfile.png'), '创建文件', self)
            self.ui.action6 = QAction(QIcon('icons/refresh.png'), '刷新', self)

            self.ui.action7 = QAction(QIcon('icons/remove.png'), '删除', self)
            self.ui.tree_menu.addAction(self.ui.action1)
            self.ui.tree_menu.addAction(self.ui.action2)
            self.ui.tree_menu.addAction(self.ui.action3)
            self.ui.tree_menu.addAction(self.ui.action4)
            self.ui.tree_menu.addAction(self.ui.action5)
            self.ui.tree_menu.addAction(self.ui.action6)

            # 添加分割线,做标记区分
            bottom_separator = QAction(self)
            bottom_separator.setSeparator(True)
            self.ui.tree_menu.addAction(bottom_separator)

            self.ui.tree_menu.addAction(self.ui.action7)
            self.ui.action1.triggered.connect(self.downloadFile)
            self.ui.action2.triggered.connect(self.uploadFile)
            self.ui.action3.triggered.connect(self.editFile)
            self.ui.action4.triggered.connect(self.createDir)
            self.ui.action5.triggered.connect(self.createFile)
            self.ui.action6.triggered.connect(self.refresh)
            self.ui.action7.triggered.connect(self.remove)
            # 声明当鼠标在groupBox控件上右击时，在鼠标位置显示右键菜单   ,exec_,popup两个都可以，
            self.ui.tree_menu.popup(QCursor.pos())

    # 创建docker列表树右键菜单函数
    def treeDocker(self):
        if self.isConnected:
            self.ui.tree_menu = QMenu(self)
            self.ui.tree_menu.setStyleSheet("""
                QMenu::item {
                    padding-left: 5px;  /* 调整图标和文字之间的间距 */
                }
                QMenu::icon {
                    padding-right: 0px; /* 设置图标右侧的间距 */
                }
            """)
            self.ui.action1 = QAction(QIcon('icons/stop.png'), '停止', self)
            self.ui.action2 = QAction(QIcon('icons/restart.png'), '重启', self)
            self.ui.action3 = QAction(QIcon('icons/remove.png'), '删除', self)
            # self.ui.action4 = QAction('日志', self)

            self.ui.tree_menu.addAction(self.ui.action1)
            self.ui.tree_menu.addAction(self.ui.action2)
            self.ui.tree_menu.addAction(self.ui.action3)
            # self.ui.tree_menu.addAction(self.ui.action4)

            self.ui.action1.triggered.connect(self.stopDockerContainer)
            self.ui.action2.triggered.connect(self.restartDockerContainer)
            self.ui.action3.triggered.connect(self.rmDockerContainer)
            # self.ui.action4.triggered.connect(self.rmDockerContainer)

            # 声明当鼠标在groupBox控件上右击时，在鼠标位置显示右键菜单,exec_,popup两个都可以，
            self.ui.tree_menu.popup(QCursor.pos())

    # 打开增加配置界面
    def showAddConfig(self):
        self.ui.addconfwin = AddConfigUi()
        self.ui.addconfwin.show()
        self.ui.addconfwin.dial.pushButton.clicked.connect(self.refreshConf)
        self.ui.addconfwin.dial.pushButton_2.clicked.connect(self.ui.addconfwin.close)

    # 打开增加隧道界面
    def showAddSshTunnel(self):
        self.add = AddTunnelConfig(self)
        self.add.setModal(True)
        self.add.show()

    # 刷新设备列表
    def refreshConf(self):
        if not os.path.exists('conf/config.dat'):
            with open('conf/config.dat', 'wb') as c:
                start_dic = {}
                c.write(pickle.dumps(start_dic))
                c.close()
        with open('conf/config.dat', 'rb') as c:
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
            self.ui.treeWidget.topLevelItem(i).setIcon(0, QIcon('icons/icons8-ssh-48.png'))
            i += 1

    # 当前目录列表刷新
    def refreshDirs(self):
        self.pwd, files = self.getDirNow()
        self.dir_tree_now = files[1:]
        self.ui.treeWidget.setHeaderLabels(["文件名", "文件大小", "修改日期", "权限", "所有者/组"])
        self.ui.add_line_edit('当前目录：' + self.pwd)  # 添加一个初始的 QLineEdit
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
        pwd = self.getData2('cd ' + self.pwd + ' && sudo pwd')
        dir_info = self.getData2(cmd='cd ' + self.pwd + ' && sudo ls -al').split('\n')
        dir_n_info = []
        for d in dir_info:
            d_list = get_running_data.DevicInfo.del_more_space(d)
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
            text = self.getData2('sudo cat ' + self.pwd + '/' + self.file_name)
            if text != 'error' and text != '\n':
                self.ui.addTextEditWin = TextEditor(title=self.file_name, old_text=text)
                self.ui.addTextEditWin.show()
                self.ui.addTextEditWin.save_tex.connect(self.getNewText)
            elif text == 'error' or text == '\n':
                self.alarm('无法编辑文件，请确认！')
        else:
            self.alarm('文件夹不能被编辑！')

    def createDir(self):
        dialog = QInputDialog(self)
        dialog.setWindowTitle('创建文件夹')
        dialog.setLabelText('文件夹名字:')
        dialog.setFixedSize(400, 150)

        # 显示对话框并获取结果
        ok = dialog.exec()
        text = dialog.textValue()

        if ok:
            sftp = self.ssh_conn.open_sftp()
            pwd_text = self.pwd + '/' + text

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
        dialog = QInputDialog(self)
        dialog.setWindowTitle('创建文件')
        dialog.setLabelText('文件名字:')
        dialog.setFixedSize(400, 150)

        # 显示对话框并获取结果
        ok = dialog.exec()
        text = dialog.textValue()

        if ok:
            sftp = self.ssh_conn.open_sftp()
            pwd_text = self.pwd + '/' + text
            try:
                with sftp.file(pwd_text, 'w'):
                    pass  # 不写入任何内容
                self.refreshDirs()
            except IOError as e:
                print(f"创建文件出现异常: {e}")
                self.alarm('创建文件失败，请联系开发作者')

    # 获取返回信息，并保存文件
    def getNewText(self, new_list):
        nt, sig = new_list[0], new_list[1]
        # 将双引号转义为转义字符
        escaped_string = nt.replace("\"", '\\"')
        if sig == 0:
            self.getData2('sudo echo -e "' + escaped_string + '" > ' + self.pwd + '/' + self.file_name)
            self.ui.addTextEditWin.new_text = self.ui.addTextEditWin.old_text
            self.ui.addTextEditWin.te.chk.close()
            self.ui.addTextEditWin.close()
        elif sig == 1:
            self.getData2('sudo echo -e "' + escaped_string + '" > ' + self.pwd + '/' + self.file_name)
            self.ui.addTextEditWin.old_text = nt

    # 删除设备配置文件
    def delConf(self):
        focus = self.ui.treeWidget.currentIndex().row()
        if focus != -1:
            name = self.ui.treeWidget.topLevelItem(focus).text(0)
            with open('conf/config.dat', 'rb') as c:
                conf = pickle.loads(c.read())
                c.close()
            with open('conf/config.dat', 'wb') as c:
                del conf[name]
                c.write(pickle.dumps(conf))
                c.close()
            self.refreshConf()
        else:
            self.alarm('请选中要删除的配置')

    # 定时刷新设备状态信息
    def flushSysInfo(self):
        self.timer1 = QTimer()
        self.timer1.start(1000)
        self.timer1.timeout.connect(self.refreshSysInfo)

    # 刷新设备状态信息功能
    def refreshSysInfo(self):
        if self.isConnected:
            cpu_use = self.getsysinfo.cpu_use
            mem_use = self.getsysinfo.mem_use
            dissk_use = self.getsysinfo.disk_use
            self.ui.cpuRate.setValue(cpu_use)
            self.ui.cpuRate.setStyleSheet(updateColor(cpu_use))
            self.ui.memRate.setValue(mem_use)
            self.ui.memRate.setStyleSheet(updateColor(mem_use))
            self.ui.diskRate.setValue(dissk_use)
            self.ui.diskRate.setStyleSheet(updateColor(dissk_use))
        else:
            self.ui.cpuRate.setValue(0)
            self.ui.memRate.setValue(0)
            self.ui.diskRate.setValue(0)

    def flushDokerInfo(self):
        self.timer2 = QTimer()
        self.timer2.start(5000)
        self.timer2.timeout.connect(self.refreshDokerInfo)

    def refreshDokerInfo(self):
        if self.isConnected:
            info = self.getsysinfo.docker_info
            self.ui.treeWidgetDocker.clear()
            self.ui.treeWidgetDocker.headerItem().setText(0, 'docker容器管理：')
            if len(info) != 0:
                i = 0
                for n in info:
                    self.ui.treeWidgetDocker.addTopLevelItem(QTreeWidgetItem(0))
                    self.ui.treeWidgetDocker.topLevelItem(i).setText(0, n)
                    if i != 0:
                        self.ui.treeWidgetDocker.topLevelItem(i).setIcon(0, QIcon("icons/icons8-docker-48.png"))
                    # 设置字体为加粗
                    if i == 0:
                        bold_font = QFont()
                        bold_font.setBold(True)  # 设置字体为加粗
                        self.ui.treeWidgetDocker.topLevelItem(i).setFont(0, bold_font)

                    i += 1

                # 设置列宽为自适应内容
                for i in range(self.ui.treeWidgetDocker.columnCount()):
                    self.ui.treeWidgetDocker.resizeColumnToContents(i)
            else:
                self.ui.treeWidgetDocker.addTopLevelItem(QTreeWidgetItem(0))
                self.ui.treeWidgetDocker.topLevelItem(0).setText(0, '没有可用的docker容器')
        else:
            self.ui.treeWidgetDocker.clear()
            self.ui.treeWidgetDocker.addTopLevelItem(QTreeWidgetItem(0))
            self.ui.treeWidgetDocker.topLevelItem(0).setText(0, '没有可用的docker容器')

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
                items = self.ui.treeWidget.selectedItems()
                sftp = self.ssh_conn.open_sftp()
                for item in items:
                    item_text = item.text(0)
                    sftp.get(self.pwd + '/' + item_text, f'{directory}/{item_text}')

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
                    sftp = self.ssh_conn.open_sftp()
                    try:
                        sftp.put(file_path, self.pwd + '/' + os.path.basename(file_path))
                    except IOError as e:
                        print(f"Failed to upload file: {e}")
            self.refreshDirs()

    # 刷新
    def refresh(self):
        self.refreshDirs()

    # 删除
    def remove(self):
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
            sftp = self.ssh_conn.open_sftp()
            # 批量删除
            for key, value in rm_dict.items():
                try:
                    if value:
                        util.deleteFolder(sftp, self.pwd + '/' + key)
                    else:
                        sftp.remove(self.pwd + '/' + key)
                    self.refreshDirs()
                except IOError as e:
                    print(f"Failed to remove file: {e}")
            rm_dict.clear()
            self.success("删除")

    # 停止docker容器
    def stopDockerContainer(self):
        focus = self.ui.treeWidgetDocker.currentIndex().row()
        if focus != -1:
            text = self.ui.treeWidgetDocker.topLevelItem(focus).text(0)
            # 取出前12位字符串
            container_id = text[:12]
            data_ = self.getData2('sudo docker stop ' + container_id)
            print('stop----', data_)
            time.sleep(1)  # 延迟一秒
            self.refreshDokerInfo()

    # 重启docker容器
    def restartDockerContainer(self):
        focus = self.ui.treeWidgetDocker.currentIndex().row()
        if focus != -1:
            text = self.ui.treeWidgetDocker.topLevelItem(focus).text(0)
            # 取出前12位字符串
            container_id = text[:12]
            data_ = self.getData2('sudo docker restart ' + container_id)
            print('restart----', data_)
            time.sleep(1)  # 延迟一秒
            self.refreshDokerInfo()

    # 删除docker容器
    def rmDockerContainer(self):
        focus = self.ui.treeWidgetDocker.currentIndex().row()
        if focus != -1:
            text = self.ui.treeWidgetDocker.topLevelItem(focus).text(0)
            # 取出前12位字符串
            container_id = text[:12]
            data_ = self.getData2('sudo docker rm ' + container_id)
            print('rm----', data_)
            time.sleep(1)  # 延迟一秒
            self.refreshDokerInfo()

    # 删除文件夹
    def removeDir(self):
        focus = self.ui.treeWidget.currentIndex().row()
        if focus != -1:
            text = self.ui.treeWidget.topLevelItem(focus).text(0)
            sftp = self.ssh_conn.open_sftp()
            try:
                sftp.rmdir(self.pwd + '/' + text)
                self.refreshDirs()
            except IOError as e:
                print(f"Failed to remove directory: {e}")
        pass

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    # 拖拉拽上传文件
    def dropEvent(self, event: QDropEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            for url in mime_data.urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    self.fileEvent = file_path
                    sftp = self.ssh_conn.open_sftp()
                    try:
                        sftp.put(file_path, self.pwd + '/' + os.path.basename(file_path))
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
        custom_icon = QIcon('icons/icons8-fail-48.png')
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
        custom_icon = QIcon('icons/icons8-success-48.png')  # 替换为你的图标路径
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
        self.app.setStyleSheet(qdarkstyle.load_stylesheet(palette=DarkPalette))

    def setLightTheme(self):
        self.app.setStyleSheet(qdarkstyle.load_stylesheet(palette=LightPalette))

    def toggleTheme(self):
        if self.app.styleSheet() == qdarkstyle.load_stylesheet(palette=DarkPalette):
            self.setLightTheme()
        else:
            self.setDarkTheme()


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
            with open('conf/config.dat', 'rb') as c:
                conf = pickle.loads(c.read())
                c.close()
            with open('conf/config.dat', 'wb') as c:
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
        pixmap = QPixmap(item['icon'])
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

    def installAction(self, item, ssh_conn):
        """
        点击安装按钮，安装docker容器
        :param item: 数据对象
        :param ssh_conn: ssh 连接对象
        :return:
        """

        self.docker = InstallDocker(item, ssh_conn)
        self.docker.dial.lineEdit_containerName.setText(item['containerName'])
        self.docker.dial.lineEdit_Image.setText(item['image'])

        volumes = ""
        environment_variables = ""
        labels = ""
        ports = ""
        for port in item['ports']:
            ports += "-p " + port['source'] + ":" + port['destination'] + " "
        self.docker.dial.lineEdit_ports.setText(ports)

        for bind in item['volumes']:
            volumes += "-v " + bind.get('destination') + ":" + bind.get('source') + " "
        self.docker.dial.lineEdit_volumes.setText(volumes)

        for env in item['environmentVariables']:
            environment_variables += "-e " + env.get('name') + "=" + env.get('value') + " "
        self.docker.dial.lineEdit_environmentVariables.setText(environment_variables)

        for label in item['labels']:
            labels += "--" + label.get('name') + "=" + label.get('value') + " "
        self.docker.dial.lineEdit_labels.setText(labels)

        if item['containerName']:
            self.docker.dial.checkBox_privileged.setChecked(True)

        self.docker.communicate.refresh_parent.connect(lambda: self.refresh(item, ssh_conn))
        self.docker.show()

    def refresh(self, item, ssh_conn):
        # 安装按钮
        self.install_button.setText("已安装")
        self.install_button.setStyleSheet("background-color: rgb(102, 221, 121);")
        self.install_button.setDisabled(True)


# docker容器安装
class InstallDocker(QDialog):
    def __init__(self, item, ssh_conn):
        super().__init__()
        self.dial = docker_install.Ui_Dialog()
        self.dial.setupUi(self)
        self.setWindowIcon(QIcon("icons/icons8-docker-48.png"))
        # 取消
        self.dial.buttonBoxDockerInstall.rejected.connect(self.reject)
        # 安装
        self.dial.buttonBoxDockerInstall.accepted.connect(lambda: self.installDocker(item, ssh_conn))

        # 创建一个 Communicate 实例
        self.communicate = Communicate()
        # 在对话框关闭时发射信号
        self.finished.connect(self.onFinished)

    @Slot(int)
    def onFinished(self, result):
        # 当对话框关闭时发射信号
        self.communicate.refresh_parent.emit()

    def installDocker(self, item, ssh_conn):
        try:
            container_name = self.dial.lineEdit_containerName.text()
            image = self.dial.lineEdit_Image.text()
            volumes = self.dial.lineEdit_volumes.text()
            environment = self.dial.lineEdit_environmentVariables.text()
            labels = self.dial.lineEdit_labels.text()
            ports = self.dial.lineEdit_ports.text()
            cmd_ = item['cmd']

            formatter = HtmlFormatter(style='rrt', noclasses=True)

            privileged = ""
            if self.dial.checkBox_privileged.isChecked():
                privileged = "--privileged=true"

            cmd1 = "docker pull " + image
            ack = ssh_conn.exec(cmd=cmd1, pty=False)
            highlighted = highlight(ack, PythonLexer(), formatter)
            self.dial.textBrowserDockerInout.append(highlighted)
            if ack:
                #  创建宿主机挂载目录
                cmd_volumes = ""
                for bind in item['volumes']:
                    cmd_volumes += f"mkdir -p " + bind.get('destination') + " "
                ssh_conn.exec(cmd=cmd_volumes, pty=False)

                # 创建临时容器
                image_str = f"{image}".split(":", 1)
                ports_12_chars = f"{ports}"[:12]
                cmd2 = f"docker run {ports_12_chars} --name {container_name} -d {image_str[0]}"
                ack = ssh_conn.exec(cmd=cmd2, pty=False)
                # 睡眠一秒
                time.sleep(1)
                highlighted = highlight(ack, PythonLexer(), formatter)
                self.dial.textBrowserDockerInout.append(highlighted)
                if ack:
                    for bind in item['volumes']:
                        source = bind.get('source')
                        cp = bind.get('cp')
                        cmd3 = f"docker cp {container_name}:{source}/ {cp}" + " "
                        ack = ssh_conn.exec(cmd=cmd3, pty=False)
                        highlighted = highlight(ack, PythonLexer(), formatter)
                        self.dial.textBrowserDockerInout.append(highlighted)

                    cmd_stop = f"docker stop {container_name}"
                    ack = ssh_conn.exec(cmd=cmd_stop, pty=False)
                    # 删除临时容器
                    if ack:
                        cmd4 = f"docker rm {container_name}"
                        ack = ssh_conn.exec(cmd=cmd4, pty=False)
                        self.dial.textBrowserDockerInout.append(ack)

            cmd = f"docker run -d --name {container_name} {environment} {ports} {volumes} {labels} {privileged} {image} {cmd_}"
            ack = ssh_conn.exec(cmd=cmd, pty=False)
            highlighted = highlight(ack, PythonLexer(), formatter)
            self.dial.textBrowserDockerInout.append(highlighted)

        except Exception as e:
            print(f"安装失败：{e}")
            return 'error'
        print("安装成功")


class TunnelConfig(QDialog):
    """
    初始化配置对话框并设置UI元素值；
    监听UI变化以更新SSH命令；
    提供复制SSH命令和
    """

    def __init__(self, parent, data):
        super(TunnelConfig, self).__init__(parent)

        self.ui = Ui_TunnelConfig()
        self.ui.setupUi(self)

        tunnel_type = data.get(KEYS.TUNNEL_TYPE)
        self.ui.comboBox_tunnel_type.setCurrentText(tunnel_type)
        self.ui.comboBox_ssh.setCurrentText(data.get(KEYS.DEVICE_NAME))
        self.ui.remote_bind_address_edit.setText(data.get(KEYS.REMOTE_BIND_ADDRESS))
        if tunnel_type == "动态":
            self.ui.remote_bind_address_edit.hide()
            self.ui.label_remote_bind_address_edit.hide()
        else:
            self.ui.remote_bind_address_edit.show()
            self.ui.label_remote_bind_address_edit.show()
        self.ui.local_bind_address_edit.setText(data.get(KEYS.LOCAL_BIND_ADDRESS))
        self.ui.browser_open.setText(data.get(KEYS.BROWSER_OPEN))
        self.ui.copy.clicked.connect(self.do_copy_ssh_command)
        self.ui.comboBox_tunnel_type.currentIndexChanged.connect(self.readonly_remote_bind_address_edit)

    def readonly_remote_bind_address_edit(self):
        tunnel_type = self.ui.comboBox_tunnel_type.currentText()
        if tunnel_type == "动态":
            self.ui.remote_bind_address_edit.hide()
            self.ui.label_remote_bind_address_edit.hide()
        else:
            self.ui.remote_bind_address_edit.show()
            self.ui.label_remote_bind_address_edit.show()

    def render_ssh_command(self):
        text = self.ui.local_bind_address_edit.text()
        ssh = self.ui.comboBox_ssh.currentText()
        username, password, host, key_type, key_file = open_data(ssh)
        if not util.check_server_accessibility(host.split(':')[0], int(host.split(':')[1])):
            QMessageBox.warning(self, "连接超时", "服务器无法连接，请检查网络或服务器状态。")
            return

        ssh_command = (f"ssh -L {int(text.split(':')[1])}:{self.ui.remote_bind_address_edit.text()} "
                       f"{username}@{host.split(':')[0]}")
        self.ui.ssh_command.setText(ssh_command)

    def do_copy_ssh_command(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.ui.ssh_command.text())

    def as_dict(self):
        return {
            KEYS.TUNNEL_TYPE: self.ui.comboBox_tunnel_type.currentText(),
            KEYS.BROWSER_OPEN: self.ui.browser_open.text(),
            KEYS.DEVICE_NAME: self.ui.comboBox_ssh.currentText(),
            KEYS.REMOTE_BIND_ADDRESS: self.ui.remote_bind_address_edit.text(),
            KEYS.LOCAL_BIND_ADDRESS: self.ui.local_bind_address_edit.text(),
        }


class AddTunnelConfig(QDialog):
    """
    初始化配置对话框并设置UI元素值；
    监听UI变化以更新SSH命令；
    提供复制SSH命令和
    """

    def __init__(self, parent=None):
        super(AddTunnelConfig, self).__init__(parent)

        self.tunnel = Ui_AddTunnelConfig()
        self.tunnel.setupUi(self)
        self.tunnel.add_tunnel.accepted.connect(self.addTunnel)
        self.tunnel.add_tunnel.rejected.connect(TunnelConfig.reject)
        self.tunnel.comboBox_tunnel_type.currentIndexChanged.connect(self.readonly_remote_bind_address_edit)

    def addTunnel(self):

        remote = self.tunnel.remote_bind_address_edit.text()
        tunnel_type = self.tunnel.comboBox_tunnel_type.currentText()
        if remote == '' and tunnel_type != '动态':
            QMessageBox.critical(self, "警告", "请填写远程绑定地址")
            return
        split = remote.split(':')
        if len(split) != 2 and tunnel_type != '动态':
            QMessageBox.critical(self, "警告", "远程绑定地址格式不正确，请检查")
            return

        local = self.tunnel.local_bind_address_edit.text()
        if local == '':
            QMessageBox.critical(self, "警告", "请填写本地绑定地址")
            return
        local_split = local.split(':')
        if len(local_split) != 2:
            QMessageBox.critical(self, "警告", "本地绑定地址格式不正确，请检查")
            return
        if self.tunnel.ssh_tunnel_name.text() == '':
            QMessageBox.critical(self, "警告", "请填写隧道名称")
            return

        dic = {
            KEYS.TUNNEL_TYPE: self.tunnel.comboBox_tunnel_type.currentText(),
            KEYS.BROWSER_OPEN: self.tunnel.browser_open.text(),
            KEYS.DEVICE_NAME: self.tunnel.comboBox_ssh.currentText(),
            KEYS.REMOTE_BIND_ADDRESS: self.tunnel.remote_bind_address_edit.text(),
            KEYS.LOCAL_BIND_ADDRESS: self.tunnel.local_bind_address_edit.text(),
        }

        file_path = 'conf/tunnel.json'
        # 读取 JSON 文件内容
        data = util.read_json(file_path)
        data[self.tunnel.ssh_tunnel_name.text()] = dic

        # 将修改后的数据写回 JSON 文件
        util.write_json(file_path, data)
        self.close()

        util.clear_grid_layout(self.parent().ui.gridLayout_ssh)
        self.parent().tunnel_refresh()

    def readonly_remote_bind_address_edit(self):
        tunnel_type = self.tunnel.comboBox_tunnel_type.currentText()
        if tunnel_type == "动态":
            self.tunnel.remote_bind_address_edit.hide()
            self.tunnel.label_remote_bind_address_edit.hide()
        else:
            self.tunnel.remote_bind_address_edit.show()
            self.tunnel.label_remote_bind_address_edit.show()


class Tunnel(QWidget):
    """
    创建单个隧道实例，包括启动、停止隧道以及打开浏览器的功能。
    """

    def __init__(self, name, data, parent=None):
        super(Tunnel, self).__init__(parent)

        self.ui = Ui_Tunnel()
        self.ui.setupUi(self)
        self.manager = ForwarderManager()

        self.tunnelconfig = TunnelConfig(self, data)
        self.tunnelconfig.setWindowTitle(name)
        self.tunnelconfig.setModal(True)
        self.ui.name.setText(name)

        self.tunnelconfig.icon = F"./icons/{name}.png"

        if not os.path.exists(self.tunnelconfig.icon):
            self.tunnelconfig.icon = ICONS.TUNNEL

        self.ui.icon.setPixmap(QPixmap(self.tunnelconfig.icon))
        self.ui.action_tunnel.clicked.connect(self.do_tunnel)
        self.ui.action_settings.clicked.connect(self.show_tunnel_config)
        self.ui.action_open.clicked.connect(self.do_open_browser)
        self.ui.delete_ssh.clicked.connect(lambda: self.delete_tunnel(parent))

        self.process = False

    # 打开修改页面
    def show_tunnel_config(self):
        self.tunnelconfig.render_ssh_command()
        self.tunnelconfig.show()

    def do_open_browser(self):
        browser_open = self.tunnelconfig.ui.browser_open.text()
        if browser_open:
            QDesktopServices.openUrl(QUrl(browser_open))

    def do_tunnel(self):
        if self.process:
            try:
                self.stop_tunnel()
            except Exception as e:
                print(f"Error stopping tunnel: {e}")
        else:
            try:
                self.start_tunnel()
            except Exception as e:
                print(f"Error starting tunnel: {e}")
        # Ensure UI is updated after the tunnel operation completes
        self.update_ui()

    def update_ui(self):
        if self.process:
            self.ui.action_tunnel.setIcon(QIcon(ICONS.STOP))
        else:
            self.ui.action_tunnel.setIcon(QIcon(ICONS.START))

    def start_tunnel(self):
        type_ = self.tunnelconfig.ui.comboBox_tunnel_type.currentText()
        ssh = self.tunnelconfig.ui.comboBox_ssh.currentText()

        # 本地服务器地址
        local_bind_address = self.tunnelconfig.ui.local_bind_address_edit.text()
        local_host, local_port = local_bind_address.split(':')[0], int(local_bind_address.split(':')[1])

        # 获取SSH信息
        ssh_user, ssh_password, host, key_type, key_file = open_data(ssh)
        ssh_host, ssh_port = host.split(':')[0], int(host.split(':')[1])

        tunnel, ssh_client, transport = None, None, None
        tunnel_id = self.ui.name.text()
        if type_ == '本地':
            remote_bind_address = self.tunnelconfig.ui.remote_bind_address_edit.text()
            remote_host, remote_port = remote_bind_address.split(':')[0], int(remote_bind_address.split(':')[1])
            # 启动本地转发隧道
            tunnel, ssh_client, transport = self.manager.start_tunnel(tunnel_id, 'local', local_host, local_port,
                                                                      remote_host, remote_port, ssh_host, ssh_port,
                                                                      ssh_user, ssh_password, key_type, key_file)
        if type_ == '远程':
            remote_bind_address = self.tunnelconfig.ui.remote_bind_address_edit.text()
            remote_host, remote_port = remote_bind_address.split(':')[0], int(remote_bind_address.split(':')[1])
            # 启动远程转发隧道
            tunnel, ssh_client, transport = self.manager.start_tunnel(tunnel_id, 'remote', local_host, local_port,
                                                                      remote_host, remote_port, ssh_host, ssh_port,
                                                                      ssh_user, ssh_password, key_type, key_file)
        if type_ == '动态':
            # 启动动态转发隧道
            tunnel, ssh_client, transport = self.manager.start_tunnel(tunnel_id, 'dynamic', local_host, local_port,
                                                                      ssh_host=ssh_host, ssh_port=ssh_port,
                                                                      ssh_user=ssh_user, ssh_password=ssh_password,
                                                                      key_type=key_type, key_file=key_file)

        self.manager.add_tunnel(tunnel_id, tunnel)
        self.manager.ssh_clients[ssh_client] = transport
        if transport:
            self.process = True

        self.ui.action_tunnel.setIcon(QIcon(ICONS.STOP))
        self.do_open_browser()

    def stop_tunnel(self):
        try:
            # self.process.kill()
            name_text = self.ui.name.text()
            self.manager.remove_tunnel(name_text)
            self.process = False

        except Exception as e:
            print(f"Error stopping process: {e}")
        self.ui.action_tunnel.setIcon(QIcon(ICONS.START))

    # 删除隧道
    def delete_tunnel(self, parent):

        # 创建消息框
        reply = QMessageBox()
        reply.setWindowTitle('确认删除')
        reply.setText(f'您确定要删除此隧道吗？这将无法恢复！')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # 设置按钮文本为中文
        yes_button = reply.button(QMessageBox.Yes)
        no_button = reply.button(QMessageBox.No)
        yes_button.setText("确定")
        no_button.setText("取消")
        # 显示对话框并等待用户响应
        reply.exec()

        if reply.clickedButton() == yes_button:
            name_text = self.ui.name.text()
            file_path = 'conf/tunnel.json'
            # 读取 JSON 文件内容
            data = util.read_json(file_path)
            del data[name_text]
            # 将修改后的数据写回 JSON 文件
            util.write_json(file_path, data)
            # 刷新隧道列表
            util.clear_grid_layout(parent.ui.gridLayout_ssh)
            parent.tunnel_refresh()
        else:
            pass


def open_data(ssh):
    with open('conf/config.dat', 'rb') as c:
        conf = pickle.loads(c.read())[ssh]
    username, password, host, key_type, key_file = '', '', '', '', ''
    if len(conf) == 3:
        return username, password, host, '', ''
    else:
        return conf[0], conf[1], conf[2], conf[3], conf[4]


if __name__ == '__main__':
    print("PySide6 version:", PySide6.__version__)
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
