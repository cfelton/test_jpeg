
from collections import OrderedDict

from .video_source import VideoSource

# color bar template, lifted from rhea.cores.video.color_bars
COLOR_BARS = OrderedDict(
    white=dict(red=1, green=1, blue=1),
    yellow=dict(red=1, green=1, blue=0),
    cyan=dict(red=0, green=1, blue=1),
    green=dict(red=0, green=1, blue=0),
    magenta=dict(red=1, green=0, blue=1),
    red=dict(red=1, green=0, blue=0),
    blue=dict(red=0, green=0, blue=1),
    black=dict(red=0, green=0, blue=0),
)


class ColorBars(VideoSource):
    def __init__(self, resolution=(1920, 1080), color_depth=(8, 8, 8),
                 frame_rate=60, swap_rate=1):
        """A color bar video stream model

        Args:
            resolution (tuple):
            color_depth (tuple):
            frame_rate (float): frame rate of the video in Hz
            swap_rate  (float): color bar shift in Hz, each bar will
                move one to the right at this rate, should be much less
                than the frame rate
        """
        self.resolution = res = resolution
        self.color_depth = color_depth
        self.frame_rate = frame_rate
        self.swap_rate = swap_rate

        self.pwidth = pwidth = sum(self.color_depth)
        self.num_colors, pmax = len(COLOR_BARS), (2**pwidth)-1
        # the bar widths are all the same
        self.bar_width = int(res[0] // self.num_colors)

        # create a list to index into
        self.color_bars = [vv.copy() for vv in COLOR_BARS.values()]

        # convert the colors to the color depth
        rmx, gmx, bmx = [(cc**2)-1 for cc in self.color_depth]
        for color in self.color_bars:
            color['red'] = color['red'] * rmx
            color['green'] = color['green'] * gmx
            color['blue'] = color['blue'] * gmx

        super(ColorBars, self).__init__(resolution, frame_rate, color_depth)

    def pixel_value(self, row, col):
        # the row index is not used/needed for color bars
        idx = int(col // self.bar_width)
        color = self.color_bars[idx]

        self.pixel.red.next = r = color['red']
        self.pixel.green.next = g = color['green']
        self.pixel.blue.next = b = color['blue']

        return r, g, b

    def check_pixel(self, rgb, npixel=None):
        """

        Args:
            row: row index of the pixel
            col: column index of the pixel
            rgb (tuple):
        """
        if npixel is None:
            npixel = self.npixel

        ncols, nrows = self.resolution
        row, col = npixel // nrows, npixel % nrows
        r, g, b = self.pixel_value(row, col)
        assert r == rgb[0] and g == rgb[1] and b == rgb[2]

        npixel += 1
        if npixel >= (nrows * ncols):
            npixel = 0


    def check_pixel(self, buffer, frame=0, offset=0):
        """Regenerate a frame and compare it to a buffer

        Args:
            frame (int): which frame to compare

        Returns:

        """
        pass