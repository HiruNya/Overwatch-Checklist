# Overwatch Checklist

# Import modules
from sys import exit as sys_exit
from yaml import load, dump
from os.path import isfile

# Import Qt5 Modules
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QTabWidget, QMessageBox,
    QListWidget, QListWidgetItem, QPushButton, QFileDialog, QLabel
)


with open("config.yaml", "r") as file:
    path = load(file)["Default Event"]
if path != "" and isfile(path):
    with open(path, "r") as file:
        data = load(file)
else:
    data = {
        "Skins": [],
        "Emotes": [],
        "Sprays": [],
        "Voice Lines": [],
        "Victory Poses": [],
        "Player Icons": [],
        "Highlight Intros": [],
    }


class mainWidget(QWidget): #The main widget to be created
    def __init__(self, total_data, path="", parent=None):
        super(mainWidget, self).__init__(parent)
        self.setWindowTitle("Overwatch Checklist")
        self.setGeometry(100, 100, 600, 400)
        layout = QGridLayout()
        self.setLayout(layout)
        self.data = total_data
        self.original_path = path
        self.path = path

        self.tabs = tabWidget(self.data)
        buttons = buttonWidgets()
        self.lbl = QLabel()
        self.qntity = QLabel()
        self.qntity.setAlignment(Qt.AlignHCenter)
        self.quantity_get()
        txtlayout = QGridLayout()
        txtlayout.addWidget(self.lbl, 0, 0)
        txtlayout.addWidget(self.qntity, 0, 1)

        layout.addWidget(self.tabs, 0, 0)
        layout.addLayout(buttons, 1, 0)
        layout.addLayout(txtlayout, 2, 0)

        buttons.buttons[0].clicked.connect(self.load_data)
        buttons.buttons[1].clicked.connect(self.save_data)
        buttons.buttons[2].clicked.connect(self.clear_check)
        self.tabs.currentChanged.connect(self.quantity_get)

    def load_data(self):
        self.path, ext_type = QFileDialog().getOpenFileName(
            self, "Open an event file", "",
            "YAML Files (*.yaml)"
        )
        if self.path != "":
            with open(self.path, "r") as file:
                self.data = load(file)
            try:
                for i in self.tabs.cosmetic_tabs:
                    i.data = self.data[i.cosmetic_type]
                    i.update_list()
            except KeyError:
                error_message("Incorrect Event File")

    def save_data(self):  # UNDER DEVELOPMENT
        # for i in self.data.keys():
        #     for j in self.data[i]:
        #         j["Obtained"] = 0
        if self.path != "":
            for i in self.tabs.cosmetic_tabs:
                for j in range(i.count()):
                    item = i.item(j)
                    if item.checkState() == Qt.Checked:
                        self.data[i.cosmetic_type][j]["Obtained"] = 1
                    else:
                        self.data[i.cosmetic_type][j]["Obtained"] = 0
            with open(self.path, "w") as file:
                file.write(dump(self.data))
            self.lbl.setText("Success! File saved.")

    def clear_check(self):
        for i in self.tabs.cosmetic_tabs:
            for j in range(i.count()):
                item = i.item(j)
                item.setCheckState(Qt.Unchecked)

    def closeEvent(self, event):
        if self.path != self.original_path:
            with open("config.yaml", "w") as file:
                dump_data = {"Default Event": self.path}
                file.write(dump(dump_data))
        event.accept()

    def quantity_get(self):
        string = "Obtained {0}/{1} - ${2} needed"
        current_tab = self.tabs.cosmetic_tabs[self.tabs.currentIndex()]
        total_item_count = current_tab.count()
        checked_item_count = 0
        money_needed = 0
        for i in range(total_item_count):
            if current_tab.item(i).checkState() == Qt.Checked:
                checked_item_count += 1
            else:
                if current_tab.cosmetic_type != "Player Icons":
                    background = current_tab.item(i).background()
                    if background == Qt.cyan:
                        money_needed += 75
                    elif background == Qt.magenta:
                        money_needed += 750
                    elif background == Qt.yellow:
                        money_needed += 3000
                    else:
                        money_needed += 25
        string = string.format(checked_item_count,
                               total_item_count,
                               money_needed)
        self.qntity.setText(string)


class tabWidget(QTabWidget):
    def __init__(self, total_data, parent=None):
        super(tabWidget, self).__init__(parent)
        self.total_data = total_data
        self.add_tabs()

    def add_tabs(self):
        self.cosmetic_tabs = [
            listWidget(data=self.total_data, cosmetic_type="Skins"),
            listWidget(data=self.total_data, cosmetic_type="Emotes"),
            listWidget(data=self.total_data, cosmetic_type="Sprays"),
            listWidget(data=self.total_data, cosmetic_type="Voice Lines"),
            listWidget(data=self.total_data, cosmetic_type="Victory Poses"),
            listWidget(data=self.total_data, cosmetic_type="Player Icons"),
            listWidget(data=self.total_data, cosmetic_type="Highlight Intros"),
        ]
        for i in self.cosmetic_tabs:
            self.addTab(i, i.cosmetic_type)


class listWidget(QListWidget):
    def __init__(self, data, cosmetic_type, parent=None):
        super(listWidget, self).__init__(parent)
        self.cosmetic_type = cosmetic_type
        self.data = data[cosmetic_type]
        self.update_list()

    def update_list(self):
        self.clear()
        for i in self.data:
            item = QListWidgetItem(i["Name"])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            rarity = [Qt.white, Qt.cyan, Qt.magenta, Qt.yellow]
            if i["Obtained"] == 0:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)
            try:
                item.setBackground(rarity[i["Rarity"]])
            except KeyError:
                error_message("Error: Does not contain 'Rarity' key")
            self.addItem(item)


class buttonWidgets(QGridLayout):
    def __init__(self, parent=None):
        super(buttonWidgets, self).__init__(parent)
        self.buttons = [
            QPushButton(text="Load Event"),
            QPushButton(text="Save Event"),
            QPushButton(text="Clear Event"),
        ]
        for i in range(len(self.buttons)):
            self.addWidget(self.buttons[i], 0, i)


def error_message(text, title="Error"):
    msg = QMessageBox()
    msg.setText(text)
    msg.setWindowTitle(title)
    msg.exec_()

app = QApplication([])
main_wid = mainWidget(total_data=data, path=path)
main_wid.show()
sys_exit(app.exec_())
