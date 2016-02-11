import pygame
import sys
import os
local_path = os.getcwd()
sys.path.append("{}/..".format(local_path))
import constants as cons

'''
All units have certain stats:
base_hp, base_attack, base_defense, base_speed
'''

class Unit:
    def __init__(self, location=None, base_hp=None, base_attack=None, Base_defense=None, base_speed=None):
        self.location = location
        self.base_hp = base_hp
        self.max_hp = self.base_hp
        self.current_hp = self.base_hp
        self.base_attack = base_attack
        self.real_attack = self.base_attack
        self.base_defense = base_defense
        self.real_defense = self.real_defense
        self.base_speed = base_speed
        self.real_speed = self.base_speed
    
    def get