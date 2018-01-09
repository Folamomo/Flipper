#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 22:54:04 2017

@author: Igor Noga
"""

import os, sys
import pygame
import pygame.gfxdraw


class Options(object):
    def __init__(self):
        self.g=50
        self.speed=0.5
        self.ball_start=(200, 400)
        self.ball_speed=(100, -100)
        self.drawpolygons=False
        self.drawshapes=True
        
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

class Edge(pygame.sprite.Sprite):
    def __init__ (self, start, end, material=steel):
        pygame.sprite.Sprite.__init__(self)
        self.add(coliders)
        self.start=pygame.math.Vector2(start)
        self.end=pygame.math.Vector2(end)
        self.normal=(self.end-self.start).rotate(90).normalize()
        self.material=material

        #set up rect properly
        self.rect=pygame.Rect(0, 0, 0, 0)
        self.rect.top=min(self.end.y, self.start.y)
        self.rect.bottom=max(self.end.y, self.start.y)       
        self.rect.left=min(self.end.x, self.start.x)
        self.rect.right=max(self.end.x, self.start.x)
        
        #draw to background
        if options.drawshapes == True:
            pygame.gfxdraw.line(background, int(self.start.x), int(self.start.y), int(self.end.x), int(self.end.y), (255, 255, 255))

       
class Circle(pygame.sprite.Sprite):
    def __init__(self, position, radius=1,  material=steel):
        pygame.sprite.Sprite.__init__(self)
        self.add(coliders)
        self.position = pygame.math.Vector2(position)
        self.radius=radius
        self.material=material
        self.rect=pygame.Rect(self.position.x-self.radius, self.position.y-self.radius, self.position.x+self.radius, self.position.y+self.radius)
        if options.drawshapes == True:
            pygame.gfxdraw.circle(background, int(self.position.x), int(self.position.y), int(self.radius)+1, (255, 255, 255))           
class Polygon (pygame.sprite.Group):
    def __init__(self, vertices, material=steel):
        self.edges=[]
        self.vertices=[]
        self.material=material
        for i in range(len(vertices)):
            self.edges.append(Edge(vertices[i-1], vertices[i], self.material))
            self.vertices.append(Circle(vertices[i], 0, self.material))
        if options.drawpolygons==True:
            pygame.gfxdraw.polygon(background, vertices, (255, 255, 255))
            
class Ball(pygame.sprite.Sprite):
    def __init__ (self, position, velocity=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.add(balls)
        self.position=pygame.math.Vector2(position)
        self.velocity=pygame.math.Vector2(velocity)
        self.image, self.rect=load_image("ball.png", -1)
        self.radius=self.rect.w/2
    def bounce (self, normal, material):
        if self.velocity.angle_to(normal)>90 or self.velocity.angle_to(normal)<-90:
            self.velocity-=normal*self.velocity.dot(normal)*(1+material.bouncines) #using analitic geometry (magic)
     
    def colision_detection (self, coliders): 
        for colider in coliders.sprites(): 
            if type(colider) is Edge:
                if self.radius > colider.normal.x*(self.position.x-colider.start.x)+colider.normal.y*(self.position.y-colider.start.y): #distance from enge<radius
                    if 0<colider.normal.y*(self.position.x-colider.start.x)-colider.normal.x*(self.position.y-colider.start.y):         #inside box
                        if 0<-colider.normal.y*(self.position.x-colider.end.x)+colider.normal.x*(self.position.y-colider.end.y):
                            if 0 < colider.normal.x*(self.position.x-colider.start.x)+colider.normal.y*(self.position.y-colider.start.y):
                                self.bounce(colider.normal, colider.material)
                            
            elif type(colider) is Circle: 
                if self.radius+colider.radius>(self.position-colider.position).length():
                    self.bounce((self.position-colider.position).normalize(), colider.material)
                    
    def update (self):
        self.gravity()
        
        #colision check
        self.colision_detection(coliders)
        
        self.position+=self.velocity*dt*options.speed
        self.rect.center=self.position
    def gravity (self):
        self.velocity+=pygame.math.Vector2(0, options.g)*dt*options.speed

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
    # Initialise ball
ball1 = Ball(options.ball_start,options.ball_speed)
ball2 = Ball((120, 115), (70, 0))
    # Initialise clock
clock = pygame.time.Clock()
    #initialise field
edges=Polygon([(50 , 0) , (500, 50), (550, 500), (55, 400)])
line=Polygon([ (500, 500), (400, 500)])
square=Polygon([(201 , 200) , (200, 101), (101, 100), (100, 201)])
circle1=Circle((100, 200), 55)
circle2=Circle((300, 310), 0)
square2=Polygon([(250, 250), (250, 300), (300, 300), (300, 250)])
ball3=Ball((320, 230), (-68.356, 50))
    # Blit everything to the screen
screen.blit(background, (0, 0))
pygame.display.flip()

quit=False

while quit is not True:
    
    dt=clock.tick(60)/1000     #frame length in seconds
   # print(clock.get_fps())
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit=True
    for ball in balls:
        screen.blit(background, ball.rect, ball.rect)
    balls.update()
    balls.draw(screen)
    pygame.display.flip()

pygame.quit()