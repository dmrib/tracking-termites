import cv2
import pandas as pd
import json
import numpy as np
import os


class LabelingSession():
    def __init__(self, source_folder_path):
        '''Initializer.

        Args:
            source_folder_path (str): path to folder containing tracking data.
        Returns:
            None.
        '''
        self.termites = []

        self._load_metadata(source_folder_path)
        self._load_termites(source_folder_path)

        self.video = cv2.VideoCapture(self.metadata['video_path'])

    def _load_metadata(self, source_folder_path):
        '''Load tracking metadata file.

        Args:
            source_folder_path (str): path to folder containing tracking data.
        Returns:
            None.
        '''
        with open(os.path.join(source_folder_path, 'meta.json')) as metadata:
            self.metadata = json.load(metadata)

    def _load_termites(self, source_folder_path):
        '''Load termite data.

        Args:
            source_folder_path (str): path to folder containing tracking data.
        Returns:
            None.
        '''
        for termite_number in range(1, self.metadata['n_termites'] + 1):
            file_name = '{}-trail.csv'.format(termite_number)
            file_path = os.path.join(source_folder_path, file_name)
            self.termites.append(pd.read_csv(file_path))

    def _compute_distances(self):
        '''Compute distances between termites on every experiment frame and
           updates dataframes.

        Args:
            None.
        Returns:
            None.
        '''
        for a_number, termite_a in enumerate(self.termites, start=1):
            for b_number, termite_b in enumerate(self.termites, start=1):
                if a_number != b_number:
                    distance = np.sqrt((((termite_a['x']-termite_b['x'])**2) +
                               ((termite_a['y']-termite_b['y'])**2)))
                    termite_a['distance_to_{}'.format(b_number)] = distance

    def start(self):
        '''Starts labeling session.

        Args:
            None.
        Returns:
            None.
        '''
        self._compute_distances()

        for frame_number in range(len(self.termites[0]['frame'])):
            playing, frame = self.video.read()
            frame = cv2.resize(frame, (0,0), fx=self.metadata['resize_ratio'],
                       fy=self.metadata['resize_ratio'])

            for termite in self.termites:
                predicted = (int(termite.loc[frame_number, 'x'] + (termite.loc[frame_number, 'xoffset']/2)),
                             int(termite.loc[frame_number, 'y'] + (termite.loc[frame_number, 'yoffset']/2)))
                cv2.circle(frame, predicted, 3, (0,0,255), -1)
                cv2.putText(frame, termite.loc[frame_number,'label'], (predicted[0]+5, predicted[1]+5), 2,
                            color=(0,0,255), fontScale=0.4)

            cv2.imshow('Labeling...', frame)
            pressed_key = cv2.waitKey(1) & 0xff
    
            if pressed_key == 27:
                return False

if __name__ == '__main__':
    labeling = LabelingSession('data/Sample Experiment')
    labeling.start()