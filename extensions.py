import logging
import sys
from typing import Tuple

dummyLogger = logging.getLogger('Dummy')
dummyLogger.addHandler(logging.NullHandler())


def setup_root_logger_format(level=logging.INFO):
    """
    :param level: logging level.
    """
    logging.basicConfig(format='[%(asctime)s][%(process)d][%(levelname)s]'
                               '[%(name)s.%(funcName)s: %(lineno)d] : %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S %z',
                        level=level)


class LevelFilter(logging.Filter):
    """ A filter that accepts one or more logging levels in the constructor,
     all levels not included in the filter will be discarded.

    example:
    >>> sh_out = logging.StreamHandler(sys.stdout)
    >>> sh_out.addFilter(LevelFilter(logging.INFO))
    """
    def __init__(self, *levels: [int, Tuple[int]]):
        super(LevelFilter, self).__init__('level_filter')
        self.levels = levels

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno in self.levels
