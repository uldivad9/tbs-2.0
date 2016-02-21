from util import load_image

class Status:
    def __init__(self, unit=None, duration=1, sprite=None):
        self.unit = unit
        self.duration = duration
        self.sprite = sprite
    
    def update():
        self.duration -= 1

class CalibrateWeaponsStatus:
    def __init__(self, unit=None, duration=4, power=1000):
        self.unit = unit
        self.duration = duration
        self.power = power
        self.sprite = load_image('assets/icons/calibrateweaponsstatus.png')
    
    def update():
        self.duration -= 1