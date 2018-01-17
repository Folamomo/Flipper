#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 22:16:51 2018

@author: igor
"""
import pygame
class physics(object):
    def __init__(self):
        self.dt=1
        self.pause=False
        self.clock=pygame.time.clock()
    def run(self):
        while True:
            self.dt=self.clock.tick(1000)/1000
            if not self.pause:
                balls.update()
                arms.update()
    