#!/usr/local/bin/python2.7
# encoding: utf-8
'''
ui -- shortdesc

ui is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2017 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os
import serial
import struct

from time import time
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2017-02-10'
__updated__ = '2017-02-10'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

def start_command(ser, rate, target):
    msg = struct.pack('=BffB',
                       0xFC,
                       rate,
                       target,
                       0xCF)
    ser.write(msg)
    print(' '.join('{:02x}'.format(x) for x in msg))
    
def stop_command(ser):
    ser.write(struct.pack('B'), 0xAB)
    
def read_message(ser):
    while True:
        x = struct.unpack('B', ser.read())[0]
        if x == 0x55:
            return 0x55, ser.readline().decode('utf-8')
        if x in [0x21, 0x22, 0x24, 0x28, 0x31, 0x32]:
            return x, struct.unpack('f', ser.read(4))[0]
        if x in [0x11, 0x12, 0x14, 0xFF]:
            return x, None

message_strings = {
                   0x11: 'Started Ramp',
                   0x12: 'Cancelled Ramp',
                   0x14: 'Ramp Complete',
                   0x21: 'Temp',
                   0x22: 'Filtered Temp',
                   0x24: 'Rate',
                   0x28: 'Filtered Rate',
                   0x31: 'Control Error',
                   0x32: 'Control Output'
                   }

def print_message(x, msg):
    if x == 0x21:
        print('{}: {}'.format(message_strings[x], msg))
    return

    if x > 0x20 and x < 0x50:
        print('{}: {}'.format(message_strings[x], msg))
    elif x > 0x50:
        print(msg)
    else:
        print(message_strings[x])
                       
class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2017 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]", default=0)
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-m', '--monitor-only', action='store_true', dest='monitor', default=False)
        
        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose

        if verbose > 0:
            print("Verbose mode on")

        ser = serial.Serial('/dev/ttyUSB0', 115200)
        
        temp = 0
        while temp == 0:
            x, msg = read_message(ser)
            print_message(x, msg)
            if x == 0x22:
                temp = msg
            
        if not args.monitor:        
            start_command(ser, 0.5, 150)
        
            timeout_start = 0
        
            while True:
                x, msg = read_message(ser)
                print_message(x, msg)
                if x == 0x14:
                    timeout_start = time()
                    print("Soak")
                if timeout_start > 0 and time() - timeout_start > 120:
                    break
            
            start_command(ser, 0.5, 220)
            
            timeout_start = 0
        
            while True:
                x, msg = read_message(ser)
                print_message(x, msg)
                if x == 0x14:
                    timeout_start = time()
                    print("Flow")
                if timeout_start > 0 and time() - timeout_start > 75:
                    break
            print("Done")
            
        else:
            while True:
                pass
        return 0
    except KeyboardInterrupt:
        msg = struct.pack('B', 0xAB)
        ser.write(msg)
        return 0
    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'ui_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())