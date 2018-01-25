from collections import namedtuple
import cv2
import random
import sys
import termite as trmt
import time

Record = namedtuple('Record', ['frame', 'time', 'x', 'y'])

def track(video_path, n_termites):
    termites = []

    # Open video source
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print('Could not find the video file.')
        sys.exit()

    # Read first frame and resize
    playing, frame = video.read()
    frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
    if not playing:
        print('Could not start video.')
        sys.exit()

    # Select termites and start trackers
    for i in range(1, n_termites+1):
        random_color = (random.randint(0, 255), random.randint(0, 255),
                        random.randint(0, 255))
        termite = trmt.Termite(str(i), random_color)
        termite.tracker = cv2.Tracker_create('KCF')
        termite_pos = cv2.selectROI('Select the termite...', frame, False,
                                    False)
        termite.trail.append(Record(int(video.get(cv2.CAP_PROP_POS_FRAMES)),
                             time.strftime("%H:%M:%S",
                             time.gmtime(int(video.get(cv2.CAP_PROP_POS_MSEC)/1000))),
                             int(termite_pos[0]),
                             int(termite_pos[1])))
        termite.tracker.init(frame, termite_pos)
        cv2.destroyWindow('Select the termite...')
        termites.append(termite)

    # Tracking loop
    while True:
        # Read next frame
        playing, frame = video.read()
        if not playing:
            break
        frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)

        # Update tracker and termite trail
        for termite in termites:
            found, termite_pos = termite.tracker.update(frame)
            if not found:
                print('Termite lost.')
            else:
                termite.trail.append(Record(int(video.get(cv2.CAP_PROP_POS_FRAMES)),
                                     time.strftime("%H:%M:%S",
                                     time.gmtime(int(video.get(cv2.CAP_PROP_POS_MSEC)/1000))),
                                     (termite_pos[0]+termite_pos[2])//2,
                                     (termite_pos[1]+termite_pos[3])//2))

            # Draw termites' bounding boxes on current frame
            origin = (int(termite_pos[0]), int(termite_pos[1]))
            end = (int(termite_pos[0] + termite_pos[2]),
                   int(termite_pos[1] + termite_pos[3]))
            cv2.rectangle(frame, origin, end, termite.color)
            cv2.putText(frame, termite.label, (end[0]+5, end[1]+5), 2,
                        color=termite.color, fontScale=0.3)

        # Draw frame info
        cv2.putText(frame, f'Frame #{int(video.get(cv2.CAP_PROP_POS_FRAMES))}'
                           f' of {int(video.get(cv2.CAP_PROP_FRAME_COUNT))}',
                           (5,10), 1, color=(0, 0, 255), fontScale=0.7)

        # Show current frame
        cv2.imshow('Tracking...', frame)
        pressed_key = cv2.waitKey(1) & 0xff
        if pressed_key == 27:
            break

    for termite in termites:
        termite.to_csv()


if __name__ == '__main__':
    #track('D:/Og-footage/00100.MTS', 1)
    #track('D:/Og-footage/00100.MTS', 8)
    track('D:/Og-footage/sample.MP4', 1)
    #track('D:/Og-footage/sample.MP4', 8)
