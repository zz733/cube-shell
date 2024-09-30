import json

from PySide6.QtCore import QSortFilterProxyModel, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QLineEdit, QTreeView, QWidget


# 创建树搜索应用程序
class TreeSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建主窗口
        self.setWindowTitle("Linux常用命令查找")
        self.setGeometry(100, 100, 600, 400)

        # 创建中央小部件和布局
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建搜索框
        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Search...")
        layout.addWidget(self.search_box)

        # 创建树视图
        self.tree_view = QTreeView(self)
        layout.addWidget(self.tree_view)

        # 创建模型并填充数据
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['命令', '选项', '描述'])

        # 读取 JSON 数据并填充模型
        self.load_data_from_json('conf/linux_commands.json')

        # 创建代理模型用于过滤
        self.proxy_model = TreeFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setRecursiveFilteringEnabled(True)

        # 设置模型到树视图
        self.tree_view.setModel(self.proxy_model)

        # 连接搜索框的输入事件
        self.search_box.textChanged.connect(self.filter_tree)

    def load_data_from_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.add_items(self.model.invisibleRootItem(), data['treeData'])

    def add_items(self, parent, elements):
        for element in elements:
            command_item = QStandardItem(element['command'])
            option_item = QStandardItem(element['option'])
            description_item = QStandardItem(element['description'])

            parent.appendRow([command_item, option_item, description_item])

            if 'children' in element:
                self.add_items(command_item, element['children'])

    def filter_tree(self):
        search_text = self.search_box.text()
        self.proxy_model.setFilterRegularExpression(search_text)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)


# 创建代理模型
class TreeFilterProxyModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)  # 获取当前行的第一个索引

        # 检查当前行是否匹配过滤条件
        for column in range(model.columnCount()):
            if self.filterRegularExpression().match(
                    model.data(model.index(source_row, column, source_parent))).hasMatch():
                return True

        # 递归检查子项是否匹配过滤条件
        for i in range(model.rowCount(index)):  # 使用当前行的索引作为父索引
            if self.filterAcceptsRow(i, index):
                return True

        return False
