#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 22:54:04 2017

@author: Igor Noga
"""

import os, sys
import pygame

class Options(object):
    def __init__(self):
        self.g=50
        self.speed=2
        self.ball_start=(200, 200)
        self.ball_speed=(100, -100)

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

class Edge(pygame.sprite.Sprite):
    def __init__ (self, start, end):
        pygame.sprite.Sprite.__init__(self)
        self.add(coliders)
        self.start=pygame.math.Vector2(start)
        self.end=pygame.math.Vector2(end)
        self.normal=pygame.math.Vector2(self.end.x-self.start.x, self.end.y-self.start.y).rotate(90).normalize()
        self.bouncines=0.5
        #set up rect properly
        self.rect=pygame.Rect(0, 0, 0, 0)
        self.rect.top=min(self.end.y, self.start.y)
        self.rect.bottom=max(self.end.y, self.start.y)       
        self.rect.left=min(self.end.x, self.start.x)
        self.rect.right=max(self.end.x, self.start.x)
        
class Vertex(pygame.sprite.Sprite):
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.add(coliders)
        self.x, self. y = position
        self.radius=1
        self.bouncines=0.95
        self.rect=pygame.Rect(self.x-self.radius, self.y-self.radius, 2*self.radius+1, 2*self.radius+1)
        
class Ball(pygame.sprite.Sprite):
    def __init__ (self, position, velocity=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.add(balls)
        self.position=pygame.math.Vector2(position)
        self.velocity=pygame.math.Vector2(velocity)
        self.image, self.rect=load_image("ball.png", -1)
        self.radius=self.rect.w/2
    def bounce (self, normal, bouncines):
        if self.velocity.angle_to(normal)>90 or self.velocity.angle_to(normal)<-90:
            self.velocity=self.velocity.reflect(normal)
            self.velocity-=normal*self.velocity.dot(normal)*(1-bouncines) #slow ball down in normal axis, parallel unchanged
        
    def colision_detection (self, coliders):
        
        for colider in coliders.sprites():#pygame.sprite.spritecollide(self, coliders, False, pygame.sprite.collide_circle):  
            if type(colider) is Edge:
                if self.radius > colider.normal.x*(self.position.x-colider.start.x)+colider.normal.y*(self.position.y-colider.start.y):
                    self.bounce(colider.normal, colider.bouncines)
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

screen = pygame.display.set_mode((600, 800))
pygame.display.set_caption('Flipper')

# Fill background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))

    # Initialise sprite Groups
balls = pygame.sprite.Group()
coliders=pygame.sprite.Group()
    # Initialise ball
ball = Ball(options.ball_start,options.ball_speed)
    # Blit everything to the screen
screen.blit(background, (0, 0))
pygame.display.flip()
    # Initialise clock
clock = pygame.time.Clock()


top=Edge((50 , 50) , (550, 50))
right=Edge((550, 50), (550, 500))
bottom=Edge((550, 500), (50, 550))
left=Edge((50, 550), (50, 50))

quit=False

while quit is not True:
    
    dt=clock.tick(60)/1000     #frame length in seconds
   # print(clock.get_fps())
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit=True
    
    screen.blit(background, ball.rect, ball.rect)
    balls.update()
    balls.draw(screen)
    pygame.display.flip()

pygame.quit()