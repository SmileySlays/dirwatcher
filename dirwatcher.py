import signal
import os
import time
import datetime
import logging
import argparse
import sys

__author__ = 'SmileySlays'

"""
Program watches direct for a string and logs instance of string,
files added/removed, and any errors.
"""

signames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                if v.startswith('SIG') and not v.startswith('SIG_'))

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("dirwatcher.log")
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

exit_flag = False
watcher_start_time = datetime.datetime.now()


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT.
    Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets a global flag,
    and main() will exit it's loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name (the python3 way)
    # logger.warn('Received ' + signal.Signals(sig_num).name)
    # log the signal name (the python2 way)
    global exit_flag
    logger.warn('Received ' + signames[sig_num])
    exit_flag = True


def watch_directory(directory, string, extension):
    """Watches a directory for changes"""
    dir_path = os.path.join(os.getcwd(), directory)
    os.chdir(dir_path)
    current = dict([(file, 0) for file in os.listdir(dir_path)
                    if file.endswith(extension)])
    while 1:
        time.sleep(3)
        updated_dir = {dir_ for dir_ in set(os.listdir(dir_path))
                       if dir_.endswith(extension)}
        current = detect_removed_files(current, updated_dir)
        detect_added_files(current, updated_dir)
        magic_string(current, string)


def detect_added_files(current, updated_dir):
    """Logs any files added"""
    for name_file in updated_dir:
        if name_file in current:
            continue
        else:
            current[name_file] = 0
            logger.info("{} added to dirwatcher".format(name_file))


def detect_removed_files(current, updated_dir):
    """Logs any files removed"""
    temp_dict = {}
    for current_file in current:
        if current_file not in updated_dir:
            logger.info("{} removed from dirwatcher".format(current_file))
        else:
            temp_dict[current_file] = current[current_file]
    return temp_dict


def magic_string(current, string):
    """Logs magic string"""
    for file in current:
        try:
            with open(file, 'r') as f:
                index = 1
                for line in f:
                    if string in line and current[file] < index:
                        current[file] = index
                        logger.info("Line {} found {} in {}".format
                                    (index, string, file))
                    index += 1
        except Exception:
            pass


def create_parser():
    """
    Creates parsers for the magic string, directory path,
    extension, and time interval.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-interval", type=float, default=5,
                        help="time between dir watcher sprint")
    parser.add_argument("magic", help="searching string")
    parser.add_argument("-extension", type=str, default=".txt",
                        help="extension for files to search")
    parser.add_argument("path", help="directory watching")
    return parser


def main(args):
    """
    Hooks up the signal, creates start and end banners in log
    if there is no exit flag
    """
    # Hook these two signals from the OS ..
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends either
    # of these to my process.
    uptime = datetime.datetime.now() - watcher_start_time
    parser = create_parser()
    args = parser.parse_args()
    polling_interval = args.interval
    logger.info(
        '\n'
        '----------------------------------------------------\n'
        '   Running Dirwatcher on {}\n'
        '----------------------------------------------------\n'
        .format(args.path)
    )

    while not exit_flag:
        try:
            # call my directory watching function..
            watch_directory(args.path, args.magic, args.extension)
        except Exception as e:
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            logger.error("unhandled exception {}".format(e))

            # put a sleep inside my while loop so
            # I don't peg the cpu usage at 100%
            time.sleep(polling_interval)
    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start.
    logger.info(
        '\n'
        '----------------------------------------------------\n'
        '   Stopped {0}\n'
        '   Uptime was {1}\n'
        '----------------------------------------------------\n'
        .format(__file__, str(uptime))
    )


if __name__ == '__main__':
    main(sys.argv[1:])
