import pygame
import sys
import os
local_path = os.getcwd()
sys.path.append("{}/environment".format(local_path))
from team import Team
import constants as cons
import animations
import abilities
from util import abs_pixel_of_loc, load_image


'''
All units have certain stats:
base_hp - int
base_attack - int
base_defense - int
base_speed - int
sprite - pygame image
'''

class Unit:
    def __init__(self, name="???", location=None, base_hp=None, base_attack=None, base_defense=None, base_speed=None, base_range=None, sprite=None, team = Team.ENEMY, base_ability=None):
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
        self.map = None
        self.base_ability = base_ability
    
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
        cloned.map = self.map
        cloned.base_ability = self.base_ability
        return cloned
    
    def get_attack(self):
        return self.base_attack
    
    def get_speed(self):
        return self.base_speed
    
    def get_range(self):
        return self.base_range
    
    def take_damage(self, damage):
        self.current_hp -= damage
        px, py = abs_pixel_of_loc(self.location)
        
        explosion = animations.Explosion(origin = (px + cons.TILESIZE / 2, py + cons.TILESIZE / 2), spark_count=50, radius=30, spark_size=1)
        self.map.animations.append(explosion)
        
        if self.current_hp <= 0:
            death_animation = animations.DeathAnimation(origin = (px,py), sprite=self.sprite)
            self.map.animations.append(death_animation)
            self.map.remove_unit(self)
        damage_text = animations.DamageText(origin = (px + cons.TILESIZE / 2, py + cons.TILESIZE / 4), amount=damage)
        self.map.animations.append(damage_text)
    
#Leonidas = Unit(name="Leonidas", base_hp=10000, base_attack=1000, base_defense=1000, base_speed=10, base_range=8, sprite=pygame.image.load('assets/units/leonidas.png'), base_ability = abilities.BowAttack(8))
#red_probe = Unit(name="Probe", base_hp=10, base_attack=0, base_defense=0, base_speed=3, base_range=0, sprite=pygame.image.load('assets/units/probe_red.png'))

Leonidas = Unit(name="Leonidas", base_hp=10000, base_attack=1000, base_defense=1000, base_speed=10, base_range=8, sprite=load_image('assets/units/leonidas.png'), base_ability = abilities.BowAttack(8))
red_probe = Unit(name="Probe", base_hp=10, base_attack=0, base_defense=0, base_speed=3, base_range=0, sprite=load_image('assets/units/probe_red.png'))
