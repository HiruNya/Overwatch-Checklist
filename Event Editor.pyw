# Import Modules
from sys import exit as sys_exit
from yaml import load, dump

# PyQt5 Modules
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QFileDialog, QLabel,
    QTabWidget, QListWidget, QListWidgetItem, QMessageBox, QLineEdit,
    QComboBox
)

class mainWidget(QWidget):
    def __init__(self, parent=None):
        super(mainWidget, self).__init__(parent)
        self.setWindowTitle("Event Editor")
        self.path = ""
        layout = QGridLayout()
        layout.setColumnStretch(0, 9)
        layout.setColumnStretch(1, 1)
        self.setGeometry(100, 100, 730, 400)
        self.setLayout(layout)
        self.data = {
            "Skins": [],
            "Emotes": [],
            "Sprays": [],
            "Voice Lines": [],
            "Victory Poses": [],
            "Player Icons": [],
            "Highlight Intros": [],
        }

        self.title_label = QLabel(text="New Event")
        self.title_label.setWordWrap(True)
        self.tabs = tabWidget(self.data)
        self.buttons = Buttons()
        self.edits = editTools()

        layout.addWidget(self.title_label, 0, 0)
        layout.addWidget(self.tabs, 1, 0)
        layout.addLayout(self.buttons, 2, 0)
        layout.addLayout(self.edits, 0, 1, 3, 1)

        self.connect()

    def connect(self):
        self.buttons.buttons[1].clicked.connect(self.load_data)
        self.buttons.buttons[0].clicked.connect(self.save_data)
        self.edits.buttons[0].clicked.connect(self.add_item)
        self.edits.buttons[1].clicked.connect(self.edit_item)
        self.edits.buttons[2].clicked.connect(self.delete_item)
        for i in self.tabs.tabs:
            i.itemClicked.connect(self.update_edit_info)

    def populate_data(self):
        data = {}
        for i in self.tabs.tabs:
            cos_type = i.cosmetic_type
            data[cos_type] = []
            for j in range(i.count()):
                item = i.item(j)
                item_data = {
                    "Name": item.text(),
                    "Obtained": 0,
                    "Rarity": item.rarity,
                }
                # if item.background() == Qt.cyan:
                #     item_data["Rarity"] = 1
                # elif item.background() == Qt.magenta:
                #     item_data["Rarity"] = 2
                # elif item.background() == Qt.yellow:
                #     item_data["Rarity"] = 3
                # else:
                #     item_data["Rarity"] = 0
                data[cos_type].append(item_data)
        self.data = data

    def update_edit_info(self, item):
        self.edits.name.setText(item.text())
        self.edits.cosmetic_type.setCurrentIndex(item.get_cosmetic_type_index())
        self.edits.rarity.setCurrentIndex(item.rarity)

    def load_data(self):
        self.path, ext = QFileDialog.getOpenFileName(
            self, "Open an event file", "",
            "YAML Files (*.yaml)"
        )
        if self.path != "":
            with open(self.path, "r") as file:
                try:
                    self.data = load(file)
                    for i in self.tabs.tabs:
                        i.update_list(self.data)
                except:
                    error_message("Incorrect Event File")
                    return 0
            self.title_label.setText(self.path)

    def save_data(self):
        self.populate_data()
        if self.path == "":
            self.path, ext = QFileDialog.getSaveFileName(
                self, "Save an event file", "",
                "YAML Files (*.yaml)"
            )
            if self.path == "":
                return 0
            self.title_label.setText(self.path)
        with open(self.path, "w") as file:
            file.write(dump(self.data))

    def add_item(self):
        index = self.edits.cosmetic_type.currentIndex()
        item = listItem(self.tabs.tabs[index].cosmetic_type, self.edits.rarity.currentIndex(), self.edits.name.text())
        self.tabs.tabs[index].addItem(item)

    def edit_item(self):
        tab = self.tabs.currentWidget()
        item = tab.currentItem()
        new_name = self.edits.name.text()
        new_rarity = self.edits.rarity.currentIndex()
        new_cos_type = self.tabs.tabs[self.edits.cosmetic_type.currentIndex()].cosmetic_type
        if item.cosmetic_type != new_cos_type:
            error_message("Cannot edit an item from another tab\r\nPlease delete this item then add it to the other one")
            return 0
        else:
            item.setText(new_name)
            item.update_rarity(new_rarity)


    def delete_item(self):
        tab = self.tabs.currentWidget()
        response = tab.takeItem(tab.currentRow())


class tabWidget(QTabWidget):
    def __init__(self, data, parent=None):
        super(tabWidget, self).__init__(parent)

        self.tabs = [
            listWidget("Skins", data),
            listWidget("Emotes", data),
            listWidget("Sprays", data),
            listWidget("Voice Lines", data),
            listWidget("Victory Poses", data),
            listWidget("Player Icons", data),
            listWidget("Highlight Intros", data),
        ]

        for i in self.tabs:
            self.addTab(i, i.cosmetic_type)

class listWidget(QListWidget):
    def __init__(self, cosmetic_type, data, parent=None):
        super(listWidget, self).__init__(parent)
        self.cosmetic_type = cosmetic_type
        self.update_list(data)
        self.setGeometry(100, 100, 50, 50)

    def update_list(self, data):
        self.clear()
        for i in data[self.cosmetic_type]:
            try:
                item = listItem(self.cosmetic_type, i["Rarity"], i["Name"])
            except KeyError:
                error_message("Error, incorrect event file")
            self.addItem(item)

class listItem(QListWidgetItem):
    def __init__(self, cosmetic_type, rarity, parent=None):
        super(listItem, self).__init__(parent)
        self.cosmetic_type = cosmetic_type
        self.rarity = None
        self.update_rarity(rarity)

    def get_cosmetic_type_index(self):
        types = [
            "Skins",
            "Emotes",
            "Sprays",
            "Voice Lines",
            "Victory Poses",
            "Player Icons",
            "Highlight Intros",
        ]
        for i in range(len(types)):
            if self.cosmetic_type == types[i]:
                return i

    def update_rarity(self, index):
        colours = [Qt.white, Qt.cyan, Qt.magenta, Qt.yellow]
        self.rarity = index
        self.setBackground(colours[self.rarity])
        del colours



class Buttons(QGridLayout):
    def __init__(self, parent=None):
        super(Buttons, self).__init__(parent)

        self.buttons = [
            QPushButton(text="Save Event"),
            QPushButton(text="Load Event"),
            #QPushButton(text="New Event"),
        ]

        for i in range(len(self.buttons)):
            self.addWidget(self.buttons[i], 0, i)

class editTools(QGridLayout):
    def __init__(self, parent=None):
        super(editTools, self).__init__(parent)

        self.name = QLineEdit()

        self.cosmetic_type = QComboBox()
        self.cosmetic_type.addItem("Skins")
        self.cosmetic_type.addItem("Emotes")
        self.cosmetic_type.addItem("Sprays")
        self.cosmetic_type.addItem("Voice Lines")
        self.cosmetic_type.addItem("Victory Poses")
        self.cosmetic_type.addItem("Player Icons")
        self.cosmetic_type.addItem("Highlight Intros")

        self.rarity = QComboBox()
        self.rarity.addItem("Normal")
        self.rarity.addItem("Rare")
        self.rarity.addItem("Epic")
        self.rarity.addItem("Legendary")

        self.buttons = [
            QPushButton(text="Add"),
            QPushButton(text="Edit"),
            QPushButton(text="Delete")
        ]

        self.addWidget(QLabel(text="Name: "), 0, 0)
        self.addWidget(self.name, 0, 1)
        self.addWidget(QLabel(text="Type: "), 1, 0)
        self.addWidget(self.cosmetic_type, 1, 1)
        self.addWidget(QLabel(text="Rarity: "), 2, 0)
        self.addWidget(self.rarity, 2, 1)
        self.addWidget(self.buttons[0], 3, 0)
        self.addWidget(self.buttons[1], 3, 1)
        self.addWidget(self.buttons[2], 4, 0, 1, 2)


def error_message(text, title="Error"):
    msg = QMessageBox()
    msg.setText(text)
    msg.setWindowTitle(title)
    msg.exec_()

app = QApplication([])
main_wid = mainWidget()
main_wid.show()
sys_exit(app.exec_())
