import dicom
import struct
import pygtk
pygtk.require('2.0')
import gtk
import pdb
import math
import random

PLAN_VAL= 220
MIN_VAL = 100
MID_VAL = 800
MAX_VAL = 10000

class App:
    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()
    def delete_event(self, widget, event, data=None):
        print "delete event occurred"

    def read_plan(self):
        new_plan_id = self.plan_.get_value()
        if new_plan_id == self.plan_id:
            return
        self.plan_id = new_plan_id
        self.directory = "data/04231972/20121220/2.16.840.114421.80129.9409311810.9440847810/"
        print " Self plan_id", self.plan_id
        self.plan   = dicom.read_file(self.directory + ("%04d" % (447-int(self.plan_id))) + ".dcm")
        self.pixels = struct.unpack("<409600H", self.plan.PixelData)


    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)
        self.window.set_default_size(800,800)

        self.vbox = gtk.VBox()
        self.window.add(self.vbox)

        self.plan_id = None
        self.plan_ = gtk.HScale()
        self.plan_.set_range(0, 447)
        self.plan_.set_value(PLAN_VAL)
        self.vbox.add(self.plan_)
        self.plan_.show()
        #label="Min threshold", length=600)


        self.min_ = gtk.HScale()
        self.min_.set_range(0, 1000)
        self.min_.set_value(MIN_VAL)
        self.vbox.add(self.min_)
        self.min_.show()
        #label="Min threshold", length=600)

        self.mid_ = gtk.HScale()
        self.mid_.set_range(0, 2000)
        self.mid_.set_value(MID_VAL)
        self.vbox.add(self.mid_)
        self.mid_.show()
 
        self.max_ = gtk.HScale()
        self.max_.set_range(0, 10000)
        self.max_.set_value(MAX_VAL)
        #label="Max threshold", length=600)
        self.vbox.add(self.max_)
        self.max_.show()

        self.read_plan()

        self.pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 640, 640)
        self.pixbuf_pixels = self.pixbuf.get_pixels_array()
        self.image = gtk.Image()
        self.vbox.add(self.image)
        self.image.show()

        self.vbox.show()
        self.window.show()
        self.drawing = False

        self.plan_.connect(  "button-release-event", self.draw)
        self.min_.connect(  "button-release-event", self.draw)
        self.max_.connect(  "button-release-event", self.draw)
        self.mid_.connect("button-release-event", self.draw)

    def draw(self, widget, event):
        if self.drawing:
            print "Already drawing.  Aborting draw()"
            return

        self.drawing = True
        self.read_plan()
        _min = self.min_.get_value()
        _max = self.max_.get_value()
        _mid = self.mid_.get_value()

        print "Setting pixels with %s -> %s" % (_min, _max)
        self.points_used = 0
        for y in range(640):
          for x in range(640):
            v = self.pixels[y*640+x]
            _v = 0
            if v > _mid and v < _max: _v = 65535
            if v > _min and v <= _mid:
              if random.random() < ((1.0*v - _min)/(_mid - _min)): 
                _v = 32767
            self.pixbuf_pixels[x][y][0] = _v
            self.pixbuf_pixels[x][y][1] = _v
            self.pixbuf_pixels[x][y][2] = _v

        print "  %d points used" % self.points_used

        print "Create Image"
        self.pixbuf = gtk.gdk.pixbuf_new_from_array(self.pixbuf_pixels, gtk.gdk.COLORSPACE_RGB, 8)
        self.image.set_from_pixbuf(self.pixbuf)

        self.drawing = False

    def main(self):
        self.draw(None, None)
        gtk.main()


if __name__ == "__main__":
    app = App()
    app.main()


