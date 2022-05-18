import contextlib
import functools
import logging
import types
from threading import Lock
from typing import Callable

from logging_extensions import setup_default_log


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
        >>> setup_default_log()
        >>> log = logging.getLogger('test')
        >>> @CallRecorder(log)
        ... def doc_test1(arg, arg2, arg3, arg4):
        ...     return arg2

        >>> doc_test1(Callable,'bar', arg3=True, arg4='test')
        'bar'
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
            parameters = [repr(param) if isinstance(param, str) else str(param) for param in args]

            for k, v in kwargs.items():
                parameters.append(f'{k}={v!r}')

            with CallRecorder._lock, _replace_log_record_factory(new_factory):
                self.log.info(f'-> ({", ".join(parameters)})')

            result = func(*args, **kwargs)

            with CallRecorder._lock, _replace_log_record_factory(new_factory):
                self.log.info(f'<- {result!r}')

            return result
        return wrapper
