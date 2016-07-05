from __future__ import division

import io
import random
import threading
import time

from picamera import PiCamera
from PIL import Image
import numpy as np


class Pivideo(object):
    def __init__(self, update_rate=15, debug=False):
        self.debug = debug

        self.update_rate = update_rate  # secs

        self.brightness = 0
        self.variance = 0
        self.rbratio = 0

        self.update()

    def update(self):
        start_time = time.time()
        stream = io.BytesIO()

        with PiCamera() as camera:
            camera.resolution = (640, 480)
            camera.capture(stream, format='jpeg', use_video_port=True,
                           quality=20)

        # Open image
        stream.seek(0)
        image = Image.open(stream)

        # Separate out RGB channels
        rdat = image.getdata(0)
        gdat = image.getdata(1)
        bdat = image.getdata(2)

        # Average RGB channels individually
        sample_size = 1000
        ravg = np.median(random.sample(rdat, sample_size))
        gavg = np.median(random.sample(gdat, sample_size))
        bavg = np.median(random.sample(bdat, sample_size))
        rgb = [ravg, gavg, bavg]

        self.brightness = (np.mean(rgb) * (100 / 125)) - 50

        rscaled = (ravg + 1) * (100 / 125)
        bscaled = (bavg + 1) * (100 / 125)
        self.rbratio = rscaled / bscaled

        histo = image.histogram()
        self.variance = 1e8 / np.var(histo) - 35

        stream.close()

        if self.debug:
            msg = ['Pivideo update',
                   "Brightness: {}".format(self.brightness),
                   "Variance: {}".format(self.variance),
                   "RB Ratio: {}".format(self.rbratio),
                   '']
            print('\n'.join(msg))

        remaining = self.update_rate - (time.time() - start_time)
        threading.Timer(remaining, self.update)

    @property
    def energy(self):
        return int(self.rbratio)

    @property
    def get_disposition(self):
        return int(self.brightness)

    @property
    def get_chaos(self):
        return int(self.variance)
