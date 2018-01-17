#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 21:39:00 2018

@author: igor
"""

class Options(object):
    def __init__(self):
        self.g=50
        self.speed=3
        self.ball_start=(535, 540)
        self.ball_speed=(-10, 0)
        self.drawcoliders=True

options=Options()