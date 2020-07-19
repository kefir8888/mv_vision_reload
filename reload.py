import cv2
import math
import time
import numpy as np

class Blob:
    def __init__ (self, x_, y_, w_, h_):
        self.x_ = x_
        self.y_ = y_
        self.w_ = w_
        self.h_ = h_

    def x (self):
        return self.x_

    def y (self):
        return self.y_

    def w (self):
        return self.w_

    def h (self):
        return self.h_

    def cx (self):
        return int (self.x_ + self.w_ / 2)

    def cy (self):
        return int (self.y_ + self.h_ / 2)

    def rect (self):
        return (self.x_, self.y_, self.w_, self.h_)

class Line:
    def __init__ (self, x1_, y1_, x2_, y2_, theta_):
        self.x1_ = x1_
        self.y1_ = y1_
        self.x2_ = x2_
        self.y2_ = y2_
        self.theta_ = theta_

    def x1 (self):
        return self.x1_

    def y1 (self):
        return self.y1_

    def x2 (self):
        return self.x2_

    def y2 (self):
        return self.y2_

    def theta (self):
        return self.theta_

    def line (self):
        return (self.x1_, self.y1_, self.x2_, self.y2_)

class Image:
    def __init__ (self, img_):
        self.img = img_

    def find_blobs (self, ths, pixels_threshold, area_threshold, merge, margin, invert = False):
        masks = []

        for th in ths:
            #print ("a", th)
            low_th = (int(th[0] * 2.55), th[2] + 128, th[4] + 128)
            high_th = (int(th[1] * 2.55), th[3] + 128, th[5] + 128)

            labimg = cv2.cvtColor (self.img, cv2.COLOR_BGR2LAB)

            mask = cv2.inRange (labimg, low_th, high_th)

            if (invert == True):
                mask = cv2.bitwise_not (mask)

            masks.append (mask)

        final_mask = masks [0].copy ()

        if (len (masks) > 1):
            #print ("and")
            for m in masks [1:]:
                final_mask = cv2.bitwise_and (final_mask, m)

        #print (final_mask.shape)

        #cv2.imshow("a", final_mask)

        output = cv2.connectedComponentsWithStats (final_mask, 8, cv2.CV_32S)

        #labels_count = output      [0]
        #labels       = output      [1]
        stats        = output      [2]
        #labels_count, labels, stats = output[:3]
        sz = stats.shape[0]

        blobs = []

        for label_num in range (1, sz):
            #print ("cc processing")
            area = stats [label_num, cv2.CC_STAT_AREA]
            
            if (area >= pixels_threshold):
                new_blob = Blob (stats [label_num, cv2.CC_STAT_LEFT],
                                 stats [label_num, cv2.CC_STAT_TOP],
                                 stats [label_num, cv2.CC_STAT_WIDTH],
                                 stats [label_num, cv2.CC_STAT_HEIGHT])

                #print ("append", area)
                blobs.append (new_blob)

        merges_num = 1

        if (merge == True):
            while (merges_num != 0):
                #print ("merges not zero")
                merges_num = 0

                for i in range (len (blobs)):
                #for b1 in blobs:
                    if (merges_num != 0):
                        break

                    b1 = blobs [i]

                    for j in range (i + 1, len (blobs)):
                    #for b2 in blobs [1:]:
                        if (merges_num != 0):
                            break

                        #print ("j", j)
                        #print("merge true", len(blobs))
                        b2 = blobs [j]

                        dx = abs (b1.cx() - b2.cx())
                        dy = abs (b1.cy() - b2.cy())
                        sw = (b1.w() + b2.w()) / 2
                        sh = (b1.h() + b2.h()) / 2

                        #check for bounding boxes intersection with margin
                        if (dx - margin < sw and dy - margin < sh):
                            left = min (b1.x(), b2.x())
                            top  = min (b1.y(), b2.y())

                            right  = max (b1.x() + b1.w(), b2.x() + b2.w())
                            bottom = max (b1.y() + b1.h(), b2.y() + b2.h())

                            b3 = Blob (left, top, right - left, bottom - top)

                            blobs.remove (b1)
                            blobs.remove (b2)
                            blobs.append (b3)

                            merges_num += 1

                            #print ("blobs num", len (blobs))

                            continue

        return blobs

    def binary (self, th):
        low  = (th [0], th [2], th [4])
        high = (th [1], th [3], th [5])

        mask = cv2.inRange(self.img, low, high)

        sh = mask.shape

        result = np.zeros((sh[0], sh[1], 3), img.dtype)

        for i in range(0, 3):
            result[:, :, i] = mask.copy()

        return result

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

        #blobs = img.find_blobs ((40, 80, -28, 72, -28, 72), 200, 20, True, 10)
        #blobs = img.find_blobs ([(35, 50, 15, 75, 50, 135)], 200, 20, True, 10)

        #(self, ths, pixels_threshold, area_threshold, merge, margin, invert = False):
        blobs = img.find_blobs ([(92, 100, 0, 127, 0, 127)], pixels_threshold=20,
                                area_threshold=20, merge = True, margin = 30)

        for blob in blobs:
            #print ("a")
            img.draw_rectangle (blob.rect ())

        #lines = img.find_lines ()

        #for line in lines:
        #    img.draw_line (line.line ())

        cv2.imshow ("objects", img.img)

        time.sleep (0.02)
        
        keyb = cv2.waitKey (1) & 0xFF
        
        if (keyb == ord('q')):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main ()