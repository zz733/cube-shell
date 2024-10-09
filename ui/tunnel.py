# -*- coding: utf-8 -*-

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize, Qt)
from PySide6.QtGui import (QFont, QIcon)
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QPushButton)


class Ui_Tunnel(object):
    def setupUi(self, Tunnel):
        if not Tunnel.objectName():
            Tunnel.setObjectName(u"Tunnel")
        Tunnel.resize(360, 36)
        self.horizontalLayout = QHBoxLayout(Tunnel)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.icon = QLabel(Tunnel)
        self.icon.setObjectName(u"icon")
        self.icon.setMinimumSize(QSize(24, 24))
        self.icon.setMaximumSize(QSize(24, 24))
        self.icon.setScaledContents(True)

        self.horizontalLayout.addWidget(self.icon)

        self.name = QLabel(Tunnel)
        self.name.setObjectName(u"name")
        font = QFont()
        font.setPointSize(11)
        self.name.setFont(font)
        self.name.setIndent(5)

        self.horizontalLayout.addWidget(self.name)

        self.action_tunnel = QPushButton(Tunnel)
        self.action_tunnel.setObjectName(u"action_tunnel")
        self.action_tunnel.setMaximumSize(QSize(32, 16777215))
        self.action_tunnel.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        icon1 = QIcon()
        icon1.addFile(u"icons/open.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_tunnel.setIcon(icon1)
        self.action_tunnel.setIconSize(QSize(20, 20))
        self.action_tunnel.setFlat(True)

        self.horizontalLayout.addWidget(self.action_tunnel)

        self.action_open = QPushButton(Tunnel)
        self.action_open.setObjectName(u"action_open")
        self.action_open.setMaximumSize(QSize(32, 16777215))
        self.action_open.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        icon2 = QIcon()
        icon2.addFile(u"icons/browser.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_open.setIcon(icon2)
        self.action_open.setIconSize(QSize(20, 20))
        self.action_open.setFlat(True)

        self.horizontalLayout.addWidget(self.action_open)

        self.action_settings = QPushButton(Tunnel)
        self.action_settings.setObjectName(u"action_settings")
        self.action_settings.setMaximumSize(QSize(32, 16777215))
        self.action_settings.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        icon3 = QIcon()
        icon3.addFile(u"icons/Settings-4.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_settings.setIcon(icon3)
        self.action_settings.setIconSize(QSize(20, 20))
        self.action_settings.setFlat(True)

        self.horizontalLayout.addWidget(self.action_settings)

        self.delete_ssh = QPushButton(Tunnel)
        self.delete_ssh.setObjectName(u"delete_ssh")
        self.delete_ssh.setMaximumSize(QSize(32, 16777215))
        self.delete_ssh.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        icon4 = QIcon()
        icon4.addFile(u"icons/delete.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.delete_ssh.setIcon(icon4)
        self.delete_ssh.setIconSize(QSize(20, 20))
        self.delete_ssh.setFlat(True)

        self.horizontalLayout.addWidget(self.delete_ssh)

        self.retranslateUi(Tunnel)

        QMetaObject.connectSlotsByName(Tunnel)

    # setupUi

    def retranslateUi(self, Tunnel):
        Tunnel.setWindowTitle(QCoreApplication.translate("Tunnel", u"Form", None))
        self.icon.setText(QCoreApplication.translate("Tunnel", u"icon", None))
        self.name.setText(QCoreApplication.translate("Tunnel", u"TextLabel", None))
        self.action_tunnel.setText("")
        self.action_open.setText("")
        self.delete_ssh.setText("")
        # if QT_CONFIG(shortcut)
        self.delete_ssh.setShortcut(QCoreApplication.translate("Tunnel", u"Ctrl+Z", None))
# endif // QT_CONFIG(shortcut)
# retranslateUi
