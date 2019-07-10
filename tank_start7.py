# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 18:08:50 2019

@author: Renyuan LIU, Sheng ZHOU
"""

try:
   # Qt5
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtMultimedia import *
except ImportError:
    try:
        # Qt4
        from PyQt4.QtCore import *
        from PyQt4.QtGui import *
    except ImportError:
        print('Merci d\'installer PyQt5 ou PyQt4.')
        exit()

from tank_v7 import *


class ParametersWindow(QWidget):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.subscribe(self)

        types = ['HUMAIN', 'MACHINE', 'AUCUN']
        self.combo_player1 = QComboBox()
        self.combo_player2 = QComboBox()
        for item in types:
            self.combo_player1.addItem(item)
            self.combo_player2.addItem(item)
        self.combo_player1.currentTextChanged.connect(self.on_change_player)
        self.combo_player2.currentTextChanged.connect(self.on_change_player)
        self.combo_player1.setCurrentText('MACHINE')
        self.combo_player2.setCurrentText('MACHINE')
        layout_joueurs = QFormLayout()
        layout_joueurs.addRow("Player 1", self.combo_player1)
        layout_joueurs.addRow("Player 2", self.combo_player2)
        groupbox_joueurs = QGroupBox("Players")
        groupbox_joueurs.setLayout(layout_joueurs)
        button_newgame = QPushButton("New game")
        button_newgame.clicked.connect(self.on_new_game)
        self.button_pause = QPushButton("Pause")
        self.button_pause.clicked.connect(self.on_pause)
        button_quit = QPushButton("Quit")
        button_quit.clicked.connect(self.on_quit)
        layout_actions = QVBoxLayout()
        layout_actions.addWidget(button_newgame)
        layout_actions.addWidget(self.button_pause)
        layout_actions.addWidget(button_quit)
        groupbox_actions = QGroupBox("Actions")
        groupbox_actions.setLayout(layout_actions)

        label_touches_j1 = QLabel("Movement Player 1 : W A S D")
        label_touches_j2 = QLabel("Movement Player 2 : keyboard arrows")
        label_touches_j1_mb = QLabel("Fire Player 1: X")
        label_touches_j2_mb = QLabel('Fire Player 2: Space')
        label_touches_pause = QLabel("Pause : P")
        label_touches_new = QLabel("New game : N")
        label_touches_quit = QLabel("Quit : Ctrl + Q")
        layout_touches = QVBoxLayout()
        layout_touches.addWidget(label_touches_j1)
        layout_touches.addWidget(label_touches_j2)
        layout_touches.addWidget(label_touches_j1_mb)
        layout_touches.addWidget(label_touches_j2_mb)
        layout_touches.addWidget(label_touches_new)
        layout_touches.addWidget(label_touches_pause)
        layout_touches.addWidget(label_touches_quit)
        groupbox_touches = QGroupBox("Keys")
        groupbox_touches.setLayout(layout_touches)
        
        self.label_numb_j1 = QLabel('Player 1\'s reloading time is 800 ms ')
        self.label_power_j1=QLabel('Player 1 Score: 0')
        self.label_numb_j2 = QLabel('Player 2 \'s reloading time is 800 ms ')
        self.label_power_j2=QLabel('Player 2 Score: 0')
        layout_states=QVBoxLayout()
        layout_states.addWidget(self.label_numb_j1)
        layout_states.addWidget(self.label_power_j1)
        layout_states.addWidget(self.label_numb_j2)
        layout_states.addWidget(self.label_power_j2)
        groupbox_states = QGroupBox('states')
        groupbox_states.setLayout(layout_states)
        layout = QVBoxLayout()
        layout.addWidget(groupbox_joueurs)
        layout.addWidget(groupbox_states)
        layout.addWidget(groupbox_touches)
        layout.addWidget(groupbox_actions)
        layout.addStretch()

        self.setLayout(layout)

    def on_change_player(self):
        choix_player1 = self.combo_player1.currentText()
        choix_player2 = self.combo_player2.currentText()
        self.controller.set_players([choix_player1, choix_player2])

    def on_new_game(self):
        self.controller.new_game()

    def on_pause(self):
        self.controller.change_pause()

    def on_quit(self):
        self.controller.quit()

    def refresh(self):        
        if len(self.controller.get_game().players) ==2:
            self.label_numb_j1.setText('Player 1\'s reloading time is {} ms'.format(self.controller.get_game().players[0].interval ))
            self.label_power_j1.setText('Player 1 Score: {}'.format(self.controller.get_game().players[0].score))
            self.label_numb_j2.setText('Player 2\'s reloading time is {} ms'.format(self.controller.get_game().players[1].interval ))
            self.label_power_j2.setText('Player 2 Score: {}'.format(self.controller.get_game().players[1].score))
        elif  len(self.controller.get_game().players) == 1:
            self.label_numb_j1.setText('Player 1\'s reloading time is {} ms'.format(self.controller.get_game().players[0].interval ))
            self.label_power_j1.setText('Player 1 Score: {}'.format(self.controller.get_game().players[0].score))
            self.label_numb_j2.setText('Player 2\'s reloading time is 800 ms')
            self.label_power_j2.setText('Player 2 Score: 0')
        elif  len(self.controller.get_game().players) == 0:
            pass


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.controller.subscribe(self)
        self.controller.set_main_window(self)
        self.setWindowTitle("Tankwar Zhou et Liu")
        self.create_menu()
        self.create_statusbar()
        self.create_central_widget()

    def create_menu(self):
        pass

    def create_toolbar(self):
        toolbar = QToolBar("toolbar", self)
        toolbar.addAction("new game")
        self.addToolBar(toolbar)

    def create_statusbar(self):
        self.statusBar().showMessage("Ready to play !")

    def create_central_widget(self):
        param = ParametersWindow(self, self.controller)
        view = TankView(self, self.controller)
        widget_central = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(param, 2)
        layout.addWidget(view, 0)
        widget_central.setLayout(layout)
        self.setCentralWidget(widget_central)

    def refresh(self):
        pass


def main():
    app = QApplication([])
    controller = TankController()
    controller.new_game()
    controller.change_pause()
    mainwindow = MainWindow(controller)
    mainwindow.show()
    app.exec()
    
       

if __name__ == '__main__':
    main()