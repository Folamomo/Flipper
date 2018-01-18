#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 22:54:04 2017

@author: Igor Noga
"""

import os, sys
import pygame
import pygame.gfxdraw
import math
import threading

class Options(object):
    def __init__(self):
        self.g=50
        self.speed=3
        self.ball_start=(535, 540)
        self.ball_speed=(-10, 0)
        self.drawcoliders=True
        
def load_image(name, colorkey=None):
    fullname=os.path.join('data', name)
    try:
        image=pygame.image.load(fullname)
    except pygame.error:
        print ("Cannot load image: ", name)
        raise SystemExit
    image=image.convert()
    if colorkey is not None:
        if colorkey==-1:
            colorkey=image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound:', name)
        raise SystemExit
    return sound

class Material(object):
    def __init__(self, bouncesound, bouncines):
       # self.sound=load_sound(bouncesound)
        self.bouncines=bouncines
        
    #initialize materials
steel=Material("steelsound", 0.6)
bouncermaterial=Material("bouncersound", 1.2)
death=Material("deathsound", 0)
armmaterial=Material("armsound", 0.4)

class Edge(pygame.sprite.Sprite):
    def __init__ (self, start, end, material=steel):
        pygame.sprite.Sprite.__init__(self)
        self.start=pygame.math.Vector2(start)
        self.end=pygame.math.Vector2(end)
        self.normal=self.calculatenormal()
        self.material=material
        self.parent=None
    def calculatenormal(self):
        return (self.end-self.start).rotate(90).normalize()
    def update(self):
        pygame.gfxdraw.line(screen, int(self.start.x), int(self.start.y), int(self.end.x), int(self.end.y), (255, 255, 255))
    def move(self, startvector, endvector):
        self.start+=startvector
        self.end+=endvector
        self.normal=self.calculatenormal()
    def moveto(self, startvector, endvector):
        self.start, self.end=startvector, endvector
        self.normal=self.calculatenormal()
        
class Circle(pygame.sprite.Sprite):
    
    def __init__(self, position, radius=1,  material=steel):
        pygame.sprite.Sprite.__init__(self)
        self.position = pygame.math.Vector2(position)
        self.radius=radius
        self.material=material
        self.parent=None
        
    def update(self):
        pygame.gfxdraw.circle(screen, int(self.position.x), int(self.position.y), int(self.radius)+1, (255, 255, 255))    

    def move(self, vector):
        self.position+=vector
        
    def moveto(self, vector):
        self.position=vector
class Arc(pygame.sprite.Sprite):
    def __init__(self, position, radius=1, startangle=0, endangle=90,  material=steel):
        pygame.sprite.Sprite.__init__(self)
        self.position = pygame.math.Vector2(position)
        self.radius=radius
        self.material=material
        self.start=startangle
        self.end=endangle
        self.parent=None
        
    def update(self):
        pygame.gfxdraw.arc(screen, int(self.position.x), int(self.position.y), int(self.radius), self.start, self.end, (255,255,255))

    def move(self, vector):
        self.position+=vector
        
    def moveto(self, vector):
        self.position=vector
    def rotateto(self, angle):
        span=self.start-self.end
        self.start, self.end = angle, angle+span
        
class Shape (pygame.sprite.Group):
    def __init__(self, vertices=[], material=steel):
        self.edges=[]
        self.vertices=[]
        self.arcs=[]
        self.material=material
        if len(vertices)!=0:
            self.makepolygon(vertices)
    def duplicate(self):
        copy=Shape( [], self.material)
        for edge in self.edges:
            copy.edges.append(Edge(edge.start, edge.end, self.material))
        for vertex in self.vertices:
            copy.vertices.append(Circle(vertex.position, vertex.radius, self.material))
        for arc in self.arcs:
            copy.arcs.append(Arc(arc.position, arc.radius, arc.start, arc.end, self.material))
        return copy
    def makepolygon(self, vertices):
        for i in range(len(vertices)):
            self.edges.append(Edge(vertices[i-1], vertices[i], self.material))
            self.vertices.append(Circle(vertices[i], 0, self.material))
    def makecircle(self, center, radius):
        self.vertices.append(Circle(center, radius, self.material))
    def makearc(self, center, radius, startangle, endangle):
        self.arcs.append(Arc(center, radius, startangle, endangle, self.material))
    def makeedge(self, start, end):
        self.edges.append(Edge(start, end, self.material))
    def add(self, group):
        for colider in self.edges+self.vertices+self.arcs:
            colider.add(group)
    def setparent(self, parent):
        for colider in self.edges+self.vertices+self.arcs:
            colider.parent=parent
    def move(self, vector):
        for edge in self.edges:
            edge.move(vector, vector)
        for vertex in self.vertices:
            vertex.move(vector)
        for arc in self.arcs:
            arc.move(vector)
            
class Ball(pygame.sprite.Sprite):
    def __init__ (self, position, velocity=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.add(balls)
        self.position=pygame.math.Vector2(position)
        self.velocity=pygame.math.Vector2(velocity)
        self.image, self.rect=load_image("ball.png", -1)
        self.radius=self.rect.w/2
    def bounce (self, normal, material, parent):
        coliderVelocity=(0, 0)
        if type(parent) is Arm:
            coliderVelocity=(self.position-parent.axis).rotate(90)*math.radians(parent.angularvelocity*parent.turndirection)
        if parent == target:
            addpoints()
        if material == death:
            self.kill()
        relativeVelocity=(self.velocity-coliderVelocity)
        if relativeVelocity.angle_to(normal)>90 or relativeVelocity.angle_to(normal)<-90:
            relativeVelocity-=normal*relativeVelocity.dot(normal)*(1+material.bouncines) #using analytic geometry (magic)
            self.velocity=relativeVelocity+coliderVelocity
    def colision_detection (self, coliders): 
        for colider in coliders.sprites(): 
            if type(colider) is Edge:
                if self.radius > colider.normal.x*(self.position.x-colider.start.x)+colider.normal.y*(self.position.y-colider.start.y): #distance from enge<radius
                    if 0<colider.normal.y*(self.position.x-colider.start.x)-colider.normal.x*(self.position.y-colider.start.y):         #inside box
                        if 0<-colider.normal.y*(self.position.x-colider.end.x)+colider.normal.x*(self.position.y-colider.end.y):
                            if 0 < colider.normal.x*(self.position.x-colider.start.x)+colider.normal.y*(self.position.y-colider.start.y):
                                self.bounce(colider.normal, colider.material, colider.parent)
                            
            elif type(colider) is Circle: 
                if self.radius+colider.radius>(self.position-colider.position).length():
                    self.bounce((self.position-colider.position).normalize(), colider.material, colider.parent)
            elif type(colider) is Arc:
                if self.radius+colider.radius>(self.position-colider.position).length():
                    colisionnormal=(self.position-colider.position).normalize()
                    colisionangle=pygame.math.Vector2(1 , 0).angle_to(colisionnormal)
                    if colisionangle>colider.start and colisionangle<colider.end:
                        if colider.radius-self.radius<(self.position-colider.position).length():
                            self.bounce(-colisionnormal, colider.material, colider.parent)
                        elif colider.radius<(self.position-colider.position).length():
                            self.bounce(colisionnormal, colider.material, colider.parent)
                        
                            
                            
                
    def update (self):
        self.gravity()
        self.colision_detection(coliders)
        self.move()
        
    def move(self):
        self.position+=self.velocity*dt*options.speed
        self.rect.center=self.position
        
    def gravity (self):
        self.velocity+=pygame.math.Vector2(0, options.g)*dt*options.speed
        
class Trigger:
    def __init__(self, action):
        self.triggerthread=threading.Thread(target=action)
    def activate(self):
        self.triggerthread.start()
def addpoints():
    global score
    score +=100
    return
        
class Arm(pygame.sprite.Sprite):
    def __init__(self, axis, shape, rotationlimit, rotatespeed, turndirection, image, imageaxis, key): 
        #shape should be a Shape and not have any arcs
        pygame.sprite.Sprite.__init__(self)
        self.add(arms)
        self.axis=pygame.math.Vector2(axis) #point the arm rotates around
        self.shape=shape    #relative to axis
        self.baseimage, self.rect=load_image(image, -1)
        self.imageaxis=pygame.math.Vector2(imageaxis)
        
        self.image=pygame.transform.rotate(self.baseimage, 0)
        
        self.rotationlimit=rotationlimit
        self.angle=0 
        self.rotatespeed=rotatespeed
        self.turndirection=turndirection
        self.colider=shape.duplicate()
        self.colider.move(axis)
        self.colider.add(coliders)
        self.colider.setparent(self)
        self.angularvelocity=0 #in degrees
        self.key = key
    def startrotating(self):
        self.angularvelocity=self.rotatespeed
    def stoprotating(self):
        self.angularvelocity=-self.rotatespeed
    def update(self):
        if self.angularvelocity !=0:
            self.angle+=self.angularvelocity*dt*options.speed
            if self.angle>=self.rotationlimit :
                self.angle=self.rotationlimit
                self.angularvelocity=0
            elif  self.angle<0:
                self.angle=0
                self.angularvelocity=0
            for i in range(len(self.colider.edges)):
                newstart=self.shape.edges[i].start.rotate(self.angle*self.turndirection)+self.axis
                newend=self.shape.edges[i].end.rotate(self.angle*self.turndirection)+self.axis
                self.colider.edges[i].moveto(newstart, newend)
            for i in range(len(self.colider.vertices)):
                newcenter=self.shape.vertices[i].position.rotate(self.angle*self.turndirection)+self.axis
                self.colider.vertices[i].moveto(newcenter)
target=Trigger(addpoints)
def initfield():
        # Initialise ball
    Ball(options.ball_start,options.ball_speed)
        
    
        #initialise field
    Shape([(50 , 50) , (530, 50), (529, 600), (370, 750), (370, 820), (230, 820), (230, 750), (50, 600)]).add(coliders)
    Shape([(150, 650), (200, 700), (150, 550)], bouncermaterial).add(coliders)
    Shape([(400, 700),  (450, 650), (450, 550)], bouncermaterial).add(coliders)
    Arc((295, 300), 246,  -180, 0).add(coliders)  
    Edge((540, 300), (540, 550)).add(coliders)
    Shape([(530, 550), (530, 300)]).add(coliders)
    Shape([(530, 570), (550, 570), (550, 550), (530, 550)]).add(coliders)
    Edge((370, 790), (230, 790), death).add(coliders)
    
    circle1=Circle((300, 400), 15, bouncermaterial)
    circle1.add(coliders)
    circle1.parent=target
    circle2=Circle((350, 350), 15, bouncermaterial)
    circle2.add(coliders)
    circle2.parent=target
    circle3=Circle((240, 320), 15, bouncermaterial)
    circle3.add(coliders)
    circle3.parent=target
    
    #initiate arms
    armshape1=Shape([(0, 10), (50, 15), (50, 5), (0, -10)], armmaterial)
    armshape1.makecircle((0, 0), 10)
    armshape1.makecircle((50, 10), 5)
    
    armshape2=Shape([(0, -10), (-50, 5), (-50, 15), (0, 10)], armmaterial)
    armshape2.makecircle((0, 0), 10)
    armshape2.makecircle((-50, 10), 5)
    
    arm1=Arm((230, 760), armshape1, 45, 180, -1, "arm.png", (0, 0), pygame.K_z)
    
    arm2=Arm((370, 760), armshape2, 45, 280, 1, "arm.png", (40, 5), pygame.K_m)

def menu():
    bg1, a = load_image("bg1.png") 
    bg2, a = load_image("bg2.png") 
    bg3, a = load_image("bg3.png") 
    images=[bg1, bg2, bg3]
    flag=True
    location=0
    while flag:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_DOWN:
                    location=(location+1)%3
                if event.key == pygame.K_UP:
                    location=(location-1)%3
                if event.key==pygame.K_RETURN:
                    if location == 0:
                        return True
                    if location == 1:
                        a=0
                    if location == 2:
                        return False
        screen.blit(images[location], (0, 0))
        pygame.display.flip()
dt = 1
def physics():
    physicsclock = pygame.time.Clock() # Initialise clock
    while balls.sprites() != []:
        global dt
        dt=physicsclock.tick(1000)/1000
        balls.update()
        arms.update()
    return()
def gameloop():
    quit = False
    displayclock = pygame.time.Clock()
    while quit is not True:
        
        displayclock.tick(60)     #frame length in seconds
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit=True
            if event.type == pygame.KEYDOWN:
                for arm in arms.sprites():
                    if event.key==arm.key:
                        arm.startrotating()
            if event.type == pygame.KEYUP:
                 for arm in arms.sprites():
                    if event.key==arm.key:
                        arm.stoprotating()
                 if event.key == pygame.K_SPACE:
                    for ball in balls.sprites():
                        if ball.position.x>530 and ball.position.y>530:
                            ball.velocity=pygame.math.Vector2(0, -250)
        
        screen.blit(background, (0, 0))
        
        points = font.render("Score: "+str(score), True, (255, 255, 153))
        screen.blit(points, (430, 700))
        if options.drawcoliders == True:
            coliders.update()
        balls.draw(screen)
        pygame.display.flip()
        if balls.sprites() == []:
            quit = True
    coliders.empty()
    return
    #initialize options
options=Options()
    #initialize screen    
pygame.init()
screen = pygame.display.set_mode((600, 800))
pygame.display.set_caption('Flipper')
    # Initialise sprite Groups
balls = pygame.sprite.Group()
coliders=pygame.sprite.Group()
arms=pygame.sprite.Group()
    #initialize fonts
font = pygame.font.SysFont("Ubuntu Mono", 24)
    # make background
background, bgrect = load_image("background.png")
while menu() != False:
          #initialize physics
    score=0
    physicsthread=threading.Thread(target=physics)
    initfield()
    physicsthread.start()
    gameloop()

pygame.quit()