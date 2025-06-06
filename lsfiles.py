#!/usr/bin/env python3
#

"""
lsfiles.py

List directory contents recursively by file modification time or size.
Prints mtime, file size, and (relative) file path.

"""

import os
import stat
import time
import argparse
from datetime import datetime


def keys_sorted_by(value, dictionary, reverse=False):
    """
    return list of dictionary keys sorted by value (mtime or fsize),
    increasing by default, decreasing if reverse=True
    """

    if value == "mtime":
        result = [(mtime, key) for (key, (mtime, _)) in dictionary.items()]
    elif value == "fsize":
        result = [(fsize, key) for (key, (_, fsize)) in dictionary.items()]
    else:
        raise ValueError("value must be 'mtime' or 'fsize'")

    result.sort(reverse=reverse)
    return [key for (_, key) in result]


def human_readable_size(numbytes):
    "human readable string for size with KB, MB, GB suffix as needed"

    if numbytes < 1000000:
        return f"{numbytes/1000.0:8.2f}KB"
    if numbytes < 1000000000:
        return f"{numbytes/1000000.0:8.2f}MB"
    return f"{numbytes/1000000000.0:8.2f}GB"


def get_args():
    """Parse and return command line arguments"""
    parser = argparse.ArgumentParser(
        description='List directory contents recursively by file modification time or size')
    parser.add_argument('directories', nargs='+', help='One or more directories to process')
    parser.add_argument('--human', action='store_true',
                        help='Show human-readable time and file sizes')

    # Add mutually exclusive group for sorting options
    sort_group = parser.add_mutually_exclusive_group()
    sort_group.add_argument('--bymtime', action='store_true', default=True,
                           help='Sort files by modification time (default)')
    sort_group.add_argument('--bysize', action='store_true',
                           help='Sort files by file size')

    return parser.parse_args()


def get_filedb(directories):
    """Build and return database of file info (mtime, fsize) for given directories"""
    filedb = {}

    for directory in directories:
        for (dirpath, _, filenames) in os.walk(directory):
            for f in filenames:
                filepath = os.path.join(dirpath, f)
                mtime = os.lstat(filepath)[stat.ST_MTIME]
                fsize = os.lstat(filepath)[stat.ST_SIZE]
                filedb[filepath] = (mtime, fsize)

    return filedb


def main():
    """main function"""
    args = get_args()
    filedb = get_filedb(args.directories)

    if args.bysize:
        sort_key = "fsize"
    else:
        sort_key = "mtime"  # default behavior

    for filename in keys_sorted_by(sort_key, filedb, reverse=True):
        mtime, fsize = filedb[filename]

        if args.human:
            time_str = time.ctime(mtime)
            size_str = human_readable_size(fsize)
        else:
            time_str = datetime.fromtimestamp(mtime).isoformat()
            size_str = str(fsize)

        print(f"{time_str} {size_str} {filename}")


if __name__ == '__main__':
    main()
