# -*- coding: utf-8 -*-
import os
import pickle

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize, Qt)
from PySide6.QtGui import (QIcon, QCursor)
from PySide6.QtWidgets import (QComboBox, QDialogButtonBox, QGridLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
                               QWidget)

from style.style import PrimaryButtonStyle


class Ui_TunnelConfig(object):
    def setupUi(self, TunnelConfig):
        if not TunnelConfig.objectName():
            TunnelConfig.setObjectName(u"TunnelConfig")
        TunnelConfig.resize(386, 257)
        self.gridLayout = QGridLayout(TunnelConfig)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(188, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.buttonBox = QDialogButtonBox(TunnelConfig)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Save)
        # 更改按钮文本
        ok_button = self.buttonBox.button(QDialogButtonBox.StandardButton.Save)
        ok_button.setText('保存')
        ok_button.setStyleSheet(PrimaryButtonStyle)
        ok_button.setCursor(QCursor(Qt.PointingHandCursor))

        self.horizontalLayout.addWidget(self.buttonBox)

        self.gridLayout.addLayout(self.horizontalLayout, 9, 0, 1, 3)

        self.comboBox_ssh = QComboBox(TunnelConfig)
        self.comboBox_ssh.setObjectName(u"comboBox_ssh")

        self.gridLayout.addWidget(self.comboBox_ssh, 1, 1, 1, 2)

        self.label_browser_open = QLabel(TunnelConfig)
        self.label_browser_open.setObjectName(u"label_browser_open")

        self.gridLayout.addWidget(self.label_browser_open, 7, 0, 1, 1)

        self.local_bind_address_edit = QLineEdit(TunnelConfig)
        self.local_bind_address_edit.setObjectName(u"local_bind_address_edit")

        self.gridLayout.addWidget(self.local_bind_address_edit, 6, 1, 1, 2)

        self.ssh_command = QLineEdit(TunnelConfig)
        self.ssh_command.setObjectName(u"ssh_command")
        self.ssh_command.setReadOnly(True)

        self.gridLayout.addWidget(self.ssh_command, 8, 1, 1, 1)

        self.label_remote_bind_address_edit = QLabel(TunnelConfig)
        self.label_remote_bind_address_edit.setObjectName(u"label_remote_bind_address_edit")

        self.gridLayout.addWidget(self.label_remote_bind_address_edit, 3, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 0, 2, 1, 1)

        self.label = QLabel(TunnelConfig)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_local_bind_address_edit = QLabel(TunnelConfig)
        self.label_local_bind_address_edit.setObjectName(u"label_local_bind_address_edit")

        self.gridLayout.addWidget(self.label_local_bind_address_edit, 6, 0, 1, 1)

        self.copy = QPushButton(TunnelConfig)
        self.copy.setCursor(QCursor(Qt.PointingHandCursor))
        self.copy.setObjectName(u"copy")

        self.gridLayout.addWidget(self.copy, 8, 2, 1, 1)

        self.label_ssh_port_edit = QLabel(TunnelConfig)
        self.label_ssh_port_edit.setObjectName(u"label_ssh_port_edit")

        self.gridLayout.addWidget(self.label_ssh_port_edit, 1, 0, 1, 1)

        self.comboBox_tunnel_type = QComboBox(TunnelConfig)
        icon = QIcon()
        icon.addFile(u":Localhost.png", QSize(), QIcon.Mode.Selected, QIcon.State.On)
        self.comboBox_tunnel_type.addItem(icon, "")
        icon1 = QIcon()
        icon1.addFile(u":remote.png", QSize(), QIcon.Mode.Selected, QIcon.State.On)
        self.comboBox_tunnel_type.addItem(icon1, "")
        icon2 = QIcon()
        icon2.addFile(u":dynamic.png", QSize(), QIcon.Mode.Selected, QIcon.State.On)
        self.comboBox_tunnel_type.addItem(icon2, "")
        self.comboBox_tunnel_type.setObjectName(u"comboBox_tunnel_type")

        self.gridLayout.addWidget(self.comboBox_tunnel_type, 0, 1, 1, 1)

        self.browser_open = QLineEdit(TunnelConfig)
        self.browser_open.setObjectName(u"browser_open")

        self.gridLayout.addWidget(self.browser_open, 7, 1, 1, 2)

        self.remote_bind_address_edit = QLineEdit(TunnelConfig)
        self.remote_bind_address_edit.setObjectName(u"remote_bind_address_edit")

        self.gridLayout.addWidget(self.remote_bind_address_edit, 3, 1, 1, 2)

        self.label_ssh_command = QLabel(TunnelConfig)
        self.label_ssh_command.setObjectName(u"label_ssh_command")

        self.gridLayout.addWidget(self.label_ssh_command, 8, 0, 1, 1)

        QWidget.setTabOrder(self.browser_open, self.ssh_command)
        QWidget.setTabOrder(self.ssh_command, self.copy)

        self.retranslateUi(TunnelConfig)
        self.buttonBox.accepted.connect(TunnelConfig.accept)
        self.buttonBox.rejected.connect(TunnelConfig.reject)

        QMetaObject.connectSlotsByName(TunnelConfig)

    # setupUi

    def retranslateUi(self, TunnelConfig):
        TunnelConfig.setWindowTitle(QCoreApplication.translate("TunnelConfig", u"Dialog", None))
        self.label_browser_open.setText(
            QCoreApplication.translate("TunnelConfig", u"\u6d4f\u89c8\u5668\u6253\u5f00", None))
        self.local_bind_address_edit.setPlaceholderText(QCoreApplication.translate("TunnelConfig",
                                                                                   u"\u8bf7\u8f93\u5165\u672c\u5730\u7ed1\u5b9a\u5730\u5740\uff0c\u4f8b\u5982:localhost:8080",
                                                                                   None))
        self.label_remote_bind_address_edit.setText(
            QCoreApplication.translate("TunnelConfig", u"\u8fdc\u7a0b\u7ed1\u5b9a\u5730\u5740", None))
        self.label.setText(QCoreApplication.translate("TunnelConfig", u"\u8f6c\u53d1\u6a21\u5f0f", None))
        self.label_local_bind_address_edit.setText(
            QCoreApplication.translate("TunnelConfig", u"\u672c\u5730\u7ed1\u5b9a\u5730\u5740", None))
        self.copy.setText(QCoreApplication.translate("TunnelConfig", u"复制", None))
        self.label_ssh_port_edit.setText(QCoreApplication.translate("TunnelConfig", u"SSH \u670d\u52a1\u5668", None))
        self.comboBox_tunnel_type.setItemText(0, QCoreApplication.translate("TunnelConfig", u"\u672c\u5730", None))
        self.comboBox_tunnel_type.setItemText(1, QCoreApplication.translate("TunnelConfig", u"\u8fdc\u7a0b", None))
        self.comboBox_tunnel_type.setItemText(2, QCoreApplication.translate("TunnelConfig", u"\u52a8\u6001", None))

        self.browser_open.setPlaceholderText(QCoreApplication.translate("TunnelConfig", u"https://127.0.0.1:80", None))
        self.remote_bind_address_edit.setPlaceholderText(QCoreApplication.translate("TunnelConfig",
                                                                                    u"\u8bf7\u8f93\u5165\u8fdc\u7a0b\u7ed1\u5b9a\u5730\u5740\uff0c\u4f8b\u5982:localhost:8080",
                                                                                    None))
        self.label_ssh_command.setText(
            QCoreApplication.translate("TunnelConfig", u"SSH \u96a7\u9053\u547d\u4ee4", None))
    # retranslateUi
