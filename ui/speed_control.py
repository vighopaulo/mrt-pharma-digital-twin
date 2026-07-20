class SpeedControl:
    def __init__(self):
        self.speed=1.0
    def set_speed(self,value):
        self.speed=float(value)
    def status(self):
        return {"speed":self.speed,"build":"46"}
