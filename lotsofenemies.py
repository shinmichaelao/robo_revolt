from math import *
from tkinter import *
from random import *
import builtins

#importing images
def import_images():
    builtins.playership = PhotoImage(file = "sprites/ship.gif")
    builtins.color_key = ["red", "purple", "gray", "green", "blue", "bronze", "gold"]
    builtins.spinner_images = []
    for colour in color_key:
        imageset = []
        for i in range(3):
            path = "sprites/spinner" + colour + str(i) + ".gif"
            imageset.append(PhotoImage(file = path))

        spinner_images.append(imageset)

    builtins.robot_images = []
    for colour in ["red", "purple", "gray", "green"]:
        imageset = []
        for i in range(3):
            path = "sprites/bot" + colour + str(i) + ".gif"
            imageset.append(PhotoImage(file = path))

        robot_images.append(imageset)

#Key Functions

#Finds next location of an object
def findnextpoints(x, y, speed, direction):
    new_x = x + speed * cos(direction)
    new_y = y - speed * sin(direction)
    return [new_x, new_y]

#Finds the angle between two points
def getAngle(x0, y0, x1, y1):
    deltax = x0 - x1
    deltay = y0 - y1
    try:
        angle = atan(abs(deltay) / abs(deltax))
    except:
        angle = pi/2
        
    
    if deltay > 0:
        if deltax > 0:
                angle = pi - angle
        else:
            angle = angle
    else:
        if deltax > 0:
            angle = pi + angle
        else:
            angle = 2*pi - angle

    return angle

#Set a player class
class player:

    #Initial class variables
    def __init__(self, x, y, colour):
        self.x = x
        self.y = y
        self.speed = 5
        self.xspeed = 0
        self.yspeed = 0
        self.colour = colour
        self.size = 7
        self.cooldown = 0
        self.shooting = False
        self.life = True
        
    #Updates the x and y positions of the player while keeping them inside the screen    
    def updatePos(self):
        if self.x + self.xspeed  * self.speed > 0 and self.x + self.xspeed * self.speed< 600:
            self.x = self.x + self.xspeed * self.speed
        if self.y + self.yspeed  * self.speed> 0 and self.y + self.yspeed * self.speed< 800:
            self.y = self.y + self.yspeed * self.speed

    #Deletes old image and draws new image    
    def drawPlayer(self):
        try:
            s.delete(self.pic)
        except:
            pass
        self.pic = s.create_image(self.x, self.y, image = playership)

#The bread and butter of all SHMUPs: the bullet        
class bullet:

    #Setting initial variables of the bullet, including its path
    #state should be  ["direction", "speed", "nextstate?"]
    def __init__(self, x, y, colour, state, size):
        self.x = x
        self.y = y
        self.colour = colour
        self.state = state
        self.size = size
        self.killme = False

    #Update position of the bullet in regards to its pathing    
    def updatePosition(self):
        global p1

        #Shoot at the player
        if self.state[2] == "homing":
            deltax = self.x - p1.x
            deltay = self.y - p1.y
            try:
                angle = atan(abs(deltay) / abs(deltax))
            except:
                angle = 0
            
            if deltay > 0:
                if deltax > 0:
                        angle = pi - angle
                else:
                    angle = angle
            else:
                if deltax > 0:
                    angle = pi + angle
                else:
                    angle = 2 * pi - angle
                    
            self.state[0] = angle
            self.state[2] = "kill"

        #This is the players 2nd type of shot, the homing type    
        elif self.state[2] == "homing_p":
            global enemies
            if len(enemies) == 0:
                self.state[0] = radians(90)
                
            else:
                deltax = self.x - enemies[0].x
                deltay = self.y - enemies[0].y
                try:
                    angle = atan(abs(deltay) / abs(deltax))
                except:
                    angle = 0
                
                if deltay > 0:
                    if deltax > 0:
                        angle = pi - angle
                    else:
                        angle = angle
                else:
                    if deltax > 0:
                        angle = pi + angle
                    else:
                        angle = 2 * pi - angle
                    
                self.state[0] = angle

        #Uses the travel angle of the bullet to derive the next point
        newpos = findnextpoints(self.x, self.y, self.state[1], self.state[0])
        self.x = newpos[0]
        self.y = newpos[1]
        
            
    #Hit detection between hitbox of bullet and hitbox of player
    def hitDetect(self):
        global p1
        if sqrt((self.x - p1.x)**2 + (self.y - p1.y)**2) < (self.size + p1.size):
            p1.life = False
            self.killme = True
            return

        if self.x > 600 or self.x < 0 or self.y > 800 or self.y < 0:
            self.killme = True

    #Hit detection of player bullets and enemies
    def hitDetect_enemy(self):
        global enemies, score
        for i in range(len(enemies)):
            if sqrt((self.x - enemies[i].x)**2 + (self.y - enemies[i].y)**2) < (self.size + enemies[i].size):
                enemies[i].life -= 1
                self.killme = True
                return
                
        if self.x > 600 or self.x < 0 or self.y > 800 or self.y < 0:
            self.killme = True

    #Draw the image of the bullet at its location        
    def drawMe(self, bad):
        try:
            s.delete(self.pic)
        except:
            pass
        if bad == True:
            self.hitDetect()
        else:
            self.hitDetect_enemy()

        self.pic = s.create_oval(self.x - self.size, self.y - self.size, self.x + self.size, self.y + self.size, fill = self.colour, outline = self.colour)

#Barebones enemy class            
class simple:

    #Initial enemy variables
    def __init__(self, x, y, ai, cd_start):
        self.x = x
        self.y = y
        self.ai = ai
        
        self.cd = cd_start
        #ai is [state, state, state, ...]
        #states are [direction, speed, ticks] <-- for more advanced movement
        self.ticks = 0
        #counting attacks and whatnot
        self.killme = False                             

    #Next position of the enemy    
    def updatePosition(self):
        global score
        
        #If an enemy is dead, award points to player
        if self.life <= 0:
            builtins.score = builtins.score + self.value
            self.killme = True

        #Checks the pathing    
        self.direction = self.ai[0][0]
        self.speed = self.ai[0][1]
        if self.ai[0][2] != "kill":
            if self.ai[0][2] > 0:
                self.ai[0][2] -= 1
            else:
                self.ai.pop(0)
        else:
            if self.x > 600 or self.x < 0 or self.y > 800 or self.y < 0:
                self.killme = True

        #Finds next location of enemy        
        newpos = findnextpoints(self.x, self.y, self.speed, self.direction)
        self.x = newpos[0]
        self.y = newpos[1]
        
    #Delete old image and draw new one    
    def drawMe(self):
        try:
            s.delete(self.pic)
        except:
            pass

        
        if self.image[0] == "spinner":
            self.pic = s.create_image(self.x, self.y, image = spinner_images[self.image[1]][self.image[2]])

        elif self.image[0] == "robot":
            self.pic = s.create_image(self.x, self.y, image = robot_images[self.image[1]][self.image[2]])

        #WOWZERS! THE GIF ANIMATES TOO?!!
        if self.image[2] == 2:
            self.image[2] = 0
        else:
            self.image[2] += 1

#THE REAL ENEMIES
#All of them are structured the same way so I'll just explain it here
#__init__(blahblah) includes the amount of hits each enemy can take, its hitbox, the score value and which image it uses
#shoot(self) is what makes it destroy your ship... hehe xd

#AKA "FODDER1"
class random1(simple):

    def __init__(self, x , y , ai, cd_start):

        simple.__init__(self,x,y,ai, cd_start)
        self.size = 15
        self.value = 100
        
        if difficulty == "Easy":
            self.life = 3
        elif difficulty == "Normal":
            self.life = 5
        else:
            self.life = 7
            
        self.image = ["spinner", randint(0, len(color_key) -1), randint(0,2)]
        
    def shoot(self):
        if self.cd == 0:
            if difficulty == "Easy":
                bulletnum = 1
            elif difficulty == "Normal":
                bulletnum = 3
            else:
                bulletnum = 5

            #Randomly shoots 3 bullets thrice in quick succession    
            for i in range(bulletnum):
                builtins.e_bullets.append(bullet(self.x, self.y,"red", [radians(randint(180,360)), randint(2,5),"kill"], 3))
            self.cd = 10
            self.ticks += 1
            if self.ticks == 3:
                self.ticks = 0
                if difficulty == "Easy":
                    self.cd = 150
                elif difficulty == "Normal":
                    self.cd = 100
                else:
                    self.cd = 70
        else:
            self.cd = self.cd - 1

#AKA "FODDER 2"        
class wave1(simple):

    def __init__(self, x , y , ai, cd_start):
        
        simple.__init__(self,x,y,ai, cd_start)
        self.size = 15
        self.value = 120
        
        if difficulty == "Easy":
            self.life = 3
        elif difficulty == "Normal":
            self.life = 5
        else:
            self.life = 7
            
        self.image = ["spinner", randint(0, len(color_key) -1), randint(0,2)]
        
    def shoot(self):

        #Aims at you with a badly calibrated antimatter shotgun and shoots bullets at you
        if self.cd == 0:
            this_angle = getAngle(self.x, self.y, p1.x, p1.y)
            if difficulty == "Easy":
                bulletnum = [-1,0,1]
                plus_angle = 30
            elif difficulty == "Normal":
                bulletnum = [-2,-1,0,1,2]
                plus_angle = 15
            else:
                bulletnum = [-3,-2,-1,0,1,2,3]
                plus_angle = 10
            for i in bulletnum:
                builtins.e_bullets.append(bullet(self.x, self.y, "red", [this_angle + i*radians(plus_angle), 3, "kill"], 3))
            self.cd = 10
            self.ticks += 1
            if self.ticks == 3:
                self.ticks = 0
                if difficulty == "Easy":
                    self.cd = 150
                elif difficulty == "Normal":
                    self.cd = 100
                else:
                    self.cd = 70
        else:
            self.cd = self.cd - 1

#AKA "FODDER 3"
class circle1(simple):

    def __init__(self, x , y , ai, cd_start):

        simple.__init__(self,x,y,ai, cd_start)
        self.size = 15
        self.value = 120
        
        if difficulty == "Easy":
            self.life = 3
        elif difficulty == "Normal":
            self.life = 5
        else:
            self.life = 7
            
        self.image = ["spinner", randint(0, len(color_key) -1), randint(0,2)]

    def shoot(self):
        #Shoots a circle of bullets that'll fill the screen
        if self.cd == 0:
            if difficulty == "Easy":
                plus_angle = 30
            elif difficulty == "Normal":
                plus_angle = 20
            else:
                plus_angle = 15
                
            this_angle = randint(0,360)
            for i in range(int(360/plus_angle)):
                builtins.e_bullets.append(bullet(self.x, self.y, "red", [radians(i*plus_angle + this_angle), 3,"kill"], 3))
            self.cd = 10
            self.ticks += 1
            if self.ticks == 3:
                self.ticks = 0
                if difficulty == "Easy":
                    self.cd = 150
                elif difficulty == "Normal":
                    self.cd = 100
                else:
                    self.cd = 70
        else:
            self.cd = self.cd - 1

#AKA "FODDER 4"
class spinner1(simple):

    def __init__(self, x , y , ai, cd_start):

        simple.__init__(self,x,y,ai, cd_start)
        self.size = 15
        self.value = 150
        
        if difficulty == "Easy":
            self.life = 3
        elif difficulty == "Normal":
            self.life = 5
        else:
            self.life = 7
            
        self.image = ["spinner", randint(0, len(color_key) -1), randint(0,2)]

    def shoot(self):
        #If robots could get dizzy, this is how they'd shoot...
        #This guy is just spraying bullets around and around....
        if self.cd == 0:
            
            if self.ticks == 0:
                self.this_angle = randint(0,360)
            else:
                self.this_angle += 20
                
            builtins.e_bullets.append(bullet(self.x, self.y, "red", [radians(self.this_angle), 3,"kill"], 3))
            if difficulty == "Hard":
                builtins.e_bullets.append(bullet(self.x, self.y, "red", [radians(self.this_angle + 180), 3,"kill"], 3))

            if difficulty == "Normal":
                self.cd = 0
            else:
                self.cd = 1
                
            self.ticks += 1
            if self.ticks == 54:
                self.ticks = 0
                self.cd = 100
        else:
            self.cd = self.cd - 1

#AKA "DON'T YOU DARE CALL ME FODDER"
class boss(simple):

    def __init__(self, x , y , ai, cd_start):
        
        simple.__init__(self,x,y,ai, cd_start)
        self.size = 20
        self.value = 10000
        
        if difficulty == "Easy":
            self.life = 50

        elif difficulty == "Normal":
            self.life = 75

        else:
            self.life = 100

        self.image = ["robot", randint(0, 3), randint(0,2)]
        self.attack = choice(["spinner", "wave", "circle", "random"])
        
    def shoot(self):

        if self.cd == 0:

            #When a hurricane meets a typhoon, everything becomes a mess!
            #Bullets everywhere!
            if self.attack == "spinner":
                if self.ticks == 0:
                    self.this_angle = degrees(getAngle(self.x,self.y,p1.x,p1.y)) + randint(0,30)
                
                if difficulty == "Easy":
                    builtins.e_bullets.append(bullet(self.x - 50, self.y, "red", [radians(self.this_angle + self.ticks*15), 3,"kill"], 3))
                    builtins.e_bullets.append(bullet(self.x + 50, self.y, "red", [radians(self.this_angle + 180 - self.ticks*15), 3,"kill"], 3))
                elif difficulty == "Medium":
                    builtins.e_bullets.append(bullet(self.x - 50, self.y - 30, "red", [radians(self.this_angle + self.ticks*20), 3,"kill"], 3))
                    builtins.e_bullets.append(bullet(self.x + 50, self.y - 30, "red", [radians(self.this_angle + 180 - self.ticks*20), 3,"kill"], 3))
                    builtins.e_bullets.append(bullet(self.x - 50, self.y - 30, "red", [radians(self.this_angle + 180 +self.ticks*20), 3,"kill"], 3))
                    builtins.e_bullets.append(bullet(self.x + 50, self.y - 30, "red", [radians(self.this_angle + - self.ticks*20), 3,"kill"], 3))
                else:
                    builtins.e_bullets.append(bullet(self.x - 50, self.y - 30, "red", [radians(self.this_angle + self.ticks*10), 3,"kill"], 3))
                    builtins.e_bullets.append(bullet(self.x + 50, self.y - 30, "red", [radians(self.this_angle + 180 - self.ticks*10), 3,"kill"], 3))
                    builtins.e_bullets.append(bullet(self.x - 50, self.y - 30, "red", [radians(self.this_angle + 180 +self.ticks*10), 3,"kill"], 3))
                    builtins.e_bullets.append(bullet(self.x + 50, self.y - 30, "red", [radians(self.this_angle + - self.ticks*10), 3,"kill"], 3))

                if difficulty == "Hard":
                    self.cd = 0
                else:
                    self.cd = 1

                self.ticks += 1
                if self.ticks == 100:
                    self.attack = choice([ "wave", "circle", "random"])
                    self.ticks = 0
                    if difficulty == "Easy":
                        self.cd = 200
                    elif difficulty == "Normal":
                        self.cd = 150
                    else:
                        self.cd = 100

            #I never knew robots could shoot a tsunami at you!!        
            elif self.attack == "wave":
                this_angle = getAngle(self.x, self.y, p1.x, p1.y)
                if difficulty == "Easy":
                    bulletnum = [-2,-1,0,1,2]
                    plus_angle = 15
                elif difficulty == "Normal":
                    bulletnum = [-3,-2,-1,0,1,2,3]
                    plus_angle = 10
                else:
                    bulletnum = [-4,-3,-2,-1,0,1,2,3,4]
                    plus_angle = 5
                for i in bulletnum:
                    builtins.e_bullets.append(bullet(self.x, self.y, "red", [this_angle + i*radians(plus_angle), 3, "kill"], 3))
                self.cd = 10
                self.ticks += 1
                if self.ticks == 20:
                    self.ticks = 0
                    self.attack = choice(["spinner",  "circle", "random"])
                    if difficulty == "Easy":
                        self.cd = 200
                    elif difficulty == "Normal":
                        self.cd = 150
                    else:
                        self.cd = 100

            #Better hope you have enough room to dodge, because this circle is tight!        
            elif self.attack == "circle":
                if difficulty == "Easy":
                    plus_angle = 30
                elif difficulty == "Normal":
                    plus_angle = 20
                else:
                    plus_angle = 15
                    
                this_angle = randint(0,360)
                for i in range(int(360/plus_angle)):
                    builtins.e_bullets.append(bullet(self.x, self.y, "red", [radians(i*plus_angle + this_angle), 3,"kill"], 3))
                self.cd = 10
                self.ticks += 1
                if self.ticks == 10:
                    self.ticks = 0
                    self.attack = choice(["spinner", "wave", "random"])
                    if difficulty == "Easy":
                        self.cd = 200
                    elif difficulty == "Normal":
                        self.cd = 150
                    else:
                        self.cd = 100

            #The fast and the furious... When all else fails!
            else:
                if difficulty == "Easy":
                    bulletnum = 10
                elif difficulty == "Normal":
                    bulletnum = 15
                else:
                    bulletnum = 20
                    
                for i in range(bulletnum):
                    builtins.e_bullets.append(bullet(self.x, self.y,"red", [radians(randint(0,360)), 5,"kill"], 3))
                self.cd = 10
                self.ticks += 1
                if self.ticks == 5 and difficulty == "Easy" or self.ticks == 10 and difficulty == "Normal" or self.ticks == 20 and difficulty == "Hard":
                    self.ticks = 0
                    self.attack = choice(["spinner", "wave", "circle"])
                    if difficulty == "Easy":
                        self.cd = 200
                    elif difficulty == "Normal":
                        self.cd = 150
                    else:
                        self.cd = 100
        else:
            self.cd = self.cd - 1






                    
