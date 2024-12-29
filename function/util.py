import json
import os
import shutil
import socket

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileIconProvider

# 小于展示字节，大于或等于展示KB
MAX_BYTES_SIZE = 1024
# 小于展示KB，大于或等于展示MB
MAX_KB_SIZE = 1024 * 1024
# 小于展示MB，大于或等于展示GB
MAX_MB_SIZE = 1024 * 1024 * 1024

BANNER = """
               _                         _            _  _ 
              | |                       | |          | || |
   ___  _   _ | |__    ___  ______  ___ | |__    ___ | || |
  / __|| | | || '_ \  / _ \|______|/ __|| '_ \  / _ \| || |
 | (__ | |_| || |_) ||  __/        \__ \| | | ||  __/| || |
  \___| \__,_||_.__/  \___|        |___/|_| |_| \___||_||_|\n 
欢迎使用 cube-shell SSH 服务器远程管理工具 如有疑问请在项目主页联系作者\n                                            
"""

# 主题
THEME = None


def get_default_folder_icon():
    """
    # 获取系统默认文件夹图标
    :return:
    """
    # 创建一个 QFileIconProvider 对象
    icon_provider = QFileIconProvider()

    # 获取文件夹的默认图标
    folder_icon = icon_provider.icon(QFileIconProvider.Folder)

    return folder_icon


# 获取系统默认文件图标
def get_default_file_icon(qt_str):
    # 创建一个 QFileIconProvider 对象
    icon_provider = QFileIconProvider()

    if qt_str.endswith(".sh"):
        return QIcon(':icons8-ssh-48.png')
    elif qt_str.endswith(".py"):
        return QIcon(':icons8-python-48.png')
    elif qt_str.endswith(".java"):
        return QIcon(':icons8-java-48.png')
    elif qt_str.endswith(".go"):
        return QIcon(':icons8-golang-48.png')
    elif qt_str.endswith(".c"):
        return QIcon(':icons8-c-48.png')
    elif qt_str.endswith(".cpp"):
        return QIcon(':icons8-c-48.png')
    elif qt_str.endswith(".js"):
        return QIcon(':icons8-js-48.png')
    elif qt_str.endswith(".vue"):
        return QIcon(':icons8-vuejs-48.png')
    elif qt_str.endswith(".html"):
        return QIcon(':icons8-html-48.png')
    elif qt_str.endswith(".css"):
        return QIcon(':icons8-css-48.png')
    elif qt_str.endswith(".exe"):
        return QIcon(':icons8-exe-48.png')
    elif qt_str.endswith(".jar"):
        return QIcon(':icons8-jar-48.png')
    elif qt_str.endswith(".so"):
        return QIcon(':icons8-linux-48.png')
    elif qt_str.endswith(('.tar', '.gz', '.zip', '.jar')):
        return QIcon(':icons8-zip-48.png')
    elif qt_str.endswith(('.cfg', '.gitconfig', '.conf')):
        return QIcon(':icons8-settings-40.png')
    elif qt_str.endswith('.png'):
        return QIcon(':icons8-png-48.png')
    elif qt_str.endswith('.gif'):
        return QIcon(':icons8-gif-48.png')
    elif qt_str.endswith(('.jpg', '.jpeg')):
        return QIcon(':icons8-jpg-48.png')
    elif qt_str.endswith('.license'):
        return QIcon(':icons8-license-48.png')
    elif qt_str.endswith('.json'):
        return QIcon(':icons8-json-48.png')
    elif qt_str.endswith('.txt'):
        return QIcon(':icons8-txt-48.png')
    elif qt_str.endswith('.gitignore'):
        return QIcon(':icons8-gitignore-48.png')
    elif qt_str.endswith('.md'):
        return QIcon(':icons8-md-48.png')
    elif qt_str.endswith(('.yaml', '.yml')):
        return QIcon(':icons8-yaml-48.png')
    elif qt_str.endswith('.properties'):
        return QIcon(':icons8-properties-48.png')
    elif qt_str.endswith('.log'):
        return QIcon(':icons-log-48.png')
    elif qt_str.endswith('.toml'):
        return QIcon(':icons-toml-48.png')

    return icon_provider.icon(QFileIconProvider.File)


def format_file_size(size_in_bytes):
    """
    根据文件大小返回适当的单位展示文件大小。
    :param size_in_bytes: 文件大小（以字节为单位）
    :return: 格式化的文件大小字符串
    """
    if size_in_bytes < MAX_BYTES_SIZE:
        return f"{size_in_bytes} 字节"
    elif size_in_bytes < MAX_KB_SIZE:
        size_in_kb = size_in_bytes / 1024
        return f"{size_in_kb:.2f} KB"
    elif size_in_bytes < MAX_MB_SIZE:
        size_in_mb = size_in_bytes / (1024 * 1024)
        return f"{size_in_mb:.2f} MB"
    else:
        size_in_gb = size_in_bytes / (1024 * 1024 * 1024)
        return f"{size_in_gb:.3f} GB"


def has_valid_suffix(filename):
    """
    检测是否包含以下类型文件
    :param filename:文件名
    :return: 包含返回true
    """
    return filename.endswith(('.db', '.exe', '.bin', '.jar', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt',
                              '.pptx', '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.iso', '.img', '.dmg', '.apk',
                              '.ipa', '.deb', '.rpm', '.msi', '.jar', '.war', '.ear', '.dmp', '.phd', '.trc',
                              '.Xauthority'))


def check_remote_directory_exists(sftp, directory):
    """
    判断文件夹是否存在
    :param sftp:
    :param directory:
    :return:
    """
    try:
        sftp.stat(directory)
        return True
    except FileNotFoundError:
        return False


def read_json_file(file_path):
    """
    读取json文件
    :param file_path: 文件地址
    :return:返回json对象
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None


# 函数：清空QGridLayout中的所有widget
def clear_grid_layout(layout):
    while layout.count():
        layout_item = layout.takeAt(0)
        if layout_item.widget():
            layout_item.widget().deleteLater()
        elif layout_item.layout():
            clear_grid_layout(layout_item.layout())  # 递归清空子布局
            layout_item.layout().deleteLater()


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


def remove_special_lines(text):
    # 拆分文本为行
    lines = text.split('\n')
    # 用于存储过滤后的行
    filtered_lines = []

    for line in lines:
        # 去掉行首和行尾的空白字符
        stripped_line = line.strip()
        # 如果行不只包含波浪号或空格，则保留
        if stripped_line and any(char != '~' for char in stripped_line):
            filtered_lines.append(line)

    # 重新组合过滤后的行
    result = '\n'.join(filtered_lines)
    return result


def check_server_accessibility(hostname, port):
    """
    快速检查服务器在指定端口上的可访问性。

    :param hostname: 服务器地址
    :param port: 端口号
    :return: 如果可访问返回 True，否则返回 False
    """
    try:
        # 使用 socket.create_connection 检查服务器可访问性
        with socket.create_connection((hostname, port), timeout=1):
            return True
    except (socket.timeout, socket.error) as e:
        print(f"Connection failed: {e}")
        return False


def read_json(file_path):
    """
    读取json文件
    :param file_path:
    :return:
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def write_json(file_path, data):
    """
    写入json文件
    indent=4 让文件具有可读性
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


# 速度格式化
def format_speed(speed):
    if speed >= 1024 * 1024:
        return f"{speed / (1024 * 1024):.2f} MB/s"
    elif speed >= 1024:
        return f"{speed / 1024:.2f} KB/s"
    else:
        return f"{speed:.0f} B/s"


# 拷贝文件到指定目录
def copy_file(src_path, dest_path):
    try:
        # 复制文件
        shutil.copy2(src_path, dest_path)
        print(f"File copied from {src_path} to {dest_path}")
    except FileNotFoundError:
        print(f"Source file not found: {src_path}")
    except PermissionError:
        print(f"Permission denied while copying to {dest_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


def copy_config_to_conf(source_path: str, target_dir: str) -> None:
    try:
        # 确定目标文件的完整路径
        target_path = os.path.join(target_dir, os.path.basename(source_path))

        # 如果目标文件存在，则删除它
        if os.path.exists(target_path):
            os.remove(target_path)

        # 复制文件
        shutil.copy2(source_path, target_path)
        print(f"File copied from {source_path} to {target_path}")
    except FileNotFoundError:
        print(f"Source file not found: {source_path}")
    except PermissionError:
        print(f"Permission denied while copying to {target_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


# 符号权限转八进制权限
def symbolic_to_octal(symbolic):
    # 排除第一个字符，它通常是文件类型
    user, group, others = symbolic[0:3], symbolic[3:6], symbolic[6:9]

    def calc_permission(perm):
        mapping = {'r': 4, 'w': 2, 'x': 1, '-': 0}
        return sum(mapping[char] for char in perm)

    return (
            calc_permission(user) * 100 +
            calc_permission(group) * 10 +
            calc_permission(others)
    )


def get_config_dir():
    """获取配置文件目录"""
    home = os.path.expanduser('~')
    config_dir = os.path.join(home, '.cube-shell')
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return config_dir


def get_config_path(filename):
    """获取配置文件的完整路径"""
    return os.path.join(get_config_dir(), filename)
