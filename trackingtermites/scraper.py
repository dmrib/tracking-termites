import cv2
import glob
import json
import numpy as np
import os
import pandas as pd
import sys
import termite as trmt


class Scraper():
    def __init__(self, settings_path):
        '''Initializer.

        Args:
            settings_path (str): path to settings file.
        Returns:
            None.
        '''
        self.termites = []

        self._load_settings(settings_path)
        self._load_metadata()
        self._load_termites()


        self.video = cv2.VideoCapture(self.metadata['video_path'])

    def _load_metadata(self):
        '''Load tracking metadata file.

        Args:
            None.
        Returns:
            None.
        '''
        with open(os.path.join(self.settings['source_folder'], 'meta.json')) as metadata:
            self.metadata = json.load(metadata)

    def _load_settings(self, settings_file):
        '''Load labeling session settings file.

        Args:
            settings_file (str): path to tracking session settings file.
        Retuns:
            None.
        '''
        with open(settings_file) as settings:
            self.settings = json.load(settings)

    def _load_termites(self):
        '''Load termite data.

        Args:
            None.
        Returns:
            None.
        '''
        for termite_number in range(1, self.metadata['n_termites'] + 1):
            label = 't' + str(termite_number)
            file_name = '{}-trail.csv'.format(label)
            file_path = os.path.join(self.settings['source_folder'], file_name)
            termite = trmt.Termite(label)
            termite.from_csv(file_path)
            self.termites.append(termite)

        self._compute_distances()

    def _compute_distances(self):
        '''Compute distances between termites on every experiment frame and
           updates dataframes.

        Args:
            None.
        Returns:
            None.
        '''
        for termite in self.termites:
            termite.trail['x'] = termite.trail['x'] + termite.trail['xoffset']/2
            termite.trail['y'] = termite.trail['y'] + termite.trail['yoffset']/2

        for a_number, termite_a in enumerate(self.termites, start=1):
            for b_number, termite_b in enumerate(self.termites, start=1):
                if a_number != b_number:
                    distance = np.sqrt((((termite_a.trail['x']-termite_b.trail['x'])**2) +
                               ((termite_a.trail['y']-termite_b.trail['y'])**2)))
                    termite_a.trail['distance_to_t{}'.format(b_number)] = distance
                    termite_a.trail['interaction_with_t{}'.format(b_number)] = 'no-interaction'

    def scrape(self):
        '''Starts labeling session.

        Args:
            None.
        Returns:
            None.
        '''
        if not os.path.exists(self.settings['output_path']):
            os.makedirs(self.settings['output_path'])

        entries_number = len(self.termites[0].trail['frame'].values)

        for frame_number in range(1, entries_number):
            playing, frame = self.video.read()
            if not playing:
                print('The end.')
                sys.exit()
            frame = cv2.resize(frame, (0,0), fx=self.metadata['resize_ratio'],
                               fy=self.metadata['resize_ratio'])
            print('Scraping on frame {} of {}'.format(frame_number, entries_number-1))

            for n_termite in range(len(self.termites)):
                predicted = (int(self.termites[n_termite].trail.loc[frame_number, 'x']), int(self.termites[n_termite].trail.loc[frame_number, 'y']))
                for other in range(n_termite+1, len(self.termites)):
                    other_predicted = (int(self.termites[other].trail.loc[frame_number, 'x']), int(self.termites[other].trail.loc[frame_number, 'y']))
                    if self.termites[n_termite].trail.loc[frame_number, 'distance_to_{}'.format(self.termites[other].trail.loc[0, 'label'])] < self.settings['distance_threshold']:
                        half = ((predicted[0]+other_predicted[0])//2, (predicted[1]+other_predicted[1])//2)
                        event = frame[(half[1]-self.settings['collection_edge']):(half[1]+self.settings['collection_edge']),
                                      (half[0]-self.settings['collection_edge']):(half[0]+self.settings['collection_edge'])]
                        cv2.imwrite(self.settings['output_path']+'{}-t{}-t{}.jpg'.format(frame_number, n_termite, other), event)


class OfflineLabeler():
    def __init__(self, settings_file):
        '''Initializer.

        Args:
            settings_path (str): path to settings file.
        Returns:
            None.
        '''
        self.paths = []
        self._load_settings(settings_file)
        self.collect_paths()

    def _load_settings(self, settings_file):
        '''Load labeling session settings file.

        Args:
            settings_file (str): path to tracking session settings file.
        Retuns:
            None.
        '''
        with open(settings_file) as settings:
            self.settings = json.load(settings)

    def _create_collections(self):
        '''Create labeled images folders.

        Args:
            None.
        Returns:
            None.
        '''
        for event in self.settings['events'].values():
            folder_name = os.path.join(self.settings['images_folder'], event)
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

    def collect_paths(self):
        '''Get all images paths in the images folder.

        Args:
            None.
        Returns:
            None.
        '''
        self.paths = [x for x in glob.glob(self.settings['images_folder']+'*.jpg')]

    def augment_dataset(self):
        '''Artificially augment dataset.

        Args:
            None.
        Returns:
            None.
        '''
        print('Augmenting dataset...')
        for folder in self.settings['events'].values():
            labeled = glob.glob(os.path.join(self.settings['images_folder'],
                                folder + '/*.jpg'))
            for image in labeled:
                frame = cv2.imread(image)
                artificial = cv2.flip(frame, 0)
                cv2.imwrite(image[:-4]+'-a1'+image[-4:], artificial)
                artificial = cv2.flip(frame, 1)
                cv2.imwrite(image[:-4]+'-a2'+image[-4:], artificial)
                artificial = cv2.flip(artificial, 0)
                cv2.imwrite(image[:-4]+'-a3'+image[-4:], artificial)

    def label(self):
        '''Start hand labeling loop.

        Args:
            None.
        Returns:
            None.
        '''
        self._create_collections()
        for image_id, path in enumerate(self.paths):
            print(path)
            frame = cv2.imread(path)
            cv2.imshow('Labeling', frame)
            pressed_key = cv2.waitKey(0) & 0xff
            if chr(pressed_key) in self.settings['events']:
                path = os.path.join(self.settings['images_folder'],
                                    self.settings['events'][chr(pressed_key)] +
                                    '/' + str(image_id) + '.jpg')
                cv2.imwrite(path, frame)

            if pressed_key == 27:
                sys.exit()


if __name__ == '__main__':
    scraper = Scraper('settings/scraper.json')
    scraper.scrape()

    labeler = OfflineLabeler('settings/scraper.json')
    labeler.label()
    labeler.augment_dataset()