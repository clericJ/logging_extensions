import contextlib
import functools
import logging
import types
from threading import Lock
from typing import Callable

from logging_extensions import setup_root_logger_format


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

    def __init__(self, recorder: Callable, hide: list = ('password',)):
        """ Decorator logging call parameters and function return value.

        :param hide: list of variable names whose values will be hidden from the output
        :param recorder: callable object

        Example(doctest):
        >>> setup_root_logger_format()
        >>> log = logging.getLogger('test')
        >>> @CallRecorder(log.info)
        ... def doc_test1(arg, arg2, arg3, arg4):
        ...     return arg2

        >>> doc_test1(Callable,'bar', arg3=True, arg4='test')
        'bar'
        """
        self.hide = hide
        self.recorder = recorder

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
            name = getattr(func, '__name__', '<undefined>')

            for k, v in kwargs.items():
                parameters.append(f'{k}=<...>' if k in self.hide else f'{k}={v!r}')

            with CallRecorder._lock, _replace_log_record_factory(new_factory):
                self.recorder(f'{name} -> ({", ".join(parameters)})')

            result = func(*args, **kwargs)

            with CallRecorder._lock, _replace_log_record_factory(new_factory):
                self.recorder(f'{name} <- {result!r}')

            return result
        return wrapper
