import pygame
import sys
import os
local_path = os.getcwd()
sys.path.append("{}/..".format(local_path))
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
    def __init__(self, location=None, base_hp=None, base_attack=None, Base_defense=None, base_speed=None, sprite=None):
        self.location = location
        self.base_hp = base_hp
        self.current_hp = self.base_hp
        self.base_attack = base_attack
        self.base_defense = base_defense
        self.base_speed = base_speed
    
    def get_real_speed():
        return self.base_speed