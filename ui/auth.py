# -*- coding: utf-8 -*-

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt)
from PySide6.QtWidgets import (QCheckBox, QDialogButtonBox, QGridLayout, QHBoxLayout, QLabel)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.setFixedSize(231, 165)
        self.gridLayout_2 = QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.labelOther = QLabel(Dialog)
        self.labelOther.setObjectName(u"labelOther")

        self.horizontalLayout_4.addWidget(self.labelOther)

        self.checkBoxOtherR = QCheckBox(Dialog)
        self.checkBoxOtherR.setObjectName(u"checkBoxOtherR")

        self.horizontalLayout_4.addWidget(self.checkBoxOtherR)

        self.checkBoxOtherW = QCheckBox(Dialog)
        self.checkBoxOtherW.setObjectName(u"checkBoxOtherW")

        self.horizontalLayout_4.addWidget(self.checkBoxOtherW)

        self.checkBoxOtherX = QCheckBox(Dialog)
        self.checkBoxOtherX.setObjectName(u"checkBoxOtherX")

        self.horizontalLayout_4.addWidget(self.checkBoxOtherX)

        self.gridLayout_2.addLayout(self.horizontalLayout_4, 2, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.labelGroup = QLabel(Dialog)
        self.labelGroup.setObjectName(u"labelGroup")

        self.horizontalLayout_3.addWidget(self.labelGroup)

        self.checkBoxGroupR = QCheckBox(Dialog)
        self.checkBoxGroupR.setObjectName(u"checkBoxGroupR")

        self.horizontalLayout_3.addWidget(self.checkBoxGroupR)

        self.checkBoxGroupW = QCheckBox(Dialog)
        self.checkBoxGroupW.setObjectName(u"checkBoxGroupW")

        self.horizontalLayout_3.addWidget(self.checkBoxGroupW)

        self.checkBoxGroupX = QCheckBox(Dialog)
        self.checkBoxGroupX.setObjectName(u"checkBoxGroupX")

        self.horizontalLayout_3.addWidget(self.checkBoxGroupX)

        self.gridLayout_2.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelUser = QLabel(Dialog)
        self.labelUser.setObjectName(u"labelUser")

        self.horizontalLayout.addWidget(self.labelUser)

        self.checkBoxUserR = QCheckBox(Dialog)
        self.checkBoxUserR.setObjectName(u"checkBoxUserR")

        self.horizontalLayout.addWidget(self.checkBoxUserR)

        self.checkBoxUserW = QCheckBox(Dialog)
        self.checkBoxUserW.setObjectName(u"checkBoxUserW")

        self.horizontalLayout.addWidget(self.checkBoxUserW)

        self.checkBoxUserX = QCheckBox(Dialog)
        self.checkBoxUserX.setObjectName(u"checkBoxUserX")

        self.horizontalLayout.addWidget(self.checkBoxUserX)

        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.gridLayout_2.addWidget(self.buttonBox, 3, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"权限设置", None))
        self.labelOther.setText(QCoreApplication.translate("Dialog", u"\u5176\u4ed6", None))
        self.checkBoxOtherR.setText(QCoreApplication.translate("Dialog", u"R", None))
        self.checkBoxOtherW.setText(QCoreApplication.translate("Dialog", u"W", None))
        self.checkBoxOtherX.setText(QCoreApplication.translate("Dialog", u"X", None))
        self.labelGroup.setText(QCoreApplication.translate("Dialog", u"\u5206\u7ec4", None))
        self.checkBoxGroupR.setText(QCoreApplication.translate("Dialog", u"R", None))
        self.checkBoxGroupW.setText(QCoreApplication.translate("Dialog", u"W", None))
        self.checkBoxGroupX.setText(QCoreApplication.translate("Dialog", u"X", None))
        self.labelUser.setText(QCoreApplication.translate("Dialog", u"\u7528\u6237", None))
        self.checkBoxUserR.setText(QCoreApplication.translate("Dialog", u"R", None))
        self.checkBoxUserW.setText(QCoreApplication.translate("Dialog", u"W", None))
        self.checkBoxUserX.setText(QCoreApplication.translate("Dialog", u"X", None))
    # retranslateUi
