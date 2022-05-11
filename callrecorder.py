import contextlib
import functools
import logging
import types
from threading import Lock
from typing import Callable


@contextlib.contextmanager
def _replace_log_record_factory(new: Callable):
    """ Replacing the factory function that produces logging.LogRecord instances.

    :param new: new callable object

    Example (doctest):
    >>> old_ = logging.getLogRecordFactory()
    >>> new_ = lambda *args, **kwargs: old_(*args, **kwargs)
    >>> with _replace_log_record_factory(new_):
    ...     logging.debug('bla')
    ...     old_ != logging.getLogRecordFactory()
    True
    >>> old_ != logging.getLogRecordFactory()
    False
    """
    old = logging.getLogRecordFactory()
    try:
        logging.setLogRecordFactory(new)
        yield
    finally:
        logging.setLogRecordFactory(old)


class CallRecorder:

    _lock = Lock()

    def __init__(self, logger_object: logging.Logger):
        """ Decorator logging call parameters and function return value.

        :param logger_object: logger for write

        Example(doctest):
        >>> log = logging.getLogger('test')
        >>> @CallRecorder(log)
        ... def doc_test1(arg, arg2):
        ...     return arg2
        >>> doc_test1(1, 2)
        2
        """
        self.log = logger_object

    def __call__(self, func: [types.FunctionType, types.MethodType]) -> Callable:
        def new_factory(*args, **kwargs) -> logging.LogRecord:
            record = logging.LogRecord(*args, **kwargs)
            record.funcName = func.__name__
            try:
                record.lineno = func.__code__.co_firstlineno

            except AttributeError:
                record.lineno = 0

            return record

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Callable:
            parameters = []
            parameters.extend(args)
            for k, v in kwargs.items():
                parameters.append(f'{k}={v}')

            parameters = ', '.join(str(param) for param in parameters) if parameters else ''
            with CallRecorder._lock, _replace_log_record_factory(new_factory):
                self.log.info(f'-> ({parameters!r})')

            result = func(*args, **kwargs)

            with CallRecorder._lock, _replace_log_record_factory(new_factory):
                self.log.info(f'<- {result!r}')

            return result
        return wrapper
