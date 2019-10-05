# x3i_extract
This is a simple script that takes a .xci and breaks it into x3f files.

It's useful if you don't want to manually extract them without spp tools. It's very fast because it does not do any processing. It reads the header, finds the embedded files, and then writes them to disk. This should then be paired with the python xcf_extract or another x3f program inorder to do anything with the extracted files.

Supported OS (As in I tested it):
1. Windows 10
2. Linux

Python Requirments:
1. Python 3.6 or later
2. Collections

To run the script:

x3i_extract <filename.xci>

Example output:
C:\test_folder> x3i_extract.py _DQH0709.X3I

Version:  bytearray(b'\x00\x01\x00\x00')
UID: b'\x01\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x000120'
Identifier: b'SECf'
Version: bytearray(b'\x00\x00\x01\x00')
Num Entries: 8
**** **** **** **** **** **** **** **** **** **** ****
**** **** **** **** **** **** **** **** **** **** ****
**** **** **** **** **** **** **** **** **** **** ****
