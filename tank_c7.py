#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 17:06:51 2019

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

import random

from tank_m7 import Game, Player,PlayerAI, Enemy,EnemyAI, Dir




class ControllerBase:
    def __init__(self):
        self.clients = []
        self.message = None

    def subscribe(self, client):
        self.clients.append(client)

    def refresh(self):
        for client in self.clients:
            client.refresh()

    def info(self):
        return self.message


class TankController(ControllerBase):
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.focus_window = None
        self.game = None
        self.pause = True
        self.w, self.h = 21, 19
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer2 = QTimer()
        self.timer2.setSingleShot(True)
        self.timer2.timeout.connect(self.add_enemy)
        self.players = []
        self.enemies = []
        self.enemies_n = 0 #number of enemies
        self.N_enemies = 8
        self.add_state = 0 #state for adding enemy
                
                                      
    def set_main_window(self, window):
        self.main_window = window

    def set_focus_window(self, window):
        self.focus_window = window
        self.focus_window.setFocus()

    def change_focus(self):
        if self.focus_window:
            self.focus_window.setFocus()

    def change_pause(self):
        self.pause = not self.pause
        self.change_focus()
        self.refresh()

    def set_players(self, players):
        self.players = players
        self.change_focus()

    def new_game(self):
        self.enemies_n = 0
        players = []
        for i, choice in enumerate(self.players):
            x, y = random.choice(self.game.wallman.region[i])
            if choice == 'HUMAIN':
                players.append(Player('Player{}'.format(i + 1), x, y, 3)) # 3 for direction up
            elif choice == 'MACHINE':
                players.append(PlayerAI('Bot Player{}'.format(i + 1), x, y, dire = 3))
            elif choice == 'AUCUN':
                pass
                    
        self.enemies = []
        self.enemies.append(EnemyAI(1,1,2,type3 = 'L'))
        self.enemies.append(EnemyAI(19,1,0, type3 = 'R'))
        self.game = Game(self.w, self.h, players, self.enemies)
        self.change_focus()
        self.pause = False
        self.timer.start(100)

    def get_game(self):
        return self.game
    
    def add_enemy(self):
        if len(self.game.enemies)==1 :
            enemy=self.game.enemies[0]
            if enemy.type3 == 'R':
                self.game.enemies.append(EnemyAI(1,1,2, type3 = 'L'))
            else:
                self.game.enemies.append(EnemyAI(19,1,0, type3 = 'R'))
            self.enemies_n += 1
        if len(self.game.enemies)==0:
            self.game.enemies.append(EnemyAI(1,1,2, type3 = 'L'))
            self.enemies.append(EnemyAI(19,1,0, type3 = 'R'))
            self.enemies_n += 2
        self.add_state = 0
                    
                               
    def on_timer(self):
        
        if not self.pause:
            if len(self.game.enemies)<2 and self.add_state == 0:
                if self.enemies_n<self.N_enemies:
                    self.timer2.start(1500)
                    self.add_state =1
                if self.enemies_n >= self.N_enemies and len(self.game.enemies)==0:
                        self.game.gameover = 'Gameover'
                                
            state = self.game.next()
            if state == 'end':
                self.timer.stop()
            self.refresh()

    def quit(self):
        if self.main_window:
            self.timer.stop()
            self.main_window.close()