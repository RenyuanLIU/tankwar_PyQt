#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 17:25:17 2019

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

from tank_c7 import TankController
from tank_m7 import Dir

s = 100

def dirtolettre(dire):            # direction to lettre, for choosing image 
    swicher={
            Dir.LEFT: 'L', 
            Dir.RIGHT: 'R', 
            Dir.UP: 'U', 
            Dir.DOWN: 'D'}
    return swicher.get(dire,None)




class TankView(QGraphicsView):
    def __init__(self, parent, controller):
        super().__init__(parent)
        controller.set_focus_window(self)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scene = TankScene(self, controller)
        self.setScene(self.scene)

    def resizeEvent(self, event):
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)


class TankScene(QGraphicsScene):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.subscribe(self)
        self.keys = []
        self.keys.append({Qt.Key_W: Dir.UP, Qt.Key_S: Dir.DOWN, Qt.Key_A: Dir.LEFT, Qt.Key_D: Dir.RIGHT})
        self.keys.append({Qt.Key_Up: Dir.UP, Qt.Key_Down: Dir.DOWN, Qt.Key_Left: Dir.LEFT, Qt.Key_Right: Dir.RIGHT})
        self.colors = [QColor(0, 0, 255), QColor(255, 0, 0)]
        self.tanks = []
        self.bricks = []
        self.base = []
        self.bonus = []
        self.bullets=[]
        self.create_scene()
        self.pause= None
        self.gameover = None
        

    def create_scene(self):
        w, h = self.controller.get_game().size
        self.setSceneRect(0, 0, w * s, h * s)
        
        for col in range(w):
            for line in range(h):
                ground = QGraphicsPixmapItem(QPixmap('images/floor.jpg'))
                ground.setScale(1.3)
                ground.setPos(col*s,line*s)
                self.addItem(ground)
                
        for wall in self.controller.get_game().wallman.get_walls():
            x, y = wall.pos.x, wall.pos.y
            wall = QGraphicsPixmapItem(QPixmap('images/wall.png'))
            wall.setScale(1.3)
            wall.setPos(x*s,y*s)
            self.addItem(wall)

        for brick in self.bricks:
            self.removeItem(brick)
        self.bricks = []
        for brick in self.controller.get_game().wallman.get_bricks():
            x, y =brick.pos.x, brick.pos.y              
            brick = QGraphicsPixmapItem(QPixmap('images/brick{}.jpg'.format(brick.value)))
            brick.setScale(1.3)
            brick.setPos(x*s,y*s)
            self.bricks.append(brick) 
            self.addItem(brick) 
            
        for base in self.controller.get_game().wallman.get_base():   
            x, y = base.pos.x, base.pos.y
            base = QGraphicsPixmapItem(QPixmap('images/base.gif'))
            base.setScale(0.9)
            base.setPos(x*s,y*s)
            self.addItem(base)

        
     
    def refresh(self):
        #dessiner les bricks
        for brick in self.bricks:
            self.removeItem(brick)
        self.bricks = []
        for brick in self.controller.get_game().wallman.get_bricks():
            x=brick.pos.x
            y=brick.pos.y
                
            brick = QGraphicsPixmapItem(QPixmap('images/brick{}.jpg'.format(brick.value)))
            brick.setScale(1.3)
            brick.setPos(x*s,y*s)
            self.bricks.append(brick) 
            self.addItem(brick)
        
        # dessiner les tanks
        for tank in self.tanks:
            self.removeItem(tank)
        self.tanks = []
        for i, player in enumerate(self.controller.get_game().players):
            for item in player.tank.get_items():
                x, y = item.pos.x, item.pos.y
                m=QGraphicsPixmapItem(QPixmap('images/tank{}{}.gif'.format(str(i+1),dirtolettre(player.dire))))
                m.setScale(0.9)
                m.setPos(x*s,y*s)
                self.tanks.append(m)
                self.addItem(m)
        for i, enemy in enumerate(self.controller.get_game().enemies):
            for item in enemy.tank.get_items():
                x, y = item.pos.x, item.pos.y
                m=QGraphicsPixmapItem(QPixmap('images/e_tank2{}.png'.format(dirtolettre(enemy.dire))))
                m.setScale(0.9)
                m.setPos(x*s,y*s)
                self.tanks.append(m)
                self.addItem(m) 

        #dessiner les bullets
        for bullet in self.bullets:
            self.removeItem(bullet)
        self.bullets=[]
        for i, player in enumerate(self.controller.get_game().players):
            for bullet in player.bullets:
                x,y = bullet.pos.x, bullet.pos.y
                bullet = QGraphicsPixmapItem(QPixmap('images/bullet{}.png'.format(dirtolettre(bullet.dire))))
                bullet.setScale(1)
                bullet.setPos(x*s,y*s)
                self.bullets.append(bullet)
                self.addItem(bullet)
                #self.balls.append(self.addEllipse(x*s,y*s,s,s,QPen(self.colors[i]), QBrush(self.colors[i])))

        for i, enemy in enumerate(self.controller.get_game().enemies):
            for bullet in enemy.bullets:
                x,y = bullet.pos.x, bullet.pos.y
                ebullet = QGraphicsPixmapItem(QPixmap('images/bullet{}.png'.format(dirtolettre(bullet.dire))))
                ebullet.setScale(1)
                ebullet.setPos(x*s,y*s)
                self.bullets.append(ebullet)
                self.addItem(ebullet) 
            
            
            
        for bo in self.bonus:
            self.removeItem(bo)
        self.bonus = []
        for bo in self.controller.get_game().wallman.get_bonus():
            x=bo.pos.x
            y=bo.pos.y                
            b = QGraphicsPixmapItem(QPixmap('images/bonus{}.gif'.format(bo.value)))
            b.setScale(0.9)
            b.setPos(x*s,y*s)
            self.bonus.append(b) 
            self.addItem(b)            
            
                              
                            
        # afficher pause et gameover le cas échéant
        if self.pause:
            self.removeItem(self.pause)
        bb_scene = self.sceneRect()
        if self.controller.pause:
            
            self.pause = self.addText("PAUSE", QFont("Arial", 80))
            bb_pause = self.pause.sceneBoundingRect()
            self.pause.setPos(bb_scene.width() / 2 - bb_pause.width() / 2, bb_scene.height() / 2 - bb_pause.height() / 2)
        #if self.gameover:
        #    self.removeItem(self.gameover)
        if self.gameover:
            self.removeItem(self.gameover)
        if self.controller.get_game().gameover!= None and self.controller.get_game().gameover!= 'Gameover':
            if self.controller.get_game().gameover == 'Both':
                self.gameover = self.addText("{} Lose".format(str(self.controller.get_game().gameover)), QFont("Arial", 80))
            else:
                self.gameover = self.addText("{} Loses".format(str(self.controller.get_game().gameover)), QFont("Arial", 80))                
            self.gameover.setDefaultTextColor(QColor(255, 0, 0))
            bb_gameover = self.gameover.sceneBoundingRect()
            self.gameover.setPos(bb_scene.width() / 2 - bb_gameover.width() / 2,
                            4*bb_scene.height() / 7 - bb_gameover.height() / 2)
            
        if self.controller.get_game().gameover== 'Gameover':
            if len(self.controller.get_game().players) == 2:
                if self.controller.get_game().players[1].score > self.controller.get_game().players[0].score:
                    self.gameover = self.addText("{}   Wins".format(self.controller.get_game().players[1].name), QFont("Arial", 80))
                if self.controller.get_game().players[1].score < self.controller.get_game().players[0].score:
                    self.gameover = self.addText("{}   Wins".format(self.controller.get_game().players[0].name), QFont("Arial", 80))   
                if self.controller.get_game().players[1].score == self.controller.get_game().players[0].score:
                    self.gameover = self.addText(("Standoff"), QFont("Arial", 80)) 
            elif len(self.controller.get_game().players) == 1:
                self.gameover = self.addText("{}   Wins".format(self.controller.get_game().players[0].name), QFont("Arial", 80))   
            else:
                pass
            self.gameover.setDefaultTextColor(QColor(255, 0, 0))
            bb_gameover = self.gameover.sceneBoundingRect()
            self.gameover.setPos(bb_scene.width() / 2 - bb_gameover.width() / 2,
                             4*bb_scene.height() /7  - bb_gameover.height() / 2)

    def keyPressEvent(self, keyboard):
        key = keyboard.key()
        for i, p in enumerate(self.controller.get_game().players):
            if key in self.keys[i]:
                self.controller.get_game().players[i].tank.change_direction(self.keys[i][key])
                self.controller.get_game().players[i].change_direction(self.keys[i][key])
        if key ==Qt.Key_X:
            self.controller.get_game().players[0].shoot()
        if key == Qt.Key_Space:
            self.controller.get_game().players[1].shoot()
                
        if key == Qt.Key_P:
            self.controller.change_pause()
        if key == Qt.Key_N:
            self.controller.new_game()
        if keyboard.modifiers() & Qt.ControlModifier:
            if key == Qt.Key_Q:
                self.controller.quit()


def test():
    app = QApplication([])
    controller = TankController()
    controller.new_game()
    mainwindow = TankView(None, controller)   
    mainwindow.show()
    app.exec()


if __name__ == '__main__':
    test()

