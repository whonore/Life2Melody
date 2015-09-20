from picamera import PiCamera
import time
from PIL import Image
import io
import numpy
import threading

def clamp(val, min, max): return sorted((val, min, max))[1]

class Video():
    def __init__(self):
        self.uprate = 3
        
        self.brightness = 0
        self.variance = 0
        self.rbratio = [0, 0, 0]
        
        threading.Thread(target=self.update()).start()
        
    def update(self):
        while True:
            start_time = time.time()
            stream = io.BytesIO()
            with PiCamera() as camera:
                camera.resolution = (640, 480)
                camera.capture(stream, format='jpeg')
                camera.close

            #open image
            stream.seek(0)
            image = Image.open(stream)
            image.load()
            rdat = list(image.getdata(0))       #separate out RGB channels
            gdat = list(image.getdata(1))
            bdat = list(image.getdata(2))
            ravg = numpy.mean(rdat)  #average RGB channels individually
            gavg = numpy.mean(gdat)
            bavg = numpy.mean(bdat)
            rgb = [ravg,gavg,bavg]
            self.brightness = int((numpy.mean(rgb)*(100.0/125))-50)
            rscaled = (ravg+1)*(100.0/125)
            bscaled = (bavg+1)*(100.0/125)
            self.rbratio = int(rscaled - bscaled)

            histo = image.histogram()
            self.variance = int(100000000.0/numpy.var(histo) - 35)
            stream.close()
            
            #cap ranges of variables
            self.brightness = clamp(self.brightness, -50, 50)
            self.variance = clamp(self.variance, -50, 50)
            self.rbratio = clamp(self.rbratio, -50, 50)
            
            print self.brightness, self.variance, self.rbratio
            remaining = self.uprate - (time.time() - start_time)
            if remaining > 0:
                time.sleep(remaining)
                
    def get_energy_change(self):
        return int(self.rbratio)
        
    def get_chaos_change(self):
        return int(self.variance)

    def get_disposition_change(self):
        return int(self.brightness)

Video()
