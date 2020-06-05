"""
This module provide logging function.
Authors: fei(fei.liang@okstate.edu)
Date: 2020/05/25 17:23:06
"""
import os
import logging
import logging.handlers

"""
init_log - initialize log module
Args:
log_path - Log file path prefix.
Log data will go to two files: log_path.log and log_path.log.wf
Any non-exist parent directories will be created automatically
level - msg above the level will be displayed
DEBUG < INFO < WARNING < ERROR < CRITICAL
the default value is logging.INFO
when - how to split the log file by time interval
'S' : Seconds
'M' : Minutes
'H' : Hours
'D' : Days
'W' : Week day
default value: 'D'
format - format of the log
default format:
%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s INFO: 12-09 18:02:42: log.py:40 * 139814749787872 HELLO WORLD
backup - how many backup file to keep
default value: 7
     Raises:
     OSError: fail to create log directories
     IOError: fail to open log file
     """
default_log_dir = "./log/my_program"
def init_log(log_path, level=logging.INFO, when="D", backup=7,
             format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s", datefmt="%m-%d %H:%M:%S"):
    formatter = logging.Formatter(format, datefmt)
    logger = logging.getLogger()
    logger.setLevel(level)
    dir = os.path.dirname(log_path)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log", when=when, backupCount=backup)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log.waring", when=when, backupCount=backup)
    handler.setLevel(logging.WARNING)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    f_handler = logging.handlers.TimedRotatingFileHandler(log_path + "log.error", when=when, backupCount=backup)
    f_handler.setLevel(logging.ERROR)
    f_handler.setFormatter(formatter)
    logger.addHandler(f_handler)

if __name__ == "__main__":
    init_log("./log/my_program")  # ./log/my_program.log./log/my_program.log.wf7
    logging.info("Hello World!!!")