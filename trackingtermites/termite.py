import numpy as np
import os
import pandas as pd
import random

random.seed(42)

class Termite:
    def __init__(self, caste, number):
        self.caste = caste
        self.number = number
        self.color = (random.randint(1,256), random.randint(1,256),
                      random.randint(1,256))
        self.trail = []
        self.tracker = None

    def __repr__(self):
        return f'{self.label}, {len(self.trail)} steps collected.'

    @property
    def label(self):
        return f'{self.caste}{self.number}'

    def to_dataframe(self):
        self.trail = pd.DataFrame(self.trail)
        self.trail = self.trail.set_index('frame')

    def to_csv(self, output_path):
        self.to_dataframe()
        self.trail.to_csv(f'{output_path}/{self.label}-trail.csv',
                     float_format='%.1f')

    def from_csv(self, source_path):
        self.trail = pd.read_csv(source_path)

    def normalize(self):
        self.trail['x'] = self.trail['x'] + self.trail['xoffset']/2
        self.trail['y'] = self.trail['y'] + self.trail['yoffset']/2


class Nest():
    def __init__(self, n_termites, source_folder):
        self.termites = []
        self.load_termites(n_termites, source_folder)

    def load_termites(self, n_termites, source_folder):
        '''Load termite movement data files from source folder.

        Args:
            n_termites (int): number of termites files.
            source_folder (str): path to folder with termite files.
        Returns:
            None.
        '''
        for termite_number in range(1, n_termites + 1):
            label = 't' + str(termite_number)
            file_name = '{}-trail.csv'.format(label)
            file_path = os.path.join(source_folder, file_name)
            termite = trmt.Termite(label)
            termite.from_csv(file_path)
            self.termites.append(termite)

    def normalize(self):
        '''Adjust predicted points.

        Args:
            None.
        Returns:
            None.
        '''
        for termite in self.termites:
            termite.normalize()
            termite.trail = termite.trail.drop(columns=['xoffset', 'yoffset'])

    def compute_distances(self):
        '''Compute distances between each termite.

        Args:
            None.
        Returns:
            None.
        '''
        for a_number, termite_a in enumerate(self.termites, start=1):
            print('Computing distances of termite {} of {}.'.format(a_number, len(self.termites)))
            for b_number, termite_b in enumerate(self.termites, start=1):
                if a_number != b_number:
                    distance = np.sqrt((((termite_a.trail['x']-termite_b.trail['x'])**2) +
                               ((termite_a.trail['y']-termite_b.trail['y'])**2)))
                    termite_a.trail['distance_to_t{}'.format(b_number)] = distance
                    termite_a.trail['interaction_with_t{}'.format(b_number)] = 'no-interaction'

    def compute_encounters(self, thresold):
        '''Check and point encounters between termites.

        Args:
            thresold (float): distance in pixel units for reporting encounters.
        Returns:
            None.
        '''
        number_of_frames = len(self.termites[0].trail['frame'])
        for frame_number in range(1, number_of_frames):
            print('Computing encounters on frame {} of {}.'.format(frame_number, number_of_frames-1))
            for n_termite in range(len(self.termites)):
                predicted = (int(self.termites[n_termite].trail.loc[frame_number, 'x']), int(self.termites[n_termite].trail.loc[frame_number, 'y']))
                for other in range(n_termite+1, len(self.termites)):
                    other_predicted = (int(self.termites[other].trail.loc[frame_number, 'x']), int(self.termites[other].trail.loc[frame_number, 'y']))
                    if self.termites[n_termite].trail.loc[frame_number, 'distance_to_{}'.format(self.termites[other].trail.loc[0, 'label'])] < thresold:
                        self.termites[n_termite].trail.loc[frame_number, 'interaction_with_{}'.format(self.termites[other].trail.loc[0, 'label'])] = 'encountering'
                        self.termites[other].trail.loc[frame_number, 'interaction_with_{}'.format(self.termites[n_termite].trail.loc[0, 'label'])] = 'encountering'

    def save(self, output_path):
        '''Save termite data in output path.

        Args:
            output_path (str): path to destination folder.
        Returns:
            None.
        '''
        output_path = os.path.join(output_path, 'Expanded')
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for termite in self.termites:
            termite.to_csv(os.path.join(output_path, termite.trail.loc[0, 'label']+'.csv'))


if __name__ == '__main__':
    nest = Nest(4, 'data/Sample Experiment/')
    nest.normalize()
    nest.compute_distances()
    nest.compute_encounters(65)
    nest.save('data/Sample Experiment/')
