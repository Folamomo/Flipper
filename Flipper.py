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
        
    def reflect (self, angle):
        self.velocity.reflect(0)
    
    def update (self):
        self.gravity()
        self.position+=self.velocity
        self.rect.x, self.rect.y =self.position
    def gravity (self):
        self.velocity=self.velocity+pygame.math.Vector2(0, 0.01)

#inicjalizacja ekranu    
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Flipper')
# Fill background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))
    # Initialise ball
ball = Ball((200, 200), (1, -1))
    # Initialise sprites
ballsprite = pygame.sprite.RenderPlain(ball)
    # Blit everything to the screen
screen.blit(background, (0, 0))
pygame.display.flip()
    # Initialise clock
clock = pygame.time.Clock()

quit=False

while quit is not True:
        # Make sure game doesn't run at more than 60 frames per second
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit=True
        print(event)
    screen.blit(background, ball.rect, ball.rect)
    ballsprite.update()
    ballsprite.draw(screen)
    pygame.display.flip()

pygame.quit()