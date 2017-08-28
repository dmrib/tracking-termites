"""Abstracts the video manipulation by OpenCV."""


import sys
import cv2

class VideoPlayer:
    """An image sequence manipulation abstraction."""
    def __init__(self, source_path, default_size, info=True):
        """Initializer.

        Args:
            source_path (str): path to video source.
            info (bool): should write frame info.
        Returns:
            None.
        """
        self.source = cv2.VideoCapture(source_path)
        if not self.source.isOpened:
            print('Could not open video.')
            sys.exit()

        self.current_frame = None
        self.playing = False
        self.default_size = default_size
        self.info = info
        self.start()

    def start(self):
        """Read video capture first frame.

        Args:
            None.
        Return:
            None.
        """
        self.next_frame()
        if not self.playing:
            print('Could not read video.')
            sys.exit()

    def next_frame(self):
        """Read video next frame.

        Args:
            None.
        Returns:
            is_playing (bool): flag to end of the video.
            frame (np.ndarray): next frame.
        """
        self.playing, frame = self.source.read()
        self.current_frame = cv2.resize(frame, self.default_size)

        if self.info:
            cv2.putText(self.current_frame, f'#{int(self.source.get(cv2.CAP_PROP_POS_FRAMES))} of'
                               f' {int(self.source.get(cv2.CAP_PROP_FRAME_COUNT))},'
                               f' {int(self.source.get(cv2.CAP_PROP_FPS))}fps.',
                       (10,10), 7, color=(0, 0, 0), fontScale=0.3)

    def pause(self):
        """Pauses image sequence.

        Args:
            None.
        Returns:
            None.
        """
        cv2.waitKey()

    def show_current_frame(self, window_name):
        """Display current frame.

        Args:
            None.
        Returns:
            None.
        """
        cv2.imshow(window_name, self.current_frame)

    def draw_label(self, label, color, coordinate):
        """Draw label at coordinate on current frame.

        Args:
            label (str): label text.
            color (tuple): label color.
            coordinates (tuple): label coordinate.
        Returns:
            None.
        """
        cv2.putText(self.current_frame, label, coordinate, 2, color=color, fontScale=0.3)

    def draw_line(self, origin, end, color):
        """Draw line from origin to end on current frame.

        Args:
            origin (tuple): line origin point.
            end (tuple): line end point.
            color (tuple): line color.
        """
        cv2.line(self.current_frame, origin, end, color=color, thickness=1)

    def draw_b_box(self, origin, end, color, strong=False):
        """Draw bounding box on current frame.

        Args:
            origin (tuple): bounding box origin point.
            end (tuple): bounding box end point.
            color (tuple): bounding box color.
            strong (bool): should use collision style box.
        Returns:
            None.
        """
        if strong:
            cv2.rectangle(self.current_frame, origin, end, color, 5)
        else:
            cv2.rectangle(self.current_frame, origin, end, color)

    def select_roi(self):
        """Prompt user for a region of interest.

        Args:
            None.
        Returns:
            ROI (tuple): selected ROI coordinates.
        """
        ROI = cv2.selectROI(self.current_frame, False)
        cv2.destroyWindow('ROI selector')
        return ROI


if __name__ == '__main__':
    vp = VideoPlayer('E:/C0001.mp4', (640,480))
    print(vp.select_roi())
