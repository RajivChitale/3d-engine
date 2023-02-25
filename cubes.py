import numpy as np
from tkinter import *
import math
import copy

#make transformation functions
#control position, and use keypress
#display
#place and remove cubes

class Coords:
    def __init__(self, x, y, z):
        self.arr = np.array([x,y,z,1], dtype=float)

    def translate(self, t):
        temp = copy.deepcopy(self)
        temp.arr[0:3] = temp.arr[0:3] + t
        return temp

    def scale(self, scale):
        temp = copy.deepcopy(self)
        temp.arr[0:3] = temp.arr[0:3] * scale
        return temp

    # pitch
    def rotx(self, angle):
        M = np.array([
            [1, 0,               0,                0],
            [0, math.cos(angle), -math.sin(angle), 0],
            [0, math.sin(angle), math.cos(angle),  0],
            [0, 0,               0,                1]
        ])
        temp = copy.deepcopy(self)
        temp.arr = temp.arr @ M
        return temp
    # yaw
    def roty(self, angle):
        M = np.array([
            [math.cos(angle), 0, math.sin(angle), 0],
            [0,               1, 0,               0],
            [-math.sin(angle),0, math.cos(angle), 0],
            [0,               0, 0,               1]
        ])
        temp = copy.deepcopy(self)
        temp.arr = temp.arr @ M
        return temp
    # roll (not used)
    def rotz(self, angle):
        M = np.array([
            [math.cos(angle), -math.sin(angle), 0, 0],
            [math.sin(angle), math.cos(angle),  0, 0],
            [0,               0,                1, 0],
            [0,               0,                0, 1]
        ])
        temp = copy.deepcopy(self)
        temp.arr = temp.arr @ M
        return temp

    # display pixels = (0.5*max width px) * object width/object distance*(tan(fov/2))
    def project(self):
        temp = copy.deepcopy(self)
        fov = 70
        tanfov = math.tan(math.radians(fov/2))
        temp.arr[0:2] = (width/2) * temp.arr[0:2] / (abs(temp.arr[2]) * tanfov) #projection
        temp.arr[0] += width/2                  #bring x to center of screen
        temp.arr[1] = -temp.arr[1] + height/2   #bring y to center of screen and upright y
        return temp

    def calcRelative(self):
        return self.translate(-position[0:3]).roty(position[4]).rotx(position[3]).project()



#render all lines
def renderLines(linelist):
    for linedata in linelist:
        a = linedata[0].calcRelative()
        b = linedata[1].calcRelative()
        clr = linedata[2]

        if(a.arr[2] > 0 or b.arr[2] > 0):
            mycanvas.create_line(a.arr[0], a.arr[1], b.arr[0], b.arr[1], fill=clr) #fix

#draw a single line given transformed coordinates
def drawLine(a, b, clr):
    if(a.arr[2] > 0 or b.arr[2] > 0):
        mycanvas.create_line(a.arr[0], a.arr[1], b.arr[0], b.arr[1], fill=clr) #fix


#settings
blocksize = 10
rendermax = 300
sensitivity = 0.08

#render all cubes
def renderCubes(cubedict):
    for c in cubedict:
        clr = cubedict[c]
        x, y ,z = c[0], c[1], c[2] 
        delta = abs(c[0:3] - position[0:3])
        if any(d > rendermax for d in delta):
            continue

        near1 = Coords(x, y, z).calcRelative()
        near2 = Coords(x, y+blocksize, z).calcRelative()
        near3 = Coords(x+blocksize, y+blocksize, z).calcRelative()
        near4 = Coords(x+blocksize, y, z).calcRelative()
        far1 = Coords(x, y, z+blocksize).calcRelative()
        far2 = Coords(x, y+blocksize, z+blocksize).calcRelative()
        far3 = Coords(x+blocksize, y+blocksize, z+blocksize).calcRelative()
        far4 = Coords(x+blocksize, y, z+blocksize).calcRelative()
        temp = [   
            [near1,near2, clr],
            [near2,near3, clr],
            [near3,near4, clr],
            [near4,near1, clr],
            [far1,far2, clr],
            [far2,far3, clr],
            [far3,far4, clr],
            [far4,far1, clr],
            [near1,far1, clr],
            [near2,far2, clr],
            [near3,far3, clr],
            [near4,far4, clr]
        ]
        for l in temp:
            drawLine(l[0], l[1], clr)

def getCubeCorner():
    global cubes
    a = Coords(0,0,30)
    a = a.rotx(-position[3]).roty(-position[4]).translate(position[0:3])
    a.arr[0:3] -= (a.arr[0:3] % blocksize)
    return (a.arr[0], a.arr[1], a.arr[2])


root = Tk()
height = 500
width = 500
root.geometry("{}x{}".format(height, width))
root.title("demo")
mycanvas =  Canvas(root, width = 500, height= 500, bg="white")
mycanvas.pack(pady=1)

#mycanvas.create_line(0,100, 300,100, fill="red")
position = np.array([0.0 ,50.0 ,0.0, 0.0, 0,0, 0.0]) #initially facing z

def key_pressed(event):
    #w=Label(root,text="Key Pressed:"+event.char)
    #w.place(x=70,y=90)
    global position
    sint = math.sin(position[4])
    cost = math.cos(position[4])
    d=2

    # map for reference
    #
    #        <-t->      
    #        z   /      
    #    a   |  /  w
    #        | /        
    # -x ----|-----x
    #        |    
    #   s    |    d
    #        z

    # forward 
    if event.char == 'w':
        position[0] += d * sint
        position[2] += d * cost
    # backward
    if event.char == 's':
        position[0] -= d * sint
        position[2] -= d * cost
    # left
    if event.char == 'a':
        position[0] -= d * cost
        position[2] += d * sint
    # right
    if event.char == 'd':
        position[0] += d * cost
        position[2] -= d * sint

    # up
    if event.char == 'e':
        position[1] += d
    # down
    if event.char == 'q':
        position[1] -= d

    # pitch up
    if event.char == 'i':
        position[3] -= sensitivity # here, -theta towards +y
    # pitch down
    if event.char == 'k':
        position[3] += sensitivity
    # yaw left
    if event.char == 'j':
        position[4] -= sensitivity
    # yaw right
    if event.char == 'l':
        position[4] += sensitivity
        
#    # roll left
#    if event.char == 'o':
#        position[5] -= 0.05
#    # roll right
#    if event.char == 'u':
#        position[5] += 0.05

    # place marker line
    if event.char == 'm':
        a = Coords(0,-10,40)
        b = Coords(0,10,40)
        a = a.rotx(-position[3]).roty(-position[4]).translate(position[0:3])
        b = b.rotx(-position[3]).roty(-position[4]).translate(position[0:3])
        lines.append([a, b, "red"])

    #create cube
    if event.char == 'h':
        facing = getCubeCorner()
        cubes[facing] = "green"
    #delete cube
    if event.char == 'f':
        facing = getCubeCorner()
        if facing in cubes:
            cubes.pop(facing)

    print(position)
    mycanvas.delete("all")
    renderLines(lines)
    renderCubes(cubes)

root.bind("<Key>",key_pressed)


# coordinates of a corner and colour
cubes = {
    (0,40,100) : "red"
}

#reference obelisk
p1 = Coords(50,50,100)
p2 = Coords(50,100,120)
p3 = Coords(50,50,140)
p4 = Coords(80,50,120)

lines = [
    [p1, p2, "red"],
    [p2, p3, "blue"],
    [p3, p1, "black"],
    [p3, p4, "black"],
    [p2, p4, "green"] ]

renderLines(lines)
renderCubes(cubes)

root.mainloop()
