#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 21:30:27 2018

@author: igor
"""
import math
import pygame
import load
from Options import *
from Flipper import dt

class Ball(pygame.sprite.Sprite):
    def __init__ (self, position, velocity=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
       
        self.position=pygame.math.Vector2(position)
        self.velocity=pygame.math.Vector2(velocity)
        self.image, self.rect=load.load_image("ball.png", -1)
        self.radius=self.rect.w/2
    def bounce (self, normal, material, parent):
        if parent is None:
            coliderVelocity=(0, 0)
        elif type(parent) is Arm:
            coliderVelocity=(self.position-parent.axis).rotate(90)*math.radians(parent.angularvelocity*parent.turndirection)
        if parent is Trigger:
            parent.activate()
        if material == death:
            self.kill()
        relativeVelocity=(self.velocity-coliderVelocity)
        if relativeVelocity.angle_to(normal)>=90 or relativeVelocity.angle_to(normal)<=-90:
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
                        if colider.radius<(self.position-colider.position).length():
                            self.bounce(colisionnormal, colider.material, colider.parent)
                        if colider.radius-self.radius<(self.position-colider.position).length():
                            self.bounce(-colisionnormal, colider.material, colider.parent)
                            
                            
                
    def update (self):
        self.gravity()
        self.colision_detection(coliders)
        self.move()
        
    def move(self):
        self.position+=self.velocity*dt*options.speed
        self.rect.center=self.position
        
    def gravity (self):
        self.velocity+=pygame.math.Vector2(0, options.g)*dt*options.speed