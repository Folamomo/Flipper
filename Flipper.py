#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 22:54:04 2017

@author: Igor Noga
"""

import os, sys
import pygame

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

class Ball(pygame.sprite.Sprite):
    def __init__ (self, position, velocity=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.position=pygame.math.Vector2(position)
        self.velocity=pygame.math.Vector2(velocity)
        self.image, self.rect=load_image("ball.png", -1)
        
    def bounce (self, angle, bouncines):
        self.velocity=self.velocity.reflect(angle)
        self.velocity+=angle*self.velocity.length()*(1-bouncines)
    
    def update (self):
        self.gravity()
        
        #insert colision check
        
        if self.position.y<50:
            colisionAngle=pygame.math.Vector2(0, -1)
            self.bounce(colisionAngle, 0.95)
            
        if self.position.x<50:
            colisionAngle=pygame.math.Vector2(-1, 0)
            self.bounce(colisionAngle, 0.95)
            
        if self.position.y>550:
            colisionAngle=pygame.math.Vector2(0, 1)
            self.bounce(colisionAngle, 0.95)
            
        if self.position.x>550:
            colisionAngle=pygame.math.Vector2(1, 0)
            self.bounce(colisionAngle, 0.95)

         
         
        
        
        self.position+=self.velocity*dt
        self.rect.x, self.rect.y =self.position
    def gravity (self):
        self.velocity+=pygame.math.Vector2(0, 50)*dt

#inicjalizacja ekranu    
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Flipper')
# Fill background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))
    # Initialise ball
ball = Ball((200, 200), (100, -100))
    # Initialise sprites
ballsprite = pygame.sprite.RenderPlain(ball)
    # Blit everything to the screen
screen.blit(background, (0, 0))
pygame.display.flip()
    # Initialise clock
clock = pygame.time.Clock()

quit=False

while quit is not True:
    
    dt=clock.tick(60)/1000     #frame length in seconds
   # print(clock.get_fps())
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit=True
    
    screen.blit(background, ball.rect, ball.rect)
    ballsprite.update()
    ballsprite.draw(screen)
    pygame.display.flip()

pygame.quit()