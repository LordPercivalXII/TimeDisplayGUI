import enum
import logging
import os
import sys
from pathlib import Path
from typing import Literal


class LoggingLevel(enum.Enum):
    """
    LoggingLevel is an enum class used to determine the logging level of the logging activity.
    Alternatively, they can be used for other cases such as testing for specific levels, etc.

    Levels are sorted in terms of their priority.

    """
    DEBUG = (logging.DEBUG, 0)
    INFO = (logging.INFO, 1)
    WARNING = (logging.WARNING, 2)
    ERROR = (logging.ERROR, 3)
    CRITICAL = (logging.CRITICAL, 4)
    EXCEPTION = (logging.ERROR, 5)

    def __init__(self, level: Literal[10, 20, 30, 40, 50], index: int):
        self.level = level
        self.index = index




class LoggerClass:
    """
    A dual function Logger cloning ApprenticeLogger & MasterLogger

    self - ApprenticeLogger Class and Functions
    self.mlog - MasterLogger Class and Functions

    Modified to include logging to console.
    """

    def __init__(self, module_name=None, main_owner=None, additional_context=None, level = logging.INFO):
        self.module_name = module_name
        self.main_owner = main_owner
        self.additional_context = additional_context
        self.level = level

        self.logger = logging.getLogger(self.module_name)

    def info(self, message):
        self.logger.info(message)

    def log(self, message, level = LoggingLevel.INFO):
        self.logger.log(msg=message, level=level.level)

    def debug(self, message):
        self.logger.debug(message)

    def warn(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def set_level(self, level = logging.INFO):
        self.level = level
        self.logger.setLevel(self.level)

    def returnLogger(self):
        return self.logger

    @property
    def get_service_name(self):
        return self.__class__.__name__


def setup_logger(log_file: str, level: int = logging.INFO, mode: str = "a", is_root: bool = False):
    """
    Setup individual logger
    :param log_file: name of log file, without .log extension
    :param level: The logging level associated with this logger (NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL)
    :param mode: The logging mode a OR w - append or write
    :param is_root: Whether the logger should be set as root or not
    :return:
    """


    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )
    handler = logging.FileHandler(os.path.join(Path(__file__).resolve().parent.parent, log_file + ".log"), encoding="utf-8", mode=mode)
    handler.setFormatter(fmt)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)

    logger = logging.getLogger(log_file if not is_root else None)

    if not logger.hasHandlers():
        logger.setLevel(level)
        logger.addHandler(handler)
        logger.addHandler(console_handler)
        logger.propagate = False

