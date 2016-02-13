import pygame
import sys
import os
local_path = os.getcwd()
sys.path.append("{}/environment".format(local_path))
from team import Team
import constants as cons

'''
All units have certain stats:
base_hp - int
base_attack - int
base_defense - int
base_speed - int
sprite - pygame image
'''

class Unit:
    def __init__(self, name="???", location=None, base_hp=None, base_attack=None, base_defense=None, base_speed=None, base_range=None, sprite=None, team = Team.ENEMY):
        self.name = name
        self.location = location
        self.base_hp = base_hp
        self.current_hp = self.base_hp
        self.base_attack = base_attack
        self.base_defense = base_defense
        self.base_speed = base_speed
        self.base_range = base_range
        self.sprite = sprite
        self.orientation = 0 # ccw
        self.hidden = False
        self.team = team
        self.active = False
    
    def clone(self, team=None):
        cloned = Unit()
        cloned.name = self.name
        cloned.location = self.location
        cloned.base_hp = self.base_hp
        cloned.current_hp = self.current_hp
        cloned.base_attack = self.base_attack
        cloned.base_defense = self.base_defense
        cloned.base_speed = self.base_speed
        cloned.base_range = self.base_range
        cloned.sprite = self.sprite
        cloned.orientation = self.orientation
        cloned.hidden = self.hidden
        cloned.team = team if team is not None else self.team 
        cloned.active = self.active
        return cloned
    
    def get_speed(self):
        return self.base_speed
    
    def get_range(self):
        return self.base_range

Leonidas = Unit(name="Leonidas", base_hp=10000, base_attack=1000, base_defense=1000, base_speed=10, base_range=8, sprite=pygame.image.load('assets/units/leonidas.png'))
red_probe = Unit(name="Probe", base_hp=10, base_attack=0, base_defense=0, base_speed=3, base_range=0, sprite=pygame.image.load('assets/units/probe_red.png'))
