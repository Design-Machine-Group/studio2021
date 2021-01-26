
class Envelope(object):
    def __init__(self, area):
        self.area = area
        self.carbon = 55
        self.orientation = 'North'
        self.operational = None
        self.materials = {}

    def compute_operational(self):
        self.operational = self.carbon * self.area

    def add_material(self, material):
        name = material['name']
        self.materials[name] = {'co2': material['co2'], 'color': material['color']}

    def to_json(self, filepath):
        pass

if __name__ == '__main__':

    for i in range(60): print('')
    area = 70
    env = Envelope(area)
