# x3i_extract
This is a simple script that takes a .xci and breaks it into x3f files.

It's useful if you don't want to manually extract them without spp tools. It's very fast because it does not do any processing. It reads the header, finds the embedded files, and then writes them to disk. This should then be paired with the python xcf_extract or another x3f program inorder to do anything with the extracted files.

Added additional Functionality:

--input can take a single file, or a GLOB search string or a list of files. 
--tif will if a pointer to x3f_extract is modified can convert to tiffs. By default the X3F's will be erased.
--x3f will preserve the extracted x3F files

To add X3F tools look here in the file at the top:

###############################################################################
# Global Variables
###############################################################################
X3F_EXTRACT_EXE = "" #Please put the path to the x3f Extract tool 

X3F_EXTRACT_ARGS = " -tiff " #This is 16 bit linear TIF

Put the full path to the exectuable, and if you want to change what gets run the ARGs needs to be modified.

Supported OS (As in I tested it):
1. Windows 10
2. Linux

Python Requirments:
1. Python 3.6 or later
2. Collections

To run the script:

x3i_extract -i *.x3i --tif

Example output:
C:\test_folder> x3i_extract -i *.x3i --tif

...

X3I Extract Utility

Version:  bytearray(b'\x00\x01\x00\x00')

**** **** **** **** **** **** **** **** **** **** ****

Section Identifier   : b'SECf'
Directory Version    : bytearray(b'\x00\x00\x01\x00')

**** **** **** **** **** **** **** **** **** **** ****
Starting Directory Table Extraction for 8 entries

        ENTRY  0 **** **** **** **** **** **** **** ****
                OFFSET IS: 1440
                SIZE is: 63607028
                TYPE is: b'FRAM'

        ENTRY  1 **** **** **** **** **** **** **** ****
                OFFSET IS: 63608480
                SIZE is: 58430484
                TYPE is: b'FRAM'

        ENTRY  2 **** **** **** **** **** **** **** ****
                OFFSET IS: 122038976
                SIZE is: 58604180
                TYPE is: b'FRAM'

        ENTRY  3 **** **** **** **** **** **** **** ****
                OFFSET IS: 180643168
                SIZE is: 59197076
                TYPE is: b'FRAM'

        ENTRY  4 **** **** **** **** **** **** **** ****
                OFFSET IS: 239840256
                SIZE is: 70731508
                TYPE is: b'FRAM'

        ENTRY  5 **** **** **** **** **** **** **** ****
                OFFSET IS: 310571776
                SIZE is: 75778548
                TYPE is: b'FRAM'

        ENTRY  6 **** **** **** **** **** **** **** ****
                OFFSET IS: 386350336
                SIZE is: 78207412
                TYPE is: b'FRAM'

        ENTRY  7 **** **** **** **** **** **** **** ****
                OFFSET IS: 464557748
                SIZE is: 3956
                TYPE is: b'SPPA'
