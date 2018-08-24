# -*- coding: utf-8 -*-

import argparse
import re
import logging

from Common.Convertion import Convertion
from Common.Common import Common


def check_characters(program, footer_header=False):
    permissible_code = [0x00, 0x0a, 0x0d, 0x20, 0x2b, 0x2f, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39,\
                        0x41, 0x43, 0x44, 0x46, 0x47, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e, 0x52, 0x53, 0x54, 0x55, 0x56,\
                        0x57, 0x58, 0x59, 0x5a]
    pc = [chr(i) for i in permissible_code]
    permissible_code_header_footer = [0x24, 0x25, 0x26, 0x28, 0x29, 0x3f, 0x42, 0x45, 0x50]
    pchf = [chr(i) for i in permissible_code_header_footer]

    for c in program:
        flag = False
        flag = flag or c in pc
        if footer_header:
            flag = flag or c in pchf
        if not flag:
            logging.warning('Not permissible code character found: %s, %s', c, hex(ord(c)))



def calulate_checksum(program):
    print program
    sum = 0
    cleaned_program = re.sub(r'(\r|\n|\s)', '', program)

    for c in cleaned_program:
        print c, hex(ord(c))
        sum += ord(c)
    print sum

    calculate_checksum = "%.4X" % sum
    return calculate_checksum

def calulate_memory_load(program):
    cleaned_program = re.sub(r'(\r|\n|\s)', '', program)
    len_cleaned_program = len(cleaned_program)
    memory_load = "%.4X" % len_cleaned_program
    return memory_load

def correct_and_check_spindle_speed(line):
    def __convert_to_correct_speed_representation(num_str):
        ALLOWED_SPINDLE_SPEEDS = [0, 31, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150]
        c = float(num_str)
        c_int = int(c)
        if Convertion.is_round_error(c, c_int):
            logging.warning('Losing spindle speed decimals: %d, %s' % (c, c_int))
        if c_int not in ALLOWED_SPINDLE_SPEEDS:
            logging.warning('Spindle speed not allowed: %s' %num_str)
        result = '{:+d}'.format(c_int)
        return result

    sub_line = line
    offset = 0
    for m in re.finditer(r'S-?\d+\.\d+', line):
        num_str = line[m.start()+1:m.end()]
        converted_num_str = __convert_to_correct_speed_representation(num_str)
        sub_line = Common.replace_string(sub_line, (m.start()+1+offset, m.end()+offset), converted_num_str)
        offset += len(converted_num_str) - (m.end()-m.start()-1)
    return sub_line

def correct_coordinate_representation(line):
    def __convert_to_correct_coordinate_representation(num_str):
        c = float(num_str)*1000
        c_int = int(c)
        if Convertion.is_round_error(c, c_int):
            logging.warning('Losing coordinate decimals: %d, %s' % (c, c_int))
        result = '{:+d}'.format(c_int)
        return result

    sub_line = line
    offset = 0
    for m in re.finditer(r'(X|Y|Z|I|J|K|W)-?\d+\.\d+', line):
        # print '%02d-%02d: %s' % (m.start(), m.end(), m.group(0))
        converted = __convert_to_correct_coordinate_representation(line[m.start() + 1:m.end()])
        sub_line = Common.replace_string(sub_line, (m.start()+1+offset, m.end()+offset), converted)
        offset += len(converted) - (m.end()-m.start()-1)
    return sub_line

parser = argparse.ArgumentParser(description="Dialog Postprocessor for CamBam")
parser.add_argument('-i', '--input', help="nc file for input", required=True)
parser.add_argument('-o', '--output', help="nc file for outfile", required=True)
args = parser.parse_args()
print(args.input)

with open(args.input, 'r') as i:
    for line in i:
        outline = correct_coordinate_representation(line)
        outline = correct_and_check_spindle_speed(outline)
        # print outline
    routine = "&P01\r\n\
D01 +010000\r\n\
\r\n\
\r\n\
\r\n\
\r\n\
(&P01/0053)\r\n\
N0001 G00 X+0 Y+0 Z+100000\r\n\
N0002 T01\r\n\
N0003 G00 Z+0 D+01\r\n\
N0004 G01 X+100000 Y+50000 F500 S+0\r\n\
N0005 M30\r\n\
\r\n\
?"
    programm = "N0001 G00 X+0 Y+0 Z+100000\r\n\
N0002 T01\r\n\
N0003 G00 Z+0 D+01\r\n\
N0004 G01 X+100000 Y+50000 F500 S+0\r\n\
N0005 M30\r\n\
\r\n\
"

    print check_characters(routine, True)
    # print calulate_memory_load(routine)
    print calulate_checksum(programm)


