import cv2
import math
import time
import numpy as np

class Blob:
    def __init__ (self, x_, y_, w_, h_):
        self.x = x_
        self.y = y_
        self.w = w_
        self.h = h_

    def x (self):
        return self.x

    def y (self):
        return self.y

    def w (self):
        return self.w

    def h (self):
        return self.h

    def cx (self):
        return int (self.x + self.w / 2)

    def cy (self):
        return int (self.y + self.h / 2)

    def rect (self):
        return (self.x, self.y, self.w, self.h)

class Line:
    def __init__ (self, x1_, y1_, x2_, y2_, theta_):
        self.x1 = x1_
        self.y1 = y1_
        self.x2 = x2_
        self.y2 = y2_
        self.theta = theta_

    def x1 (self):
        return self.x1

    def y1 (self):
        return self.y1

    def x2 (self):
        return self.x2

    def y2 (self):
        return self.y2

    def theta (self):
        return self.theta

    def line (self):
        return (self.x1, self.y1, self.x2, self.y2)

class Image:
    def __init__ (self, img_):
        self.img = img_

    def find_blobs (self, th, pixels_threshold, area_threshold, merge, margin):
        low_th  = (th [0], th[2], th [4])
        high_th = (th [1], th[3], th [5])

        labimg = cv2.cvtColor (self.img, cv2.COLOR_BGR2LAB)

        mask = cv2.inRange (labimg, low_th, high_th)

        output = cv2.connectedComponentsWithStats (mask, 8, cv2.CV_32S)

        labels_count = output      [0]
        labels       = output      [1]
        stats        = output      [2]
        sz           = stats.shape [0]

        blobs = []

        for label_num in range (1, sz):
            area = stats [label_num, cv2.CC_STAT_AREA]
            
            if (area >= pixels_threshold):
                new_blob = Blob (stats [label_num, cv2.CC_STAT_LEFT],
                                 stats [label_num, cv2.CC_STAT_TOP],
                                 stats [label_num, cv2.CC_STAT_WIDTH],
                                 stats [label_num, cv2.CC_STAT_HEIGHT])

                #print ("append", area)
                blobs.append (new_blob)

        return blobs

    def find_lines (self):
        # - Почему Колумб приплыл в Америку, а не в Индию?
        # - Потому что он плавал по одометрии

        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        #cv2.imshow ("a", edges)

        #lines = cv2.HoughLines(edges, 5, np.pi / 18, 20)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 150)

        resultant_lines = []

        #print (lines)

        for line in lines:
            x1, y1, x2, y2 = line [0]

            theta = math.atan ((y2 - y1) / (x2 - x1))

            new_line = Line (x1, y1, x2, y2, theta)

            resultant_lines.append (new_line)

        return resultant_lines

    def draw_line (self, line):
        (x1, y1, x2, y2) = line
        cv2.line (self.img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    def draw_rectangle (self, rect):
        (x, y, w, h) = rect
        cv2.rectangle (self.img, (x, y), (x+w, y+h), (255, 0, 0), 3)

class Sensor:
    def __init__ (self, filename_):
        self.filename = filename_
        self.img = cv2.imread (self.filename)

    def snapshot (self):
        return Image (self.img.copy ())

def main ():
    sensor = Sensor ("rgb_basket.jpg")

    while (True):
        #print ("a")
        img = sensor.snapshot ()

        #blobs = img.find_blobs ((35, 50, 15, 75, 50, 135), 200, 20, True, 10)

        #for blob in blobs:
        #    img.draw_rectangle (blob.rect ())

        lines = img.find_lines ()

        for line in lines:
            img.draw_line (line.line ())

        cv2.imshow ("objects", img.img)

        time.sleep (0.02)
        
        keyb = cv2.waitKey (1) & 0xFF
        
        if (keyb == ord('q')):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main ()