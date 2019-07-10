# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 03:11:08 2019

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
from copy import *
import random
import math
import numpy as np

class Dir:
    LEFT = 0
    DOWN = 1
    RIGHT = 2
    UP = 3
    STAY = 4


dep = {Dir.LEFT: (-1, 0), Dir.RIGHT: (1, 0), Dir.UP: (0, -1), Dir.DOWN: (0, 1), Dir.STAY: (0, 0)}
dep_inv = {(-1,0):Dir.LEFT,(1, 0):Dir.RIGHT, (0,-1):Dir.UP,(0,1):Dir.DOWN, (0,0):Dir.STAY}
back_dep = {Dir.LEFT: (1, 0), Dir.RIGHT: (-1, 0), Dir.UP: (0, 1), Dir.DOWN: (0, -1), Dir.STAY: (0, 0)}

    

global Type_ALL 
Type_ALL = ['bullet', 'wall', 'brick', 'dangerous']


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def translate_inplace(self, vec):
        dx, dy = vec
        self.x += dx
        self.y += dy

    def translate_outofplace(self, vec):
        p = Position(self.x, self.y)
        p.translate_inplace(vec)
        return p

    def distance(self, pos):
        return (pos.x - self.x) ** 2 + (pos.y - self.y) ** 2

    def __eq__(self, pos):
        if pos.x == self.x and pos.y == self.y:
            return True
        return False
    
       
    
class Game:
    def __init__(self, w, h, players, enemies):
        self.size = (w, h)
        self.players = players
        self.enemies = enemies
        self.wallman = WallManager(w, h)
        self.Break_pos = []
        self.timer1=QTimer()     #time for creating bonus
        self.timer1.setSingleShot(True)
        self.timer1.timeout.connect(self.wallman.create_bonus)
        self.timer2=QTimer()     #time for clock
        self.timer2.setSingleShot(True)
        self.timer2.timeout.connect(self.enemy_move)          

        self.gameover = None

    def get_board(self):
        board = []
        board += self.wallman.get_bricks()
        board += self.wallman.get_walls()
        board += self.wallman.get_base()
        board += self.wallman.get_bonus()
        for player in self.players:
            board += player.tank.get_items()
            for bullet in player.bullets:
                board += bullet.get_items()
        for enemy in self.enemies:
            board += enemy.tank.get_items() 
            for bullet in enemy.bullets:
                board += bullet.get_items()
        return board    
    
    def enemy_move(self):
        for enemy in self.enemies:
            enemy.state = True
    
    def next(self):
        if self.wallman.bonus_state == 1:
            self.timer1.start(6000)  # waiting for bonus
            self.wallman.bonus_state = 0
        
        for player in self.players:
            board = self.get_board()
            if (player.name == 'Player1' or player.name == 'Player2'):
                artefact1 = player.tank.move(board) 
                if player.tank.shoot ==True: 
                    player.shoot()
                    player.tank.shoot =False 
            else:
                artefact1 = player.move(board)
                player.shoot()
            for bullet in player.bullets:                    
                Break_Pos = bullet.move(board)    #Break brick or tank or bullet
                if bullet.state == False:
                    player.bullets.remove(bullet)
                for bbp in Break_Pos:
                    for item in self.wallman.bricks:
                        if item.type=='brick':
                            if item.pos==bbp:
                                self.wallman.delete_brick(item)
                    for item in self.wallman.base:
                        if item.type=='base':
                            if item.pos==bbp:
                                player.state='ko'  
                    for enemy in self.enemies:
                        if enemy.tank.pos==bbp:
                            self.enemies.remove(enemy)
                            player.score +=1
                    

            if artefact1.type == 'bullet' and artefact1.type2 == 2: #shot by enemies
                player.state='ko'             
            if artefact1.type == 'clock':
                self.wallman.remove_bonus()
                for enemy in self.enemies:
                    enemy.state = False
                    self.timer2.start(5000)   #enemies can't move in 5s
                player.score += 1
            if artefact1.type == 'bomb':
                self.wallman.remove_bonus() 
                if len(self.enemies) == 2:
                    self.enemies.pop(1)
                    self.enemies.pop(0)
                if len(self.enemies) == 1:
                    self.enemies.pop(0)
                player.score += 2                             
            if artefact1.type == 'star':
                self.wallman.remove_bonus() 
                player.score +=1
                if player.interval == 800:
                    player.interval = 600
                elif player.interval == 600:
                    player.interval = 400   

                    
        for enemy in self.enemies:
            if enemy.state == True:
                board = self.get_board()
                enemy.shoot()  
            for bullet in enemy.bullets:
                Break_Pos = bullet.move(board)    #Break brick or tank or bullet
                if bullet.state == False:
                    enemy.bullets.remove(bullet)
                for bbp in Break_Pos:
                    for item in self.wallman.bricks:
                        if item.type=='brick':
                            if item.pos==bbp:
                                self.wallman.delete_brick(item)
                    for item in self.wallman.base:
                        if item.type=='base':
                            if item.pos==bbp:
                                self.gameover = 'Both'  
                    for player in self.players:
                        if player.tank.pos==bbp:
                            player.state='ko'

            if enemy.state == True:
                if enemy.enemy_move == 1:
                    enemy.move(board)    
                    enemy.enemy_move = 0
                else:
                    enemy.enemy_move += 1
 
            
        
        for player in self.players:
            if player.state == 'ko':
                self.gameover = player.name
                return 'end'
        if self.gameover != None:
            return 'end'
        return 'next'   

           
    
        
        

class Player:
    def __init__(self, name, x, y, dire, interval = 800, power=1):
        self.name = name
        self.tank = Tank(x, y, dire)
        self.dire = dire
        
        self.bullets = []
        self.interval = interval # reloading time  1000 = 1s
        self.reloading = 1   #reloading state, 1 for ready to shoot , 0 for reloading  
        self.timer=QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.reload)
        
        self.power=power  
        self.score = 0
        self.state = 'ok'        
    
    def reload(self):
        self.reloading = 1
    
    def shoot(self):
        if self.reloading == 1:
            self.bullets.append(Bullet(self.tank.pos.x,self.tank.pos.y,self.dire,self.power))
            self.reloading = 0
            self.timer.start(self.interval)
    
    def change_direction(self, direction):
        self.dire = direction
        
    
class Enemy:
    def __init__(self, x, y, dire, interval = 1500, power=1 , type3 = 'L'): # type3='L' or 'R'
        self.tank = Tank(x, y, dire,type2 = 2, shoot = True)
        self.dire = dire
        self.type3 = type3
        self.bullets = []
        self.interval = interval # reloading time  1000 = 1s
        self.reloading = 1   #reloading state, 1 for ready to shoot , 0 for reloading  
        self.timer=QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.reload)        
        self.power=power        
        self.state = True # Used to judge whether it can move        
        self.enemy_move = 0 #used in game.next()  0,1,2 stay, 3 move
        
        
    def reload(self):
        self.reloading = 1
    
    def shoot(self):
        if self.reloading == 1:
            self.bullets.append(Bullet(self.tank.pos.x,self.tank.pos.y,self.dire,self.power, type2 = 2))
            self.reloading = 0
            self.timer.start(self.interval)
    
    def change_direction(self, direction):
        self.dire = direction


class Artefact:
    def __init__(self):
        self.type = None
        self.pos = Position(0, 0)
        
        
class BulletItem(Artefact):
    def __init__(self, x, y, dire, power, type2 = 1): #type2 = 1 for bullets from players and type2 = 2 for those from enemies
        self.type='bullet'
        self.type2 = type2
        self.pos=Position(x, y)
        self.dire = dire
        self.power=power        
        
class TankItem(Artefact):
    def __init__(self, x, y, dire, type2 = 1):
        self.type='tank'
        self.type2 = type2
        self.pos=Position(x, y)
        self.dire = dire

class Dangerous(Artefact):
    def __init__(self,x,y):
        self.type = 'dangerous'
        self.pos = Position(x,y)        

class Tank:
    def __init__(self, x, y, dire, type2 = 1,shoot = False):
        self.pos = Position(x, y)
        self.dire = dire        #for pose
        self.direction = Dir.STAY     #for moving
        self.type2 =type2
        self.items = [TankItem(self.pos.x, self.pos.y, self.dire, self.type2)]
        self.length = 1
        self.shoot =shoot

    
    def move(self, board):
        if board:
            itempos=[]
            for item in board:
                if item.type=='wall' or item.type=='brick' or item.type == 'tank' or item.type == 'base':  #can not move through wall and brick and tank
                    itempos.append(item.pos)
            if self.pos.translate_outofplace(dep[self.direction]) not in itempos: 
                self.pos.translate_inplace(dep[self.direction])  
                self.items.append(TankItem(self.pos.x, self.pos.y, self.direction, self.type2))
                while len(self.items) > self.length:  
                    del self.items[0]
                self.direction=Dir.STAY
        # TODO: enlever le test de collision de cette classe (à faire dans game)
        if board:
            for item in board:
                if item.pos == self.pos and item.type != 'tank':
                    return item 
        return Artefact()
    
    def change_direction(self, direction):
        self.direction = direction
        self.dire = direction

    def get_items(self):
        return self.items

    def __repr__(self):
        x, y = self.pos
        return "x={}, y={}".format(x, y)



       
class Bullet:
    def __init__(self, x, y, dire, power, type2=1): #type2 =1 from player  2 from enemy
        self.pos = Position(x, y)
        self.power = power
        self.dire = dire
        self.type2 = type2
        self.items = [BulletItem(self.pos.x, self.pos.y, self.dire, self.power, self.type2)]
        self.state=True
                
    def move(self, board):
        if board:
            tankpos=[]  
            wallpos=[]
            brickpos=[]
            basepos = []
            bulletpos = []
            Break_pos=[]

            for item in board:
                if item.type=='wall':  #can not move through wall and brick
                    wallpos.append(item.pos)
                if item.type=='brick':
                    brickpos.append(item.pos) 
                if item.type=='base':
                    basepos.append(item.pos)
                if item.type=='tank':
                    tankpos.append(item.pos)
                if item.type=='bullet':
                    if self.type2 !=item.type2:
                        bulletpos.append(item.pos)
        
                            
            if self.pos.translate_outofplace(dep[self.dire]) in tankpos: #tank
                self.explosion()
                Break_pos.append(self.pos.translate_outofplace(dep[self.dire]))
            
            if self.pos.translate_outofplace(dep[self.dire]) in basepos: #base
                self.explosion()
                Break_pos.append(self.pos.translate_outofplace(dep[self.dire]))                
            if self.pos.translate_outofplace(dep[self.dire]) in wallpos: 
                self.explosion()
            if self.pos.translate_outofplace(dep[self.dire]) in brickpos:
                self.explosion()
                Break_pos.append(self.pos.translate_outofplace(dep[self.dire]))
            else:
                self.pos.translate_inplace(dep[self.dire]) 
                self.items.append(BulletItem(self.pos.x, self.pos.y, self.dire, self.power, self.type2))
                while len(self.items) > 1:
                    del self.items[0]
        return Break_pos
                
    def explosion(self):
        for item in self.items:
            self.items.remove(item)        
        self.state=False
            
    def get_items(self):
        return self.items

    def __repr__(self):
        x, y = self.pos
        return "x={}, y={}".format(x, y)
    


class BaseItem(Artefact):
    def __init__(self, x, y):
        self.type = 'base'
        self.pos = Position(x, y) 

class BrickItem(Artefact):
    def __init__(self, x, y):
        self.type = 'brick'
        self.pos = Position(x, y)
        self.value = 2 # time can be shot

class WallItem(Artefact):
    def __init__(self, x, y):
        self.type = 'wall'
        self.pos = Position(x, y)

class ClockItem(Artefact):
    def __init__(self, x, y):
        self.type = 'clock'
        self.pos = Position(x, y)
        self.value = 0           

class BombItem(Artefact):
    def __init__(self, x, y):
        self.type = 'bomb'
        self.pos = Position(x, y)
        self.value = 1
        
class StarItem(Artefact):
    def __init__(self, x, y):
        self.type = 'star'
        self.pos = Position(x, y)
        self.value = 2


class WallManager():
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.walls = []
        self.bricks = []
        self.create_border()
        self.base = []
        self.region = []
        
        self.load_map()
        self.bonus = []
        self.bonus_list = []
        self.bonus_state = 1 # 1:set bonus     0:wait
        
        self.timer=QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.remove_bonus)
        
        
    def create_border(self):
        self.walls += [WallItem(col, 0) for col in range(self.w)]
        self.walls += [WallItem(col, self.h - 1) for col in range(self.w)]
        self.walls += [WallItem(0, line) for line in range(self.h)]
        self.walls += [WallItem(self.w - 1, line) for line in range(self.h)]
        
        
    def load_map(self):
#        self.region.append([(10,1)])
        self.region.append([(2,17)]) #initialise players' lacations
        self.region.append([(18,17)])
        
        self.base +=[BaseItem(10,17)]
        self.walls +=[WallItem(1,9),WallItem(2,9),WallItem(18,9),WallItem(19,9),WallItem(10,9)]
        self.walls +=[WallItem(9,9),WallItem(11,9), WallItem(1,3), WallItem(19,3), WallItem(2,3),WallItem(18,3)]
        self.walls +=[WallItem(col,15) for col in [1,2,18,19]]
        self.bricks +=[BrickItem(col,3) for col in [5,15]]
        self.bricks +=[BrickItem(col,line) for line in np.arange(4,7,1) for col in [1,2,5,8,9,11,12,15,18,19]]
        self.bricks +=[BrickItem(col,line) for col in [3,4,6,8,12,14,16,17] for line in [8,9]]
        self.bricks +=[BrickItem(col,line) for col in [1,2,3,6,7,13,14,17,18,19] for line in [12,13]]
        self.bricks +=[BrickItem(col,15) for col in [6,7,13,14]]
        self.bricks +=[BrickItem(col,line) for col in [9,10,11] for line in [13,14,12]]
        self.bricks +=[BrickItem(9,17),BrickItem(11,17),BrickItem(9,16),BrickItem(11,16),BrickItem(10,16)]
                
        
    def delete_brick(self, artefact):
        if artefact.value > 1:
            artefact.value -= 1
        else:
            self.bricks.remove(artefact)
    
    

    def create_bonus(self):

#        i = random.choice(np.arange(1,17,1))
#        j = random.choice([4,5,6,7,11])
        self.bonus_list = [(col,9) for col in [5,7,13,15]]
        self.bonus_list = [(col,line) for col in [1,2,5,7,9,10,11,13,15,18,19] for line in [7,8]]
        self.bonus_list += [(col,line) for col in [4,5,8,12,15,16] for line in [12,13]]
        self.bonus_list += [(col,14) for col in np.arange(1,8,1)]
        self.bonus_list += [(col,14) for col in np.arange(12,19,1)]
        i,j = random.choice(self.bonus_list)
#        i,j = 13,9 
        bonus_type = random.choice(range(3)) #       0:clock, 1:bomb, 2:star 
#        bonus_type = 2   #test
        if bonus_type == 0:
            self.bonus +=[ClockItem(i,j)]
        elif bonus_type == 1:
            self.bonus +=[BombItem(i,j)]
        elif bonus_type == 2:
            self.bonus +=[StarItem(i,j)]    
        self.timer.start(8000)
        
    def remove_bonus(self):
        for b in self.bonus:
            self.bonus.remove(b)
        self.bonus_state = 1

    
    def get_bonus(self):
        return self.bonus
        
    def get_walls(self):
        return self.walls
    
    def get_bricks(self):
        return self.bricks  
    
    def get_base(self):
        return self.base




#############################################################               A I

class PlayerAI(Player):
    def __init__(self, name, x, y, dire, interval = 1000, power=1):
        super().__init__(name, x, y, dire )

   
    def move(self, board):
        self.change_direction(board)
        return self.tank.move(board)
        
    def change_direction(self,board):
        dangerous_position=[]
        for item in board:
            if (item.type == 'bullet' and item.type2 == 2) or (item.type == 'tank' and item.type2 == 2) :
                dangerous_position += [item.pos]
                dangerous_position += [item.pos.translate_outofplace(dep[item.dire])]
                dangerous_position += [item.pos.translate_outofplace(dep[item.dire]).translate_outofplace(dep[item.dire])]
        for item in dangerous_position:
            board.append(Dangerous(item.x,item.y))
                
        for item in board:
            if item.type == 'bullet' and item.type2 == 1:
                board.remove(item)
            
        if self.tank.pos in dangerous_position: #avoid dangerous
            directions = [self.dire, (self.dire + 1) % 4, (self.dire + 2) % 4, (self.dire + 3) % 4]
            for direction in directions:
                pos = self.tank.pos.translate_outofplace(dep[direction])
                collisions = [item.pos == pos for item in board]
                if True not in collisions:
                    break
            self.dire = direction
            self.tank.direction = self.dire
            self.tank.dire =self.dire
            return

                  
        for item in board:        #find bonus
            if (item.type=='clock' or item.type =='bomb' or item.type == 'star') :
                AS_accessory = Find_Path(self.tank.pos.x,self.tank.pos.y,item.pos.x,item.pos.y,board,Type_ALL)
                AS_accessory.find_path()
                if AS_accessory.path:
                    dirx=AS_accessory.path[-2][0]
                    diry=AS_accessory.path[-2][1]
                    self.dire =dep_inv[(dirx-self.tank.pos.x,diry-self.tank.pos.y)]
                    self.tank.direction = self.dire
                    self.tank.dire =self.dire
                    return
                    
        enemy_tank = self.nearest_enemy(board)  #follow the enemies #enemy_tank get the enemy tank item
        if enemy_tank:            
            enemy_back = enemy_tank.pos.translate_outofplace(back_dep[enemy_tank.dire]).translate_outofplace(back_dep[enemy_tank.dire]) #back of enemy
            if (((self.tank.pos.x,self.tank.pos.y) != (enemy_back.x,enemy_back.y)) and 
                ((self.tank.pos.x,self.tank.pos.y) != (enemy_back.translate_outofplace(dep[enemy_tank.dire]).x,enemy_back.translate_outofplace(dep[enemy_tank.dire]).y))):
                AS_accessory = Find_Path(self.tank.pos.x,self.tank.pos.y,enemy_back.x,enemy_back.y,board,Type_ALL)
                AS_accessory.find_path()
                if AS_accessory.path:
                    dirx=AS_accessory.path[-2][0]
                    diry=AS_accessory.path[-2][1]
                    self.dire =dep_inv[(dirx-self.tank.pos.x,diry-self.tank.pos.y)]
                    self.tank.direction = self.dire
                    self.tank.dire =self.dire
                    return   
            else:                
                if self.dire != enemy_tank.dire:
                    self.dire = enemy_tank.dire
                    self.tank.direction = self.dire
                    self.tank.dire =self.dire
                    return
                else:
                    return

        if self.name == 'Bot Player1':    # normal state, back to (4,11) or (16,11) and direction UP
            if ((self.tank.pos.x,self.tank.pos.y) != (4,11) and (self.tank.pos.x,self.tank.pos.y) != (4,12))or ((self.tank.pos.x,self.tank.pos.y) == (4,11) and self.dire !=Dir.UP ):  
                AS_accessory = Find_Path(self.tank.pos.x,self.tank.pos.y,4,12,board,Type_ALL)  # left player back to (4,12)
                AS_accessory.find_path()
                if AS_accessory.path:
                    dirx=AS_accessory.path[-2][0]
                    diry=AS_accessory.path[-2][1]
                    self.dire =dep_inv[(dirx-self.tank.pos.x,diry-self.tank.pos.y)]
                    self.tank.direction = self.dire
                    self.tank.dire =self.dire
                    return     
            elif (self.tank.pos.x,self.tank.pos.y) == (4,12):
                self.dire = Dir.UP
                self.tank.direction = self.dire
                self.tank.dire =self.dire
                return                  
        elif self.name == 'Bot Player2':
            if ((self.tank.pos.x,self.tank.pos.y) != (16,11) and (self.tank.pos.x,self.tank.pos.y) != (16,12)) or ((self.tank.pos.x,self.tank.pos.y) == (16,11) and self.dire !=Dir.UP ):
                    AS_accessory = Find_Path(self.tank.pos.x,self.tank.pos.y,16,12,board,Type_ALL)  # right player back to (16,12)
                    AS_accessory.find_path()
                    if AS_accessory.path:
                        dirx=AS_accessory.path[-2][0]
                        diry=AS_accessory.path[-2][1]
                        self.dire =dep_inv[(dirx-self.tank.pos.x,diry-self.tank.pos.y)]
                        self.tank.direction = self.dire
                        self.tank.dire =self.dire
                    return
            elif (self.tank.pos.x,self.tank.pos.y) == (16,12):
                self.dire = Dir.UP
                self.tank.direction = self.dire
                self.tank.dire =self.dire
                return                            
            
    def nearest_enemy(self, board):

        enemies = [item for item in board if (item.type == 'tank' and item.type2 == 2)]
        if enemies:
            distances = [item.pos.distance(self.tank.pos) for item in enemies]
            index = distances.index(min(distances))
            return enemies[index]
        return None                




class EnemyAI(Enemy):
    def __init__(self, x, y, dire, interval = 1000, power=1 , type3='L'):
        super().__init__(x, y, dire)
        self.type3 = type3
        self.i = 0 #compter le pas de enemy

    def move(self, board):
        if self.i ==39:
            self.change_direction_a_star(board)
            self.i = 0 
        elif self.i%2 == 0:
            self.change_direction_auto(board)
            self.i +=1


        elif self.i == 5 or self.i == 13 or self.i == 29:
            self.change_direction_random()
            self.i += 1
        elif self.i == 7 or self.i == 9:
            if self.tank.items[0].pos.x < 5:
                self.dire = 2
                self.tank.direction = self.dire
                self.tank.dire =self.dire                
            if self.tank.items[0].pos.x >15 :
                self.dire = 0
                self.tank.direction = self.dire
                self.tank.dire =self.dire
#            self.change_direction_random()
            self.i +=1
        else:            
            self.change_direction_a_star(board)
            self.i +=1
#        print(self.i)
        return self.tank.move(board)
    
    def find_base(self, board):
        for item in board:
            if item.type == 'base':
                base = item        
        return base
    
    def goto_base(self, base):
        directions = [self.dire, (self.dire + 1) % 4, (self.dire + 2) % 4, (self.dire + 3) % 4]
        positions = [self.tank.pos.translate_outofplace(dep[direction]) for direction in directions]
        distances = [pos.distance(base.pos) for pos in positions]
        index = distances.index(min(distances))
        return directions[index]  

    def avoid_collision(self, board):
        directions = [self.dire, (self.dire + 1) % 4, (self.dire + 2) % 4, (self.dire + 3) % 4]
        obstacles = [item for item in board if item.type == 'brick' or item.type == 'wall' or item.type == 'tank']
        for direction in directions:
            pos = self.tank.pos.translate_outofplace(dep[direction])
            collisions = [item.pos == pos for item in obstacles]
            if True not in collisions:
                break
        return direction
    
    def change_direction_a_star(self, board):
        base = self.find_base(board)
        obstacles = [item for item in board if item.type == 'brick' or item.type == 'wall' or item.type == 'tank']
# =============================================================================
#         AS_accessory = Find_Path(self.tank.pos.x,self.tank.pos.y,base.pos.x,base.pos.y,obstacles,Type_ALL)
#         AS_accessory.find_path()
#         if AS_accessory.path:
#             dirx=AS_accessory.path[-2][0]
#             diry=AS_accessory.path[-2][1]
#             self.dire =dep_inv[(dirx-self.tank.pos.x,diry-self.tank.pos.y)]
#             self.tank.direction = self.dire
#             self.tank.dire =self.dire
# =============================================================================
        if (self.tank.pos.x,self.tank.pos.y)!=(8,17) and (self.tank.pos.x,self.tank.pos.y)!=(9,17):
            AS_accessory = Find_Path(self.tank.pos.x,self.tank.pos.y,8,17,obstacles,Type_ALL)
            AS_accessory.find_path()
            if AS_accessory.path:
                dirx=AS_accessory.path[-2][0]
                diry=AS_accessory.path[-2][1]
                self.dire =dep_inv[(dirx-self.tank.pos.x,diry-self.tank.pos.y)]
                self.tank.direction = self.dire
                self.tank.dire =self.dire
        else:
                self.dire =Dir.RIGHT
                self.tank.direction = self.dire
                self.tank.dire =self.dire            
    
    def change_direction_auto(self,board):
        if (self.tank.pos.x,self.tank.pos.y)!=(8,17) and (self.tank.pos.x,self.tank.pos.y)!=(9,17):
            base = self.find_base(board)        
            if base:
                self.direction = self.goto_base(base)  
            obstacles = [item for item in board if item.type == 'brick' or item.type == 'wall' or item.type == 'tank']
            self.dire = self.avoid_collision(board)
            self.tank.direction = self.dire   
            self.tank.dire =self.dire
        else:
                self.dire =Dir.RIGHT
                self.tank.direction = self.dire
                self.tank.dire =self.dire         
        
    def change_direction_random(self):
        self.dire = random.choice(range(4))
        self.tank.direction = self.dire
        self.tank.dire =self.dire
        
#################################################################     find path
### reference https://anseyuyin.github.io/AStar-Process/demo/
class Node:
    def __init__(self, parent, x, y, dist):
        self.parent = parent
        self.x = x
        self.y = y
        self.dist = dist

class Find_Path:    
    def __init__(self, s_x, s_y, e_x, e_y, board, Typeall):
        self.s_x = s_x
        self.s_y = s_y
        self.e_x = e_x
        self.e_y = e_y
        self.board=board
        self.Typeall=Typeall
        self.width = 21
        self.height = 19
        self.open = []
        self.close = []
        self.path = []

    def get_F(self, i):
        # F = G + H
        return i.dist + math.fabs(self.e_x-i.x)+math.fabs (self.e_y-i.y)

    def find_path(self):
        p = Node(None, self.s_x, self.s_y, 0.0)
        while True:
            self.extend_round(p)
            if not self.open:
                return
            idx, p = self.get_best()
            if self.is_target(p):
                self.make_path(p)
                return
            self.close.append(p)
            del self.open[idx]
            
    def make_path(self,p):
        while p:
            self.path.append((p.x, p.y))
            p = p.parent
        
    def is_target(self, i):
        return i.x == self.e_x and i.y == self.e_y
        
    def get_best(self):
        best = None
        bv = 1000000 
        bi = -1
        for idx, i in enumerate(self.open):
            value = self.get_F(i)   #get F
            if value < bv:   
                best = i
                bv = value
                bi = idx
        return bi, best

    def node_close(self, node):
        for i in self.close:
            if node.x == i.x and node.y == i.y:
                return True
        return False
        
    def node_open(self, node):
        for i, n in enumerate(self.open):
            if node.x == n.x and node.y == n.y:
                return i
        return -1    
            
    def extend_round(self, p):
        xs = (0, -1, 1, 0)
        ys = (-1, 0, 0, 1)
        for x, y in zip(xs, ys):
            new_x, new_y = x + p.x, y + p.y
            if not self.valid_coord(new_x, new_y):
                continue
            node = Node(p, new_x, new_y, p.dist+1)
            if self.node_close(node):
                continue
            i = self.node_open(node)
            if i != -1:
                if self.open[i].dist > node.dist:
                    self.open[i].parent = p
                    self.open[i].dist = node.dist
                continue
            self.open.append(node)
                            
    def valid_coord(self, x, y):
        for item in self.board:
            if item.pos.x==x and item.pos.y==y and item.type in self.Typeall:
                return False
        return True


##############################################################             test

def testwallman():    
    wallman = WallManager(21, 19)
    wallman.create_border()
    wallman.load_map()
    wallman.create_bonus()
    print('{}'.format(wallman.get_bonus()[0].type))
    
def testplayer():
    player=Player('Player', 1, 1, 3)
    player.shoot()
    print('player: tank type2:  {}     bullet type2:  {}'.format(player.tank.items[0].type2, player.bullets[0].type2))    
        
def testenemy():
    enemy = Enemy(10,1,0)
    enemy.shoot()
    print('enemy: tank type2:  {}     bullet type2:  {}'.format(enemy.tank.items[0].type2, enemy.bullets[0].type2))      
    
    

if __name__ == '__main__':
    testwallman()
    testplayer()
    testenemy()
