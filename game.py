#ROBOT REVOLT
#By Michael Xu
from tkinter import *
from math import *
from time import *
from random import *
import builtins
from lotsofenemies import *

#Canvas Setting
master = Tk()
builtins.s = Canvas( master, width = 600, height = 800, background = "white")
s.pack()

#Draw the nice blue background
def drawBackground():
    r = 0
    g = 204
    b = 255
    for i in range(1,800,5):
        r += 1.5
        g += .15
        hexcolor = "#%02x%02x%02x" % (int(r) ,int(g) ,int(b))
        s.create_rectangle(0, 801 - i, 600, 800-i, fill = hexcolor, outline = hexcolor)
        
#Key Events   
def keyPressed(event):
    global p1, e_bullets, gamestate, paused, selected, menu

    #What to do while in game
    if gamestate == "game":
        #Setting direction multipliers
        if event.keysym == "Up":
            p1.yspeed = -1
            
        elif event.keysym == "Left":
            p1.xspeed = -1
            
        elif event.keysym == "Down":
            p1.yspeed = 1
            
        elif event.keysym == "Right":
            p1.xspeed = 1

        #Shooting double gun
        elif event.keysym == "z":
            p1.shooting = "straight"
            
        #Shoot homing gun
        elif event.keysym == "x":
            p1.speed = 2.5
            p1.shooting = "homing"

        #Reset to menu
        elif event.keysym == "r":
            clearScreen()
            paused = True
            startScreen()

        #Quit
        elif event.keysym == "q":
            master.destroy()

        #Pause and unpause
        elif event.keysym == "p":
            if paused == False:
                paused = True
            else:
                paused = False
                runRound()

    #What to do in menu screens
    else:
        #Clear screen
        if event.keysym in ["z","x","Up","Down"]:
            if len(menu_items) > 0:
                for i in range(len(menu_items)):
                    s.delete(menu_items[0])
                    menu_items.pop(0)

        #Go back to main menu from help screen
        if menu == "help":
            startScreen()

        #Move the pointer
        elif event.keysym == "Up":
            
            pointer_index = menu.index(selected)
            pointer_index = pointer_index - 1
            if pointer_index < 0:
                pointer_index = len(menu) - 1
            selected = menu[pointer_index]
            
            draw_menu()
            
        elif event.keysym == "Down":
            
            pointer_index = menu.index(selected)
            pointer_index = pointer_index + 1
            if pointer_index == len(menu):
                pointer_index = 0
            selected = menu[pointer_index]
            
            draw_menu()

        #Confirm and run action based on the current menu
        elif event.keysym == "z":
            if selected in ["Easy", "Normal", "Hard"]:
                builtins.difficulty = selected
                runGame()
                
            elif selected == "Play":
                selected = "Normal"
                difficultyScreen()

            elif selected == "Help":
                helpScreen()
                
            elif selected == "Quit":
                master.destroy()

        #Go back to menu from difficulty selection
        elif event.keysym == "x":
            if menu == ["Easy", "Normal", "Hard"]:
                startScreen()
                
#Better version of key-release that doesn't freeze your character        
def wReleased(event):
    global p1
    if gamestate == "game":
        if p1.yspeed < 0:
            p1.yspeed = 0

def aReleased(event):
    global p1
    if gamestate == "game":
        if p1.xspeed < 0:
            p1.xspeed = 0

def sReleased(event):
    global p1
    if gamestate == "game":
        if p1.yspeed > 0:
            p1.yspeed = 0
    
def dReleased(event):
    global p1
    if gamestate == "game":
        if p1.xspeed > 0:
            p1.xspeed = 0

def zReleased(event):
    global p1
    if gamestate == "game":
        if p1.shooting == "straight":
            p1.shooting = False

def xReleased(event):
    global p1
    if gamestate == "game":
        p1.speed = 5
        if p1.shooting == "homing":
            p1.shooting = False

#Menus
def pre_start():
    global menu_items
    import_images()
    drawBackground()
    menu_items = []
    startScreen()
    
def startScreen():
    global menu, menu_items, gamestate, selected
    gamestate = "menu"
    menu = ["Play", "Help", "Quit"]
    selected = "Play"
    draw_menu()

def difficultyScreen():
    global menu
    menu = ["Easy", "Normal", "Hard"]
    draw_menu()

def helpScreen():
    global menu_items, menu
    menu = "help"
    helptext = """
Dodge the red bullets, and shoot the robots out of the sky!
Every few rounds, a boss will spawn! Kill it for MASSIVE points!

Controls:
Arrow keys to move
z to confirm/shoot double minigun
x to cancel/shoot homing shot
p to pause
r to go back to main menu
q to quit the game

Press any key to continue"""
    menu_items.append(s.create_text(300,300, font = "Arial 15", text = helptext))
    
def gameOver():
    global menu_items
    menu_items.append(s.create_rectangle(100,200 ,500,400, fill = "gray"))
    menu_items.append(s.create_text(300,250, font = "Arial 30", text = "Game Over"))
    menu_items.append(s.create_text(300,290, font = "Arial 30", text = "Your score is:"))
    scoredisplay = str(score)
    while len(scoredisplay) < 8:
        scoredisplay = "0" + scoredisplay
    menu_items.append(s.create_text(300,330, font ="Arial 15", text = scoredisplay))
    menu_items.append(s.create_text(300,370, font ="Arial 20", text = "Press r to restart!"))

#Draws the buttons if there are any on the current menu    
def draw_menu():
    global menu_items

    menu_items.append(s.create_text(300,200, font = "Arial 50", text = "ROBOT REVOLT"))
    for i in range(len(menu)):
        if selected == menu[i]:
            fillcolor = "red"
            menu_items.append(s.create_polygon(190,340+i*50, 210,350+i*50 ,190,360+i*50, fill = "black", outline = "black"))
        else:
            fillcolor = "gray"
        menu_items.append(s.create_rectangle(300 - len(menu[i]) * 13,330 + i*50,300 + len(menu[i])* 13,370 + i*50, fill = fillcolor))
        menu_items.append(s.create_text(300,350 + i*50, fill = "black", font = "Arial 20" ,text = menu[i]))
        
    s.update()
    
    
    
#Main Game Procedures

#Sets starting variables
def starting():
    global p1, enemy, e_bullets, p_bullets, paused, score, menu_items, gamestate, boss_count
    builtins.p1 = player(300,600,"blue")
    builtins.enemies = []
    builtins.e_bullets = []
    builtins.p_bullets = []
    builtins.score = 0
    if difficulty == "Easy":
        boss_count = 5
    elif difficulty == "Normal":
        boss_count = 4
    else:
        boss_count = 3
        
    gamestate = "game"
    paused = False

#Drawing the score and # of objects on screen    
def drawScore():
    global menu_items, score
    scoredisplay = str(score)
    while len(scoredisplay) < 8:
        scoredisplay = "0" + scoredisplay

    scoredisplay = "Score: " + scoredisplay
    menu_items.append(s.create_text(580, 20, fill = "black", font = "Arial 12", anchor = "e", text = scoredisplay))

    objects = len(e_bullets) + len(enemies) + len(p_bullets) + 1
    menu_items.append(s.create_text(580, 40, fill = "black", font = "Arial 12", anchor = "e", text = "Objects: " + str(objects)))

#Runs the instance of the game    
def runGame():
    global enemies
    starting()    
    s.after(0,runRound)

#Checks and spawns enemies
def runRound():
    global enemies, boss_count
    
    if len(enemies) == 0:
        
        if boss_count != 0:
            for i in range(randint(3,5)):
                a = randint(1,4)
                if a == 1:
                    enemies.append(spinner1(randint(100,500), randint(0,20),[ [radians(270), 3, randint(10,150)], [0, 0, 1000], [radians(choice([270,90])), 3, "kill"] ], 50))
                elif a == 2:
                    enemies.append(random1(randint(100,500), randint(0,20), [ [radians(270), 3, randint(10,150)], [0, 0, 1000], [radians(choice([270,90])), 3, "kill"] ], 50))
                elif a == 3:
                    enemies.append(wave1(randint(100,500), randint(0,20), [ [radians(270), 3, randint(10,150)], [0, 0, 1000], [radians(choice([270,90])), 3, "kill"] ], 50))
                elif a == 4:
                    enemies.append(circle1(randint(100,500), randint(0,20), [ [radians(270), 3, randint(10,150)], [0, 0, 1000], [radians(choice([270,90])), 3, "kill"] ], 50))
        else:
            enemies.append(boss(300,0, [[radians(270), 3, randint(50,100)], [0, 0, "kill"]], 50))
            if difficulty == "Easy":
                boss_count = 5
            elif difficulty == "Normal":
                boss_count = 4
            else:
                boss_count = 3
        boss_count = boss_count - 1
        
    updateStuff()

    if p1.life and not paused:
        s.after(0, runRound)
        
    elif p1.life == False:
        gameOver()
    
    elif gamestate == "menu":
        clearScreen()      
        draw_menu()

#Updates positions of all on-screen entities and deletes off-screen things        
def updateStuff():
    global p1, enemies, e_bullets, p_bullets, score, menu_items

    #Determines whether or not the player is shooting, and creates bullets if so
    if p1.cooldown > 0:
        p1.cooldown -= 1
    if p1.cooldown == 0:
        if p1.shooting == "straight":
            p1.cooldown = 10
            p_bullets.append(bullet(p1.x + 10, p1.y, "black", [radians(90), 10,"kill"], 5))
            p_bullets.append(bullet(p1.x - 10, p1.y, "black", [radians(90), 10,"kill"], 5))

        elif p1.shooting == "homing":
            p1.cooldown = 20
            p_bullets.append(bullet(p1.x, p1.y, "black", [radians(90), 10, "homing_p"], 5))
            
    p1.updatePos()
    p1.drawPlayer()

    #Update positions
    if len(e_bullets) > 0:
        for i in range(len(e_bullets)):
            e_bullets[i].updatePosition()
                
    if len(p_bullets) > 0:
        for i in range(len(p_bullets)):
            p_bullets[i].updatePosition()

    if len(enemies) > 0:
        for i in range(len(enemies)):
            enemies[i].updatePosition()
            enemies[i].shoot()

    #Remove off-screen and dead things
    if len(e_bullets) > 0:
        killcount = 0
        for i in range(len(e_bullets)):
            if e_bullets[i - killcount].killme:                
                s.delete(e_bullets[i - killcount].pic)
                builtins.e_bullets.pop(i - killcount)
                killcount += 1
        
    if len(p_bullets) > 0:
        killcount = 0
        for i in range(len(p_bullets)):
            if p_bullets[i - killcount].killme:                
                s.delete(p_bullets[i - killcount].pic)
                builtins.p_bullets.pop(i - killcount)
                killcount += 1
                
    if len(enemies) > 0:
        killcount = 0
        for i in range(len(enemies)):
            if enemies[i - killcount].killme:
                s.delete(enemies[i - killcount].pic)
                builtins.enemies.pop(i - killcount)
                killcount += 1

    #Draw the new images for everything    
    for i in range(len(e_bullets)):
        e_bullets[i].drawMe(True)

    for i in range(len(p_bullets)):
        p_bullets[i].drawMe(False)

    for i in range(len(enemies)):
        enemies[i].drawMe()

    if len(menu_items) > 0:
        for i in range(len(menu_items)):
            s.delete(menu_items[0])
            menu_items.pop(0)
            
    #Draw new scoreboard 
    drawScore()
    builtins.score += 1

    #Update screen and sleep
    s.update()
    sleep(0.005)

#Clears the screen of every image
def clearScreen():
    if len(e_bullets) > 0:
        for i in range(len(e_bullets)):
            s.delete(e_bullets[0].pic)
            e_bullets.pop(0)
                
    if len(p_bullets) > 0:
        for i in range(len(p_bullets)):
            s.delete(p_bullets[0].pic)
            p_bullets.pop(0)
            
    if len(enemies) > 0:
        for i in range(len(enemies)):
            s.delete(enemies[0].pic)
            enemies.pop(0)
            
    if len(menu_items) > 0:
        for i in range(len(menu_items)):
            s.delete(menu_items[0])
            menu_items.pop(0)
            
    s.delete(p1.pic)

#Tells tkinter to run pre_start() at the very beginning
master.after(0, pre_start)

#Key bindings
s.bind("<Key>", keyPressed)
s.bind("<KeyRelease-Up>", wReleased)
s.bind("<KeyRelease-Left>", aReleased)
s.bind("<KeyRelease-Down>", sReleased)
s.bind("<KeyRelease-Right>", dReleased)
s.bind("<KeyRelease-z>", zReleased)
s.bind("<KeyRelease-x>", xReleased)

#Misc. Tkinter stuff
s.pack()
s.focus_set()
master.mainloop()
