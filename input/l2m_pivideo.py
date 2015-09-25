import io
import random
import numpy
import threading
import time
from picamera import PiCamera
from PIL import Image

DEBUG = False


def clamp(val, min, max): return sorted((val, min, max))[1]


class Pivideo():
    def __init__(self, update_rate=15, debug=False):
        global DEBUG
        DEBUG = debug

        self.update_rate = update_rate

        self.brightness = 0
        self.variance = 0
        self.rbratio = 0

        threading.Thread(target=self.update).start()

    def update(self):
        while True:
            start_time = time.time()
            stream = io.BytesIO()

            with PiCamera() as camera:
                camera.resolution = (640, 480)
                camera.capture(stream, format='jpeg', use_video_port=True, quality=20)

            # Open image
            stream.seek(0)
            image = Image.open(stream)

            # Separate out RGB channels
            rdat = image.getdata(0)
            gdat = image.getdata(1)
            bdat = image.getdata(2)

            # Average RGB channels individually
            sample_size = 1000
            ravg = numpy.median(random.sample(rdat, sample_size))
            gavg = numpy.median(random.sample(gdat, sample_size))
            bavg = numpy.median(random.sample(bdat, sample_size))
            rgb = [ravg, gavg, bavg]

            self.brightness = int((numpy.mean(rgb) * (100.0 / 125)) - 50)
            rscaled = (ravg + 1) * (100.0 / 125)
            bscaled = (bavg + 1) * (100.0 / 125)
            self.rbratio = int(rscaled - bscaled)

            histo = image.histogram()
            self.variance = int(100000000.0 / numpy.var(histo) - 35)
            stream.close()

            # Cap ranges of variables
            self.brightness = clamp(self.brightness, -50, 50)
            self.variance = clamp(self.variance, -50, 50)
            self.rbratio = clamp(self.rbratio, -50, 50)

            if DEBUG:
                msg = ['Pivideo update',
                       "Brightness: {}".format(self.brightness),
                       "Variance: {}".format(self.variance),
                       "RB Ratio: {}".format(self.rbratio),
                       '']
                print('\n'.join(msg))

            remaining = self.update_rate - (time.time() - start_time)
            if remaining > 0:
                time.sleep(remaining)

    def get_energy(self):
        return int(self.rbratio)

    def get_disposition(self):
        return int(self.brightness)

    def get_chaos(self):
        return int(self.variance)
