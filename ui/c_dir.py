# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'c_dir.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication,
                            QMetaObject, QRect)
from PySide6.QtWidgets import (QLineEdit)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(369, 124)
        self.lineEdit = QLineEdit(Dialog)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(60, 30, 231, 41))

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.lineEdit.setPlaceholderText(
            QCoreApplication.translate("Dialog", u"\u8bf7\u8f93\u5165\u6587\u4ef6\u5939\u540d\u79f0", None))
    # retranslateUi
