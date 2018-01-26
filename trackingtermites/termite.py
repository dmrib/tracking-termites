from collections import namedtuple


class Termite:
    def __init__(self, label, color):
        self.label = label
        self.color = color
        self.trail = []
        self.tracker = None

    def to_csv(self):
        with open(f'data/{self.label}-trail.csv', mode='w') as trail_out:
            trail_out.write('label,frame,time,x,y\n')
            for record in self.trail:
                trail_out.write(f'{self.label},{record.frame},{record.time},'
                                f'{record.x},{record.y},{record.xoffset},'
                                f'{record.yoffset}\n')
