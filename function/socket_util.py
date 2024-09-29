import sys
import os
import subprocess
import socket
from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton
from PySide6.QtGui import QColor, QTextCursor


class Terminal(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Enhanced Terminal")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        # 当前工作目录，初始化为用户目录
        self.current_directory = os.path.expanduser("~")  # 获取用户主目录
        os.chdir(self.current_directory)  # 切换到用户主目录

        # 命令输入框
        self.command_input = QLineEdit(self)
        self.command_input.setPlaceholderText("Enter command here...")
        self.command_input.returnPressed.connect(self.execute_command)
        self.layout.addWidget(self.command_input)

        # 执行按钮
        self.execute_button = QPushButton("Execute", self)
        self.execute_button.clicked.connect(self.execute_command)
        self.layout.addWidget(self.execute_button)

        # 输出区域
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.layout.addWidget(self.output_area)

        # 历史命令存储
        self.command_history = []
        self.history_index = -1

        # 显示首次连接的 Last login 信息
        self.show_last_login()

        # 添加初始提示符
        self.show_prompt()

        self.setLayout(self.layout)

        # 连接输入框的键盘事件处理函数
        self.command_input.keyPressEvent = self.handle_key_press

    def show_last_login(self):
        # 获取当前时间
        now = datetime.now()
        # 获取本地 IP 地址
        ip_address = self.get_local_ip()
        # 格式化时间，类似 Last login: Fri Sep 10 12:34:56 2024 from 192.168.1.10
        last_login_message = now.strftime(f"Last login: %a %b %d %H:%M:%S %Y from {ip_address}")
        # 显示 Last login 信息
        self.append_output(last_login_message, "cyan")

    def get_local_ip(self):
        """获取本地 IP 地址"""
        try:
            # 获取主机名并通过主机名解析到本地 IP
            local_ip = socket.gethostbyname(socket.gethostname())
            return local_ip
        except Exception:
            # 如果发生错误，返回 127.0.0.1 作为默认 IP
            return "127.0.0.1"

    def show_prompt(self):
        # 获取当前的用户、主机名和工作目录
        user = os.getlogin()  # 获取用户名
        host = os.uname().nodename  # 获取主机名
        directory = os.getcwd()  # 获取当前目录

        # 构造类似 `user@host dir#` 的提示符
        prompt = f"[{user}@{host} {os.path.basename(directory)}]# "

        # 显示提示符
        self.append_output(prompt, "blue")

    def execute_command(self):
        command = self.command_input.text().strip()
        if command:
            # 检查是否为退出命令
            if command in ["exit", "logout"]:
                self.append_output("Connection closed.", "red")
                QApplication.quit()
                return

            # 将命令加入历史记录
            self.command_history.append(command)
            self.history_index = len(self.command_history)

            # 显示命令
            self.append_output(f"{command}", "blue")

            # 检查是否是 cd 命令
            if command.startswith("cd "):
                # 获取路径
                path = command[3:].strip()
                if os.path.isdir(path):  # 检查目录是否存在
                    try:
                        os.chdir(path)  # 改变当前工作目录
                        self.current_directory = os.getcwd()  # 更新当前目录
                        self.append_output(f"Changed directory to {self.current_directory}", "green")
                    except Exception as e:
                        self.append_output(f"cd: {str(e)}", "red")
                else:
                    # 如果路径不存在，显示错误信息
                    self.append_output(f"cd: No such file or directory: '{path}'", "red")
            else:
                try:
                    # 执行其他命令
                    result = subprocess.run(command, shell=True, capture_output=True, text=True,
                                            cwd=self.current_directory)
                    # 获取命令的输出和错误信息
                    if result.stdout:
                        self.append_output(result.stdout, "green")
                    if result.stderr:
                        self.append_output(result.stderr, "red")
                except Exception as e:
                    self.append_output(f"Error: {str(e)}", "red")

            # 清空输入框
            self.command_input.clear()

            # 显示新的提示符
            self.show_prompt()

    def append_output(self, text, color):
        # 设置文本的颜色
        self.output_area.setTextColor(QColor(color))
        self.output_area.append(text)
        self.output_area.setTextColor(QColor("black"))

        # 自动滚动到最后一行
        self.output_area.moveCursor(QTextCursor.End)

    def handle_key_press(self, event):
        # 处理命令历史的上下箭头
        if event.key() == 16777235:  # 上箭头
            if self.history_index > 0:
                self.history_index -= 1
                self.command_input.setText(self.command_history[self.history_index])
        elif event.key() == 16777237:  # 下箭头
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.command_input.setText(self.command_history[self.history_index])
            else:
                self.history_index = len(self.command_history)
                self.command_input.clear()
        else:
            # 调用原始的键盘事件处理
            QLineEdit.keyPressEvent(self.command_input, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    terminal = Terminal()
    terminal.show()
    sys.exit(app.exec())
