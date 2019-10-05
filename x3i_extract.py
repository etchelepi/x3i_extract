#from typing import NamedTuple
import collections
import sys
import os

#CONSTANTS
HEADER_FOVB = b'FOVb'
HEADER_FOVI = b'FOVi'
DIRECTORY_SECD = b'SECd'
DIRECTORY_SECI = b'SECi'
DIRECTORY_SECP = b'SECp'
DIRECTORY_SECC = b'SECc'
#X3I Specific Header Information:
DIRECTORY_FRAM = b'FRAM'

HEADER_UNIQUE_IDENTIFER = 16
X3F_IMAGE_RAW_SDQH = 65575 #0x00010027

def byte_to_int(data):
	temp = 0;
	length = len(data)
	for x in range(0,length):
		temp = temp * 256
		temp = temp + data[x]
	return temp

def l_endian(data):
	length = len(data)
	temp = bytearray(length);
	for x in range(0,length):
		temp[x] = data[(length-1)-x]
	return temp

#Checks the header for the FOV 4 byte ID
def validate_x3f_header(data):
	if data != HEADER_FOVB:
		print ("The header should start with",HEADER_FOVB,"\nBut header started with",data)
		sys.exit(0)
        
#Checks the header for the FOV 4 byte ID
def validate_xif_header(data):
	if data != HEADER_FOVI:
		print ("The header should start with",HEADER_FOVI,"\nBut header started with",data)
		sys.exit(0)
        
#When this Function is complete it will check against a list of valid versions
#And Error out if it's unsupported. Currently it just prints it.
def validate_version(data):
	print("Version: ",l_endian(data))
	return data

def validate_unique_id(data):
	print("UID:", data)
	return data

#Transverse the Directory header to create a list of the info inside a directory
def get_directory_struct(file_pointer):
	file_pointer.seek(-4, 2) #BYTE LOCATION is -4 from the end (Specified by 2)
	offset = byte_to_int(l_endian(file_pointer.read(4)))
	file_pointer.seek(offset, 0) #Traverse to the Offset
	section_identifer = file.read(4) #Get the Identifier
	#Get the Version
	dir_version = l_endian(file.read(4))
	print("Version: ",end='')
	print(dir_version)
	#Get the NUM entries
	num_dir_enteries = byte_to_int(l_endian(file.read(4)))
	print("Num Entries: ",end='')
	print(num_dir_enteries)
	print("**** **** **** **** **** **** **** **** **** **** ****")
	#Traverse the Directory
	dir_entry = []
	x3f_dir_entry = collections.namedtuple('x3f_dir_entry', ['offset', 'size', 'dirtype'])
	for x in range(0, num_dir_enteries):
		OFFSET = byte_to_int(l_endian(file.read(4)))
		SIZE = byte_to_int(l_endian(file.read(4)))
		TYPE = file.read(4)
		entry = x3f_dir_entry(offset = OFFSET,size = SIZE, dirtype = TYPE)
		dir_entry.append(entry)
	print("**** **** **** **** **** **** **** **** **** **** ****")

#Confirm a file is provided.
if len(sys.argv) > 1:
	input_filename = sys.argv[1]
	input_extension = str(os.path.splitext(input_filename)[1])
	if input_extension != '.X3I' and input_extension != '.x3i':
		print("SUPPORT FOR .X3I FILES ONLY. Filetype was:",input_extension)
		sys.exit(0)
else:
	print("NO FILE SPECIFIED")
	sys.exit(0)

#Open the XCI file for reading. The file will tell us how to
#navigate to the sections where the data we care about live
with open(input_filename,"rb") as file:
	file.seek(0, 0) #Go to the start of the file
	validate_xif_header(file.read(4))	#Bytes 0x00 to 0x04 are the header
	validate_version(file.read(4)) 	    #Bytes 0x05 to 0x08 are the version
	validate_unique_id(file.read(HEADER_UNIQUE_IDENTIFER))
	#TODO: THE REST OF THE HEADER


	#Now get the directory location in the file
	file.seek(-4, 2) #BYTE LOCATION is -4 from the end (Specified by 2)
	directory_offset = byte_to_int(l_endian(file.read(4)))
	file.seek(directory_offset, 0) #Traverse to the Offset
	#Get the Identifier
	print("Identifier: ",end='')
	section_identifer = file.read(4)
	print(section_identifer)
	#Get the Version
	dir_version = l_endian(file.read(4))
	print("Version: ",end='')
	print(dir_version)
	#Get the NUM entries
	num_dir_enteries = byte_to_int(l_endian(file.read(4)))
	print("Num Entries: ",end='')
	print(num_dir_enteries)
	print("**** **** **** **** **** **** **** **** **** **** ****")
	#Tranverse the Directory
	dir_entry = []
	x3f_dir_entry = collections.namedtuple('x3f_dir_entry', ['offset', 'size', 'dirtype'])
	for x in range(0, num_dir_enteries):
		OFFSET = byte_to_int(l_endian(file.read(4)))
		SIZE = byte_to_int(l_endian(file.read(4)))
		TYPE = file.read(4)
		entry = x3f_dir_entry(offset = OFFSET,size = SIZE, dirtype = TYPE)
		dir_entry.append(entry)
	print("**** **** **** **** **** **** **** **** **** **** ****")
	#Print the dir table contents
	for x in range(0, len(dir_entry)):
		#If the DIR type is a FRAME go to it
		if dir_entry[x].dirtype == DIRECTORY_FRAM:
			#Set the file pointer to the directory
			file.seek(dir_entry[x].offset, 0)
			#Read the contents into a varaible
			cur_x3i_data = file.read(dir_entry[x].size)
			f_name = (os.path.splitext(input_filename)[0])+"_"+str(x-3)+".X3F"
			x3i_file_handle = open(f_name, 'wb')
			x3i_file_handle.write(cur_x3i_data)
			x3i_file_handle.close()
	print("**** **** **** **** **** **** **** **** **** **** ****")
			


