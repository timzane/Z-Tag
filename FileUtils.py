import os
import hashlib
import sqlite3
import configparser
import re

# def check_config_file():
#
#
#
#     config_dir=os.getenv("HOME") + "/.config/ztag/"
#     config_file=config_dir + "config.ini"
#
#     print ("Checking..",config_file)
#     if os.path.isfile(config_file):
#         print ("File Exists")
#
#     else:
#
#         print("First Check if dir exists")
#         try:
#             os.stat(config_dir)
#         except:
#             os.mkdir(config_dir)
#
#
#         print("File Does not exist ...Creating")
#         config = configparser.RawConfigParser()
#
#         # When adding sections or items, add them in the reverse order of
#         # how you want them to be displayed in the actual file.
#
#
#         config.add_section('Ztag')
#         config.set('Ztag', 'Version', '0.1.0')
#         config.set('Ztag', 'rootDir', '/home2/Media/2017')
#
#
#         # Writing the config file
#         with open(config_file, 'w') as configfile:
#             config.write(configfile)
                
def read_config_file(Section, Parameter):

    config_file=os.getenv("HOME") + "/.config/ztag/config.ini"
    print ("Checking..",config_file)
    if os.path.isfile(config_file):
        print ("File Exists Opening")

        config = configparser.RawConfigParser()

        config.read(config_file)

        if config.has_option(Section,Parameter):
            
            #print(config.get(Section,Parameter))
            answer = config.get(Section,Parameter)
            return answer
        else:
            print ("Cannot find DB location")
            return None

def write_config_file(Section,Parameter,Value):

    config_file=os.getenv("HOME") + "/.config/ztag/config.ini"
    print ("Checking..",config_file)
    if os.path.isfile(config_file):
        print ("File Exists Opening")

        config = configparser.RawConfigParser()
        config.read(config_file)

        if not config.has_section(Section):
            config.add_section(Section)
        answer = config.set(Section,Parameter,Value)
        print (answer)
        # Writing the config file
        with open(config_file, 'w') as configfile:
            config.write(configfile)

def human_size(size_bytes):
    """
    format a size in bytes into a 'human' file size, e.g. bytes, KB, MB, GB, TB, PB
    Note that bytes/KB will be reported in whole numbers but MB and above will have greater precision
    e.g. 1 byte, 43 bytes, 443 KB, 4.3 MB, 4.43 GB, etc
    """
    if size_bytes == 1:
        # because I really hate unnecessary plurals
        return "1 byte"
    if size_bytes == None:
        return 0

    suffixes_table = [('bytes',0),('KB',0),('MB',1),('GB',2),('TB',2), ('PB',2)]

    num = float(size_bytes)
    for suffix, precision in suffixes_table:
        if num < 1024.0:
            break
        if suffix == 'MB':
            break
        num /= 1024.0

    if precision == 0:
        formatted_size = "%d" % num
    else:
        formatted_size = str(round(num, ndigits=precision))

    #return "%s %s" % (formatted_size, suffix)
    return "%s" % (formatted_size)

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def generate_file_md5(dirName, fname, blocksize=2**20):
    m = hashlib.md5()
    with open( os.path.join(dirName, fname) , "rb" ) as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update( buf )
    return m.hexdigest()

def generate_file_md5_short(dirName, fname, blocksize=2**20):
 
    m = hashlib.md5()
    try:
        with open( os.path.join(dirName, fname) , "rb" ) as f:
            buf = f.read(blocksize)
            m.update( buf )
        return m.hexdigest()
    except:
        return False

def substitute_regex(pattern,replace,string):

    result = re.sub(pattern,replace,string)
    return result

