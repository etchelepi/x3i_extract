###############################################################################
# Includes needed for this to work
###############################################################################
import os
import collections
import sys
import glob
import argparse

###############################################################################
# Constants we need for this to work
###############################################################################

#CONSTANTS
HEADER_FOVB = b'FOVb'
HEADER_FOVI = b'FOVi'
#X3I Specific Header Information:
DIRECTORY_FRAM = b'FRAM'

HEADER_UNIQUE_IDENTIFER = 16

###############################################################################
# Global Variables
###############################################################################
X3F_EXTRACT_EXE             = "x3f_extract.exe" #Please put the path to the x3f Extract tool
X3F_EXTRACT_TIF_ARGS        = " -tiff " #This is 16 bit linear TIF
X3F_EXTRACT_DNG_ARGS        = " -dng "

#Download LuminanceHDR and point to the Install. Or add it to the path. You can swap out a different tool, but these settings are from using LumianceHDR
HDR_TOOL_EXE                = "luminance-hdr-cli.exe"
HDR_TOOL_ARGS               = "--autoag 1.0 --hdrWeight gaussian --align MTB"
HDR_TOOL_TONE_MAP_ARGS      = "-q 90 --autolevels --tmo reinhard05 --tmoR05Brightness 0.0 --tmoR05Chroma 0.1 --tmoR05Lightness 1.0"

###############################################################################
# Helpful functions
###############################################################################

###############################################################################
# Convert a byte string to an integer
def byte_to_int(data):
    temp = 0;
    length = len(data)
    for x in range(0,length):
        temp = temp * 256
        temp = temp + data[x]
    return temp

###############################################################################
#Convert data into little endian
def l_endian(data):
    length = len(data)
    temp = bytearray(length);
    for x in range(0,length):
        temp[x] = data[(length-1)-x]
    return temp
  
###############################################################################
#Convert data into little endian
def signed_to_str(signed_num):
    if(signed_num < 0):
        rtn_str = str(signed_num)
    elif(signed_num > 0):
        rtn_str = "+" + str(signed_num)
    else:
        rtn_str = "_0"
        
    return rtn_str
    
###############################################################################
# When you want to start at zero, THEN negative numbers, THEN positives 
def index_str_list(num_enteries):
    index_list = []
    
    index_list.append(signed_to_str(0))
    
    index_end   = int((num_enteries + num_enteries%2) /2)
    index_start = int(num_enteries/2) - (num_enteries - num_enteries%2)
    
    for x in range (index_start,index_end):
        if(x != 0):
            index_list.append(signed_to_str(x))
            
    return index_list

###############################################################################
# Takes an argument. Use GLOB to get a list
def get_file_list(argument):
    
    file_list = []
    
    if(argument != None): #Check that it's a real arguments
        
        for i in  argument:
            tmp_list = glob.glob(i)
            for f in tmp_list:
                f_name, f_ext = os.path.splitext(os.path.basename(f))
                if( f_ext.lower() == ".x3i"):
                    file_list.append(f)
        
    return file_list;
    
###############################################################################
# X3F/X3I specific functions
###############################################################################


###############################################################################
#Checks the header for the FOV 4 byte ID
def validate_header(data,tag):
    if ((data != tag)):
        print ("ERROR: \n The header should start with %s for normal or %s for X3I's.\n Got: %s\n"%(HEADER_FOVB,HEADER_FOVI,data))
        sys.exit(0)

###############################################################################
# TODO: check against supported versions and error out if not supported
def validate_version(data):
    print("Version: ",l_endian(data))
    return data
    
###############################################################################
# Verify the UID
def validate_unique_id(data):
    print("UID:", data)
    return data
    
###############################################################################
# Get Directory Entry
def get_directory_struct(file_pointer,verbose):
    x3f_dir_entry = collections.namedtuple('x3f_dir_entry', ['offset', 'size', 'dirtype'])
    
    OFFSET = byte_to_int(l_endian(file_pointer.read(4)))
    SIZE = byte_to_int(l_endian(file_pointer.read(4)))
    TYPE = file_pointer.read(4)
    
    if(verbose):
        print("\t\tOFFSET IS: %d\n\t\tSIZE is: %d\n\t\tTYPE is: %s\n"%(OFFSET,SIZE,TYPE))
    
    entry = x3f_dir_entry(offset = OFFSET,size = SIZE, dirtype = TYPE)
    
    return entry
    
###############################################################################
# Get Directory Table
def get_directory_table(file_pointer,verbose):
    num_dir_enteries = byte_to_int(l_endian(file_pointer.read(4)))
    if(verbose):
        print("Starting Directory Table Extraction for %d entries \n"%(num_dir_enteries))
    
    dir_table = []
    
    for x in range(0, num_dir_enteries):
        if(verbose):
            print("\tENTRY %2d **** **** **** **** **** **** **** ****"%(x))
        entry = get_directory_struct(file_pointer,verbose)
        dir_table.append(entry)
        
    return dir_table
  

###############################################################################
# Get Directory Table
def process_hdr(file_list,EV_list,result_name,preview=False):
    HDR_OUT_FILE        = result_name + ".EXR"
    HDR_PREVIEW_FILE    = result_name + ".JPG"
    HDR_IN_FILES        = ""
    
    for i in file_list:
        HDR_IN_FILES    = HDR_IN_FILES + " " + i
        
    for e in range (0,len(EV_list)):
        if(e == 0):
            HDR_EVS = str(EV_list[e])
        else:
            HDR_EVS = HDR_EVS + "," + str(EV_list[e])
            
    
    HDR_CMD = HDR_TOOL_EXE + " " + HDR_TOOL_ARGS + " --ev " + HDR_EVS
    if(preview):
        HDR_CMD = HDR_CMD + " " + HDR_TOOL_TONE_MAP_ARGS + " -o " + HDR_PREVIEW_FILE
    
    HDR_CMD = HDR_CMD + " -s " + HDR_OUT_FILE + " " + HDR_IN_FILES
    
    
    print(HDR_CMD)
    os.system(HDR_CMD)
  
###############################################################################
# Extract the X3F's from the X3I
def extract_x3i_file(x3i_file,x3f=True,tif=False,dng=False,hdr=False,verbose=False):
    
    #Check the filename:
    input_extension = str(os.path.splitext(x3i_file)[1])
    base_fname      = os.path.splitext(x3i_file)[0]
    
    if (input_extension.lower() != '.x3i'):
        print("SUPPORT FOR .X3I FILES ONLY. File type was: %s",input_extension)
        return 0
        
    #We process the file
    with open(x3i_file,"rb") as file:
        file.seek(0, 0)                                         #Go to the start of the file
        validate_header(file.read(4),HEADER_FOVI)               #Bytes 0x00 to 0x04 are the header
        validate_version(file.read(4))
        validate_unique_id(file.read(HEADER_UNIQUE_IDENTIFER))
        #TODO: THE REST OF THE HEADER
    
        #Now get the directory location in the file
        file.seek(-4, 2)                                        # BYTE LOCATION is -4 from the end (Specified by 2)
        directory_offset        = byte_to_int(l_endian(file.read(4)))
        file.seek(directory_offset, 0)                          #Traverse to the Offset
        section_identifer       = file.read(4)                  #Get the section identifier 
        dir_version             = l_endian(file.read(4))        #Get the Version
        if(verbose):
            print("**** **** **** **** **** **** **** **** **** **** ****")
            print("Section Identifier   : %s"%(section_identifer))
            print("Directory Version    : %s"%(dir_version))
            print("**** **** **** **** **** **** **** **** **** **** ****")
        #Get the Directory Table
        dir_entry = get_directory_table(file,verbose)
        #Extract the X3I content - We have to do this regardless
        #Count the number of frames
        frame_cnt = 0
        for x in range(0, len(dir_entry)):
            if dir_entry[x].dirtype == DIRECTORY_FRAM:
                frame_cnt = frame_cnt + 1
        index_list = index_str_list(frame_cnt)
        
        FRAME_INDEX = 0
        DNG_LIST = []
        X3F_LIST = []
        EX_LIST = [0,-3,-2,-1,1,2,3]                            #TODO: This should be cacualted not hard coded. But whatever
        
        if(verbose):
            print("Exporting to Disk...")
            
        #Loop To Extract all the files. We do it in a loop so if a user doesn't want all the outputs possible
        #We can erase them and save working disk space
        for x in range(0, len(dir_entry)):
            if dir_entry[x].dirtype == DIRECTORY_FRAM:          #If the DIR type is a FRAME process it
                #Setup the Output Filename
                X3F_FILE_NAME = base_fname + "_" + index_list[FRAME_INDEX] + ".X3F"
                FRAME_INDEX = FRAME_INDEX + 1;
                if(verbose):
                    print("Filename: %s\n "%(X3F_FILE_NAME))
                #Goto the File Location
                file.seek(dir_entry[x].offset, 0)
                cur_x3i_data        = file.read(dir_entry[x].size)
                x3i_file_handle     = open(X3F_FILE_NAME, 'wb')
                x3i_file_handle.write(cur_x3i_data)
                x3i_file_handle.close()
                X3F_LIST.append(X3F_FILE_NAME)                  #Save the Filename we wrote out
                #Handle Additional Conversions
                X3F_ARGS = ""
                if(tif == True):
                    X3F_ARGS = X3F_ARGS + X3F_EXTRACT_TIF_ARGS
                if(hdr == True or dng == True):
                    X3F_ARGS = X3F_ARGS + X3F_EXTRACT_DNG_ARGS
                    DNG_LIST.append(X3F_FILE_NAME + ".dng")
                    
                if(tif == True or dng == True):  #Use X3F to convert                           
                    if(verbose):
                        X3F_CMD = X3F_EXTRACT_EXE + X3F_ARGS + " -v " + X3F_FILE_NAME
                        print(X3F_CMD)
                    else:
                        X3F_CMD = X3F_EXTRACT_EXE + X3F_ARGS + X3F_FILE_NAME
                        
                    os.system(X3F_CMD)
                    if(dng == True):
                        if(x3f == False):                           #Erase file if X3F isn't also True
                            os.remove(X3F_FILE_NAME) 
        #Loop Finished
        
        #Is there an HDR list we want to do
        if(hdr):
            if(dng == True):
                process_hdr(DNG_LIST,EX_LIST,base_fname,True)
            else:
                process_hdr(X3F_LIST,EX_LIST,base_fname,True)
                #Clean Up Files
                if(x3f == False):                                   #Erase file if X3F isn't also True
                    for f in X3F_LIST:
                        print(f)
                        os.remove(f) 
            
    #We have finished processing for this X3I
    return 1

###############################################################################
# THE PROGRAM BEGINS
###############################################################################
def main():
    """ MAIN
    """
    print("X3I Extract Utility\n")
    
    #Get Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--input','-i',nargs='*',required=True,      help='provide a file or a list of files (GLOB strings allows)')
    parser.add_argument('--tif',default=False,action='store_true',  help='Convert images to TIF. This requires the script to have a path to the x3f extract Util')
    parser.add_argument('--x3f',default=False,action='store_true',  help='save the X3F output')
    parser.add_argument('--dng',default=False,action='store_true',  help='Use Hugin to Create an HDR single image')
    parser.add_argument('--hdr',default=False,action='store_true',  help='Use Hugin to Create an HDR single image')
    parser.add_argument('--verbose','-v',default=False,action='store_true',  help='Verbose Output')
    args = parser.parse_args()

    IN_FILE_LIST    = get_file_list(args.input)
    OUT_TIFF        = args.tif
    OUT_X3F         = args.x3f
    OUT_HDR         = args.hdr
    OUT_DNG         = args.dng
    VERBOSE         = args.verbose
    
    #For HDR, this works on the Assumption that the Tool CAN support .X3F files. BUT because many tools support them wrong,
    #If you have a fixed X3F Extract the DNG output can be used instead.
    if(OUT_HDR == True):
        #FIrst Check if we have an HDR tool:
        if(os.path.isfile(HDR_TOOL_EXE) == False):
            print("ERROR: There is no valid HDR tool set at %s, either add it to the PATH or modify the line for HDR_TOOL_EXE in this script"%(HDR_TOOL_EXE))
            exit(-1)
        #Check if -DNG is being used with it.
        if(OUT_DNG == True):
            if(os.path.isfile(X3F_EXTRACT_EXE) == False ):
                print("ERROR: the DNG flag with the HDR flag implies to use DNG's for the HDR instead of X3F's.")
                print("This requires that X3F_EXTRACT_EXE is either set in the script or in the PATH. It's Currently set to %s"%(X3F_EXTRACT_EXE))
                exit(-1)
            
            
    if(OUT_TIFF == True or OUT_DNG == True ):
        if(os.path.isfile(X3F_EXTRACT_EXE) == False or os.path.isfile(HDR_TOOL_EXE) == False):
            print("ERROR: output mode",end='')
            if(OUT_TIFF):
                print("TIFF ",end='')
            if(OUT_DNG):
                print("DNG ",end='')
            print("but the path %s to the x3f conversion tool is not set correctly"%(X3F_EXTRACT_EXE))
            print("This requires that X3F_EXTRACT_EXE is either set in the script or in the PATH. It's Currently set to %s"%(X3F_EXTRACT_EXE))
            exit(-1)
    else:
        if(OUT_HDR != True):
            OUT_X3F = True
          
    #For each X3F provided as input process it
    for f in IN_FILE_LIST:
        extract_x3i_file(f,OUT_X3F,OUT_TIFF,OUT_DNG,OUT_HDR,VERBOSE)
        
    print("\nAll files completed\n")
        
       
if __name__ == '__main__':
    sys.exit(main())