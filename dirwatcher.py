import argparse
import datetime
import logging
import os
import signal
import time

__author__ = 'pattersonday pair programmed w/astephens91'

"""Dirwatcher is a program is that watches directories."""

"""Global Variable"""
logger = logging.getLogger(__file__)
magic_text_position = {}
already_found_files_list = []
exit_flag = False


def dir_watcher(args):
    """Monitor given directory and
    log when files are changed in directory"""
    global magic_text_position
    global already_found_files_list

    logger.info('Watching directory: {}, watching magic text: {}, '
                'polling at this many: {}'.format(
                    args.directory, args.magic_text, args.interval))

    # This gets an absolute path to our directory.
    absolute_path = os.path.abspath(args.directory)
    # This creates a list of files in directory.
    files_inside_directory = os.listdir(absolute_path)

    for file in files_inside_directory:
        if file.endswith(args.extension) and file not in already_found_files_list: # NOQA (couldn't break up line)
            logger.info("Hey, this is the: {} within this: {}".format(
                file, args.directory))
            already_found_files_list.append(file)
            magic_text_position[file] = 0

    for file in already_found_files_list:
        if file not in files_inside_directory:
            logger.info("Hey, this: {} has been deleted".format(file))
            already_found_files_list.remove(file)
            del magic_text_position[file]

    for file in already_found_files_list:
        magic_text_finder(file, args.magic_text, absolute_path)


def magic_text_finder(file_name, text_name, directory_itself):
    """Finds magic text within file"""
    global magic_text_position
    global already_found_files_list

    with open(directory_itself + '/' + file_name) as file:
        for line_number, current_line in enumerate(file.readlines(), 1):
            if text_name in current_line and line_number > magic_text_position[file_name]:  # NOQA (couldn't break up line)
                logger.info("Magic text found at line: {}".format(line_number))
            if line_number > magic_text_position[file_name]:
                magic_text_position[file_name] += 1


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT.
    Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets a global flag, and main() will exit it's loop
    if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    global exit_flag

    # log the signal name (the python2 way)
    signames = dict((key, value) for value, key in reversed(sorted(
        signal.__dict__.items()))
        if value.startswith('SIG') and not value.startswith('SIG_'))

    logger.warn('Received ' + signames[sig_num])
    exit_flag = True


def create_parser():
    """Creates an argument parser object"""
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, metavar='',
                        help='file we are searching thru')
    parser.add_argument('magic_text', type=str, metavar='',
                        help='text we are searching for')
    parser.add_argument('-i', '--interval', type=float, default=1,
                        metavar='', help='time interval')
    parser.add_argument('-ext', '--extension', type=str, default='.txt',
                        metavar='',
                        help='what kind of file to search within')

    return parser


def main():
    global exit_flag

    # This is where we setup our parser
    parser = create_parser()
    args = parser.parse_args()

    # This is our logging config
    logging.basicConfig(format='%(asctime)s.%(msecs)03d -'
                        '%(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.DEBUG)

    # Hook these two signals from the OS ..
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called
    # if OS sends either of these to my process.

    start_time_tracker = datetime.datetime.now()
    logger.info(
        "\n"
        "--------------------------------------------------------------\n"
        "       {0} Started\n"
        "       Started at {1}\n"
        "--------------------------------------------------------------\n"
        .format(__file__, start_time_tracker.isoformat())
    )

    while not exit_flag:
        try:
            dir_watcher(args)
        except Exception as err:
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            logger.error("Unhandled exception: {}".format(err))
            # put a sleep inside my while loop so
            # I don't peg the cpu usage at 100%
        except OSError:
            logger.error("This file: {} is not found".format(args.directory))
        except KeyboardInterrupt:
            exit_flag = True

        time.sleep(args.interval)

    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start.

    logged_time = datetime.datetime.now() - start_time_tracker
    logger.info(
        "\n"
        "-----------------------------------------------------------\n"
        "       {0} Shut down\n"
        "       Logged time{1}\n"
        "-----------------------------------------------------------\n"
        .format(__file__, str(logged_time))
    )


if __name__ == '__main__':
    main()
