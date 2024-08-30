import os
import pickle
import platform
import sys
import threading
import time

import PySide6
import paramiko
import qdarkstyle
from PySide6.QtCore import QTimer, Signal, Qt, QPoint, QRect, QEvent
from PySide6.QtGui import QIcon, QAction, QTextCursor, QCursor, QCloseEvent, QKeyEvent, QInputMethodEvent, QPixmap, \
    QDragEnterEvent, QDropEvent, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QDialog, QMessageBox, QTreeWidgetItem, \
    QInputDialog, QFileDialog, QTreeWidget
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
from qdarkstyle import DarkPalette, LightPalette

from function import ssh_func, get_running_data, util
from function.util import format_file_size, has_valid_suffix
from style.style import updateColor
from ui import add_config, text_editor, confirm, main


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

        # 设置拖放行为
        self.setAcceptDrops(True)

        self.ui.Shell.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.ui.Shell.setAttribute(Qt.WA_KeyCompression, True)

        self.ssh_conn = None
        self.sign = b''
        self.timer, self.timer1, self.timer2 = None, None, None
        self.getsysinfo = None
        self.dir_tree_now = []
        self.pwd = ''
        self.file_name = ''
        self.fileEvent = ''

        self.ssh_username, self.ssh_password, self.ssh_ip = None, None, None

        self.ui.discButton.clicked.connect(self.disconnect)
        self.ui.seeOnline.clicked.connect(self.getRunData)
        self.ui.setWan.clicked.connect(self.getRunData)
        self.ui.setLan.clicked.connect(self.getRunData)
        self.ui.init.clicked.connect(self.getRunData)
        self.ui.showPort.clicked.connect(self.getRunData)
        self.ui.webview.clicked.connect(self.toggleTheme)
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

        self.ui.treeWidget333.customContextMenuRequested.connect(self.treeDocker)

        self.isConnected = False

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
                    self.select_items_in_rect(self.selection_rect)
                    return True
            elif event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    if event.timestamp() - self.left_click_time < 300:  # 判断是否为单击
                        self.is_left_selecting = False
                        item = self.ui.treeWidget.itemAt(event.pos())
                        if item:
                            self.ui.treeWidget.clearSelection()
                            item.setSelected(True)
                        return False  # 允许左键单击事件继续处理
                    self.is_left_selecting = False
                    return True

        return super().eventFilter(source, event)

    def select_items_in_rect(self, rect):
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

    # 连接服务器
    def connect(self):
        focus = self.ui.treeWidget.currentIndex().row()
        if focus != -1:
            name = self.ui.treeWidget.topLevelItem(focus).text(0)
            with open('config.dat', 'rb') as c:
                conf = pickle.loads(c.read())[name]
                c.close()
            username, password, host = conf[0], conf[1], conf[2]
            try:
                self.ssh_conn = ssh_func.SshClient(host.split(':')[0], int(host.split(':')[1]), username, password)
                self.ssh_conn.connect()
                self.ssh_conn.open_sftp()
            except Exception as e:
                self.ui.Shell.setPlaceholderText(str(e))
            self.ssh_username, self.ssh_password, self.ssh_ip = username, password, host
            if self.ssh_conn.session is not None:
                self.isConnected = True
                self.ui.discButton.setEnabled(True)
                self.ui.seeOnline.setEnabled(True)
                self.ui.result.setEnabled(True)
                self.ui.lanIP.setEnabled(True)
                self.ui.wanIP.setEnabled(True)
                self.ui.gateway.setEnabled(True)
                self.ui.setWan.setEnabled(True)
                self.ui.setLan.setEnabled(True)
                self.ui.initKey.setEnabled(True)
                self.ui.init.setEnabled(True)
                self.ui.webview.setEnabled(True)
                self.ui.showPort.setEnabled(True)
                self.ui.webview.setEnabled(True)
                self.ui.iport.setEnabled(True)
                self.ui.Shell.setEnabled(True)
                self.ui.timezoneButton.setEnabled(True)
                th1 = threading.Thread(target=self.ssh_conn.receive, daemon=True)
                th1.start()
                self.getsysinfo = get_running_data.DevicInfo(username=conf[0], password=conf[1], host=conf[2])
                th3 = threading.Thread(target=self.getsysinfo.get_datas, daemon=True)
                th3.start()
                self.flush()
                self.flushSysInfo()
                time.sleep(1.5)  # 延迟一秒
                self.refreshDokerInfo()
                self.flushDokerInfo()
                self.refreshDirs()
            else:
                pass
        else:
            self.alarm('请选择一台设备！')

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
        self.timer.stop()
        self.timer1.stop()
        self.timer2.stop()

        self.ssh_conn.term_data = b''
        self.ssh_conn.diconnect()
        self.isConnected = False
        self.ssh_username, self.ssh_password, self.ssh_ip = None, None, None
        self.ui.discButton.setDisabled(True)
        self.ui.seeOnline.setDisabled(True)
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
        self.ui.showPort.setDisabled(True)
        self.ui.timezoneButton.setDisabled(True)

        self.ui.treeWidget333.clear()
        self.ui.result.clear()

        self.ui.cpuRate.setValue(0)
        self.ui.diskRate.setValue(0)
        self.ui.memRate.setValue(0)

        self.getsysinfo.disconnect()
        self.refreshConf()

    # 定时刷新shell
    def flush(self):
        self.timer = QTimer()
        self.timer.start(15)
        self.timer.timeout.connect(self.refreshXterm)

    # 刷新shell
    def refreshXterm(self):
        if self.isConnected is True:
            if self.isConnected is True and self.sign != self.ssh_conn.buffer3:
                to_show = self.ssh_conn.buffer3
                # 使用Pygments进行语法高亮
                formatter = HtmlFormatter(style='rrt', noclasses=True, bg_color='#ffffff')
                self.ui.Shell.setStyleSheet("background-color: rgb(0, 0, 0);")

                # formatter = HtmlFormatter(style='paraiso-dark', noclasses=True, bg_color='#ffffff')
                # formatter = HtmlFormatter(style='native', noclasses=True, bg_color='#ffffff')
                # formatter = HtmlFormatter(style='monokai', noclasses=True, bg_color='#ffffff')

                # formatter = HtmlFormatter(style='lightbulb', noclasses=True, bg_color='#ffffff')

                filtered_data = to_show.replace("\0", " ")
                # 高亮代码
                highlighted2 = highlight(filtered_data, PythonLexer(), formatter)

                # 将HTML插入QTextBrowser
                self.ui.Shell.setHtml(highlighted2)
                self.ui.Shell.moveCursor(QTextCursor.End)
                self.sign = self.ssh_conn.buffer3
            elif self.sign == self.ssh_conn.buffer3:
                pass

    # 键盘事件， shell输入
    def keyReleaseEvent(self, a0: QKeyEvent) -> None:
        print(a0.text())
        try:
            if a0.key() == 16777219:
                self.ssh_conn.send(b'\x08')
            elif a0.key() == 16777219:
                self.ssh_con.send(b'\x09')
            elif a0.key() == 16777235:
                self.ssh_conn.send(b'\x1b[A')
            elif a0.key() == 16777237:
                self.ssh_conn.send(b'\x1b[B')
            elif a0.key() == 16777234:
                self.ssh_conn.send(b'\x1b[D')
            elif a0.key() == 16777236:
                self.ssh_conn.send(b'\x1b[C')
            elif a0.key() == 16777220:
                self.ssh_conn.buffer1 = ['▉', '']
                self.ssh_conn.send(b'\r')
            else:
                self.ssh_conn.send(a0.text().encode('utf8'))
        except Exception as e:
            print(f'连接已经关闭，不能再进行操作{e}')
            # self.ui.result.append(e)

    def inputMethodEvent(self, a0: QInputMethodEvent) -> None:
        cmd = a0.commitString()
        print(cmd)
        if cmd != '':
            self.ssh_conn.send(cmd.encode('utf8'))

    # 服务器运行命令并获取输出
    def getRunData(self, cmd=''):
        sender = self.sender()
        cmd = cmd
        if sender.objectName() == 'seeOnline':
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
        elif sender.objectName() == 'showPort':
            # ip = self.ui.iport.text()
            # cmd = 'sudo nmap -PN ' + ip
            self.ui.initKey.clear()
            cmd = 'sudo clear'
        elif sender.objectName() == 'timezoneButton':
            cmd = 'sudo timedatectl set-timezone "Asia/Shanghai" && sudo hwclock'
        else:
            pass
        self.ui.progressBar.setValue(20)
        username, password, host = self.ssh_username, self.ssh_password, self.ssh_ip
        self.ui.result.append(cmd)
        if self.isConnected is True:
            try:
                # 创建SSH对象
                ssh = paramiko.SSHClient()
                # 允许连接不在know_hosts文件中的主机
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                # 连接服务器
                ssh.connect(hostname=host.split(':')[0], port=int(host.split(':')[1]),
                            username=username, password=password, timeout=3)
                self.ui.progressBar.setValue(50)
                # 执行命令
                stdin, stdout, stderr = ssh.exec_command(timeout=10, bufsize=100, command=cmd)
                # 获取命令结果
                ack = stdout.read().decode('utf8')

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
            # 创建菜单选项对象
            self.ui.action = QAction('添加配置', self)
            self.ui.action2 = QAction('删除配置', self)
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
            self.ui.action = QAction('下载文件', self)
            self.ui.action2 = QAction('上传文件', self)
            self.ui.action3 = QAction('编辑文本', self)
            self.ui.action4 = QAction('创建文件夹', self)
            self.ui.action4_1 = QAction('创建文件', self)
            self.ui.action5 = QAction('删除', self)
            self.ui.tree_menu.addAction(self.ui.action)
            self.ui.tree_menu.addAction(self.ui.action2)
            self.ui.tree_menu.addAction(self.ui.action3)
            self.ui.tree_menu.addAction(self.ui.action4)
            self.ui.tree_menu.addAction(self.ui.action4_1)

            # 添加分割线,做标记区分
            bottom_separator = QAction(self)
            bottom_separator.setSeparator(True)
            self.ui.tree_menu.addAction(bottom_separator)

            self.ui.tree_menu.addAction(self.ui.action5)
            self.ui.action.triggered.connect(self.downloadFile)
            self.ui.action2.triggered.connect(self.uploadFile)
            self.ui.action3.triggered.connect(self.editFile)
            self.ui.action4.triggered.connect(self.createDir)
            self.ui.action4_1.triggered.connect(self.createFile)
            self.ui.action5.triggered.connect(self.remove)
            # 声明当鼠标在groupBox控件上右击时，在鼠标位置显示右键菜单   ,exec_,popup两个都可以，
            self.ui.tree_menu.popup(QCursor.pos())

    # 创建docker列表树右键菜单函数
    def treeDocker(self):
        if self.isConnected:
            self.ui.tree_menu = QMenu(self)
            self.ui.action1 = QAction('停止', self)
            self.ui.action2 = QAction('重启', self)
            self.ui.action3 = QAction('删除', self)
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

    # 刷新设备列表
    def refreshConf(self):
        if not os.path.exists('config.dat'):
            with open('config.dat', 'wb') as c:
                start_dic = {}
                c.write(pickle.dumps(start_dic))
                c.close()
        with open('config.dat', 'rb') as c:
            dic = pickle.loads(c.read())
            c.close()
        i = 0
        self.ui.treeWidget.clear()
        self.ui.treeWidget.headerItem().setText(0, '设备列表')

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
                folder_icon = util.getDefaultFolderIcon()
                self.ui.treeWidget.topLevelItem(i).setIcon(0, folder_icon)
            elif n[0][0] in ['l', '-', 's']:
                file_icon = util.getDefaultFileIcon(n[8])
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
        if sig == 0:
            self.getData2('sudo echo -e "' + nt + '" > ' + self.pwd + '/' + self.file_name)
            self.ui.addTextEditWin.new_text = self.ui.addTextEditWin.old_text
            self.ui.addTextEditWin.te.chk.close()
            self.ui.addTextEditWin.close()
        elif sig == 1:
            self.getData2('sudo echo -e "' + nt + '" > ' + self.pwd + '/' + self.file_name)
            self.ui.addTextEditWin.old_text = nt

    # 删除设备配置文件
    def delConf(self):
        focus = self.ui.treeWidget.currentIndex().row()
        if focus != -1:
            name = self.ui.treeWidget.topLevelItem(focus).text(0)
            with open('config.dat', 'rb') as c:
                conf = pickle.loads(c.read())
                c.close()
            with open('config.dat', 'wb') as c:
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
        self.timer2.start(10000)
        self.timer2.timeout.connect(self.refreshDokerInfo)

    def refreshDokerInfo(self):
        if self.isConnected:
            info = self.getsysinfo.docker_info
            self.ui.treeWidget333.clear()
            self.ui.treeWidget333.headerItem().setText(0, 'docker容器管理：')
            if len(info) != 0:
                i = 0
                for n in info:
                    self.ui.treeWidget333.addTopLevelItem(QTreeWidgetItem(0))
                    self.ui.treeWidget333.topLevelItem(i).setText(0, n)
                    if i != 0:
                        self.ui.treeWidget333.topLevelItem(i).setIcon(0, QIcon("icons/icons8-docker-48.png"))
                    # 设置字体为加粗
                    if i == 0:
                        bold_font = QFont()
                        bold_font.setBold(True)  # 设置字体为加粗
                        self.ui.treeWidget333.topLevelItem(i).setFont(0, bold_font)

                    i += 1

                # 设置列宽为自适应内容
                for i in range(self.ui.treeWidget333.columnCount()):
                    self.ui.treeWidget333.resizeColumnToContents(i)
            else:
                self.ui.treeWidget333.addTopLevelItem(QTreeWidgetItem(0))
                self.ui.treeWidget333.topLevelItem(0).setText(0, '没有可用的docker容器')
        else:
            self.ui.treeWidget333.clear()
            self.ui.treeWidget333.addTopLevelItem(QTreeWidgetItem(0))
            self.ui.treeWidget333.topLevelItem(0).setText(0, '没有可用的docker容器')

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
                        deleteFolder(sftp, self.pwd + '/' + key)
                    else:
                        sftp.remove(self.pwd + '/' + key)
                    self.refreshDirs()
                except IOError as e:
                    print(f"Failed to remove file: {e}")
            rm_dict.clear()
            self.success("删除")

    # 停止docker容器
    def stopDockerContainer(self):
        focus = self.ui.treeWidget333.currentIndex().row()
        if focus != -1:
            text = self.ui.treeWidget333.topLevelItem(focus).text(0)
            # 取出前12位字符串
            container_id = text[:12]
            data_ = self.getData2('sudo docker stop ' + container_id)
            print('stop----', data_)
            time.sleep(2)  # 延迟一秒
            self.refreshDokerInfo()

    # 重启docker容器
    def restartDockerContainer(self):
        focus = self.ui.treeWidget333.currentIndex().row()
        if focus != -1:
            text = self.ui.treeWidget333.topLevelItem(focus).text(0)
            # 取出前12位字符串
            container_id = text[:12]
            data_ = self.getData2('sudo docker restart ' + container_id)
            print('restart----', data_)
            time.sleep(2)  # 延迟一秒
            self.refreshDokerInfo()

    # 删除docker容器
    def rmDockerContainer(self):
        focus = self.ui.treeWidget333.currentIndex().row()
        if focus != -1:
            text = self.ui.treeWidget333.topLevelItem(focus).text(0)
            # 取出前12位字符串
            container_id = text[:12]
            data_ = self.getData2('sudo docker rm ' + container_id)
            print('rm----', data_)
            time.sleep(2)  # 延迟一秒
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
        print(a0)

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


# 删除文件夹
def deleteFolder(sftp, path):
    """
        递归删除远程服务器上的文件夹及其内容
        :param sftp: 远程服务器的连接对象
        :param path: 待删除的文件夹路径
        """
    try:
        # 获取文件夹中的文件和子文件夹列表
        files = sftp.listdir(path)
    except IOError:
        # The path does not exist or is not a directory
        return

    # 遍历文件和子文件夹列表
    for file in files:
        # 拼接完整的文件或文件夹路径
        filepath = f"{path}/{file}"
        try:
            # 检查路径是否存在
            sftp.stat(filepath)
        except IOError as e:
            print(f"Failed to remove: {e}")
            continue

        try:
            # 删除文件
            sftp.remove(filepath)  # Delete file
        except IOError:
            # 递归调用deleteFolder函数删除子文件夹及其内容
            deleteFolder(sftp, filepath)

    # 最后删除空文件夹
    sftp.rmdir(path)


# 增加配置逻辑
class AddConfigUi(QDialog):

    def __init__(self):
        super().__init__()
        self.dial = add_config.Ui_addConfig()
        self.dial.setupUi(self)
        self.setWindowIcon(QIcon("Resources/icon.ico"))
        self.dial.pushButton.clicked.connect(self.addDev)

    def addDev(self):
        name, username, password, ip, prot = self.dial.configName.text(), self.dial.usernamEdit.text(), \
            self.dial.passwordEdit.text(), self.dial.ipEdit.text(), self.dial.protEdit.text()
        if name == '':
            self.alarm('配置名称不能为空！')
        elif username == '':
            self.alarm('用户名不能为空！')
        elif password == '':
            self.alarm('密码不能为空！')
        elif ip == '':
            self.alarm('ip地址不能为空！')
        else:
            with open('config.dat', 'rb') as c:
                conf = pickle.loads(c.read())
                c.close()
            with open('config.dat', 'wb') as c:
                conf[name] = [username, password, f"{ip}:{prot}"]
                c.write(pickle.dumps(conf))
                c.close()
            self.close()

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


if __name__ == '__main__':
    print("PySide6 version:", PySide6.__version__)
    app = QApplication(sys.argv)

    window = MainDialog(app)

    window.show()
    window.refreshConf()
    sys.exit(app.exec())
