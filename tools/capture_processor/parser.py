""" Device data capture processing parser """

from io import BytesIO, StringIO
import re

def parser(infile: StringIO, outfile: BytesIO) -> None:
    """ Extract ASCII bytes representation from files and write as raw bytes to output file """
    pattern = r"^((\d{2}:\d{2}:\d{2})|(\s{8}))\s+[\dA-F]{4}\s+(([\dA-F]{2} )+) (.*)$"
    for line in infile:
        match = re.match(pattern, line)
        if not match or len(match.groups()) < 4:
            continue
        data_string = match.groups()[3]
        data = bytes.fromhex(data_string)
        outfile.write(data)
