import dicom
import struct
import random
import math

_min =   100
_mid =  1000
_max = 10000

outfile = open('points.asc', 'w')
directory = "data/.../"
# Only process every other one
nums = range(447,0,-2)
for z in nums:
  f = "%s%04d.dcm" % (directory, z)
  print "Processing f", f
  plan   = dicom.read_file(f)
  pixels = struct.unpack("<409600H", plan.PixelData)

  output = ""
  for y in range(640):
      for x in range(640):
          v = pixels[y*640+x]
          _v = 0
          if v > _mid and v < _max: _v = 1
          if v > _min and v <= _mid:
              if random.random() < ((1.0*v - _min)/(_mid - _min)):
                  _v = 1
          if _v:
              output += "%02d %02d %02d\n" % (x, y, z)
  print "   Writing..."
  outfile.write(output)

outfile.close()
