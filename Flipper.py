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
        self.ball_start=(200, 400)
        self.ball_speed=(100, -100)
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
        
steel=Material("steelsound", 0.7)
bouncer=Material("bouncersound", 1.2)

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
        
class Shape (pygame.sprite.Group):
    def __init__(self, vertices=[], material=steel):
        self.edges=[]
        self.vertices=[]
        self.material=material
        if len(vertices)!=0:
            self.makepolygon(vertices)
    def duplicate(self):
        copy=Shape( [], self.material)
        for edge in self.edges:
            copy.edges.append(Edge(edge.start, edge.end, self.material))
        for vertex in self.vertices:
            copy.vertices.append(Circle(vertex.position, vertex.radius, self.material))
        return copy
    def makepolygon(self, vertices):
        for i in range(len(vertices)):
            self.edges.append(Edge(vertices[i-1], vertices[i], self.material))
            self.vertices.append(Circle(vertices[i], 0, self.material))
    def makecircle(self, center, radius):
        self.vertices.append(Circle(center, radius, self.material))
    def makeedge(self, start, end):
        self.edges.append(Edge(start, end, self.material))
    def add(self, group):
        for colider in self.edges+self.vertices:
            colider.add(group)
    def setparent(self, parent):
        for colider in self.edges+self.vertices:
            colider.parent=parent
    def move(self, vector):
        for edge in self.edges:
            edge.move(vector, vector)
        for vertex in self.vertices:
            vertex.move(vector)
            
class Ball(pygame.sprite.Sprite):
    def __init__ (self, position, velocity=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.add(balls)
        self.position=pygame.math.Vector2(position)
        self.velocity=pygame.math.Vector2(velocity)
        self.image, self.rect=load_image("ball.png", -1)
        self.radius=self.rect.w/2
    def bounce (self, normal, material, parent):
        if parent is None:
            coliderVelocity=(0, 0)
        elif type(parent) is Arm:
            coliderVelocity=(self.position-parent.axis).rotate(90)*math.radians(parent.angularvelocity*parent.turndirection)
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
            #elif type(colider) is Arm:      
    def update (self):
        self.gravity()
        self.colision_detection(coliders)
        self.move()
        
    def move(self):
        self.position+=self.velocity*dt*options.speed
        self.rect.center=self.position
        
    def gravity (self):
        self.velocity+=pygame.math.Vector2(0, options.g)*dt*options.speed
        
class Arm(pygame.sprite.Sprite):
    def __init__(self, axis, shape, rotationlimit, rotatespeed, turndirection, image, imageaxis, key): 
        #shape should be a Shape
        pygame.sprite.Sprite.__init__(self)
        self.add(arms)
        self.axis=pygame.math.Vector2(axis) #point the arm rotates around
        self.shape=shape    #relative to axis
        self.image, self.rect=load_image(image)
        imageaxis=pygame.math.Vector2(imageaxis)
        self.rect.x=self.axis.x-imageaxis.x
        self.rect.y=self.axis.y-imageaxis.y
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
options=Options()
    #inicjalizacja ekranu    
pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Flipper')
    # Fill background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))
    #initialize materials

    # Initialise sprite Groups
balls = pygame.sprite.Group()
coliders=pygame.sprite.Group()
arms=pygame.sprite.Group()

    # Initialise ball
ball1 = Ball(options.ball_start,options.ball_speed)
    # Initialise clocks
physicsclock = pygame.time.Clock()
displayclock = pygame.time.Clock()
    #initialise field
edges=Shape([(50 , 50) , (550, 50), (550, 350), (350, 500), (350, 550), (250, 550), (250, 500), (50, 350)])
edges.add(coliders)
bottom=Edge((350, 545), (250, 545), bouncer)
bottom.add(coliders)
armshape2=Shape([(-40, 10), (0, 0)])
armshape1=Shape([(0, 0), (40, 10)])
arm1=Arm((250, 500), armshape1, 45, 180, -1, "arm.png", 0, pygame.K_z)
arm2=Arm((350, 500), armshape2, 45, 180, 1, "arm.png", 0, pygame.K_m)


    # Blit everything to the screen
screen.blit(background, (0, 0))
pygame.display.flip()

quit=False
dt = 1
def physics():
    while quit is not True:
        global dt
        dt=physicsclock.tick(1000)/1000
        balls.update()
        arms.update()
        
physicsthread=threading.Thread(target=physics)
physicsthread.start()

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
    
    screen.blit(background, (0, 0))
    if options.drawcoliders == True:
        coliders.update()
   # arms.draw(screen)
    balls.draw(screen)
    pygame.display.flip()

pygame.quit()