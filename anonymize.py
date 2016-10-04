# Core modules
import base64
import datetime
import hashlib
import os

# 3rd party modules
import dicom

# Constants
NUM_LAYERS = 447
ORIGINAL_DATA = "data/04231972/20121220/2.16.840.114421.80129.9409311810.9440847810/"

# Calculate directory into which will be written the anonymized data
dt = datetime.datetime.now()
# Note: this does not anonymize my birthday...
NEW_DATA      = "data/04231972/%04d%02d%02d/2.16.840.114421.80129.9409311810.9440847810/" %  (dt.year, dt.month, dt.day)

# Don't display huge values
DISPLAY_BLACK_LIST   = [ (0x7fe0, 0x0010)]

# For de-identification purposes, don't include these fields
INCLUSION_BLACK_LIST = [ (0x0010, 0x0030), # PatientComments
                         (0x0010, 0x0010), # PatientName
                         (0x0008, 0x1010), # StationName
                         (0x0010, 0x0020)  # PatientID
                       ]

def build_file_name(directory, layer):
    """Helper to build a file name from a root directory and an image layer.
    Arguments:
    directory -- String.  Root directory.
    layer - int.  The layer number.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    return "%s%04d.dcm" % (directory, (NUM_LAYERS-layer))

def load_and_print_representative_layer(l):
        """Loads a DICOM layer file and prints the metadata, obfuscating certain values.
        Arguments:
        l -- int.  The layer to be printed.
        """
        dataset = dicom.read_file(build_file_name(ORIGINAL_DATA, l))
        ks = dataset.keys()
        for k in ks:
            try:
                i = dataset[k]
                if i and i.tag in DISPLAY_BLACK_LIST:
                    i.value = "< NOT DISPLAYED >"
                print i
            except Exception as e:
                print k, None
        print "=========================\n\n"

def anonymize_all_datasets():
    """Loads and de-identifies all layers in a DICOM study.
    Arguments:
    None
    """
    # Shorthand for unidirectionally hashing and Base64 encoding a string
    _h = lambda s : base64.b64encode(hashlib.sha1(s).digest())

    for l in range(0, NUM_LAYERS+1):
        original_filename = build_file_name(ORIGINAL_DATA, l)
        new_filename      = build_file_name(NEW_DATA,      l)
        print " Layer#", l
        print "   Original:", original_filename
        print "   New     :", new_filename
        dataset = dicom.read_file(original_filename)
        ks = dataset.keys()
        for k in ks:
            try:
                i = dataset[k]
                if i and i.tag in INCLUSION_BLACK_LIST:
                    i.value = _h(i.value)
                    print '      REPLACED', k, i
            except Exception as e:
                print "EXCEPTION:", e
        print "    SAVING %s ..."
        dataset.save_as(new_filename)
        print "=========================\n\n"

class _getch:
    """Small helper class which creates a getch() function.
    Arguments:
    None
    """
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

if __name__ == "__main__":
    load_and_print_representative_layer(int(NUM_LAYERS/2))
    print "Anonymize? [n/Y]"
    c = _getch()()
    if c == 'Y':  anonymize_all_datasets()
    else:         print "'Y' not pressed.  Exiting..."


