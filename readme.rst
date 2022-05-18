logging_extensions
------

**CallRecorder**

Decorator logging call parameters and function return value.

*example*:

.. code-block:: python

        >>> import logging
        >>> from logging_extensions import CallRecorder, setup_root_logger_format
        >>> setup_root_logger_format(logging.INFO)
        >>> log = logging.getLogger('test')
        >>> @CallRecorder(log)
        ... def doc_test1(arg, arg2, arg3, arg4):
        ...     return arg2
        >>> doc_test1(list,'bar', arg3=True, arg4='test')
        [2022-05-18 09:58:45 +0300][16396][INFO][test.doc_test1: 1] : -> (list, 'bar', arg3=True, arg4='test')
        [2022-05-18 09:58:45 +0300][16396][INFO][test.doc_test1: 1] : <- 'bar'

**Inspectable**

Mixin-class need for detailed representation inherited classes.

*example:*

.. code-block:: python

    >>> import logging
    >>> from logging_extensions import Inspectable
    >>> class TT(Inspectable):
    ...    __multiline_repr__ = True
    ...    __include_methods__ = True
    ...    @classmethod
    ...    def cls_method(cls):
    ...        pass

    ...    @staticmethod
    ...    def static_methoddddddddddddd():
    ...        pass
    ...    class_attr = 23.43
    ...
    ...    def __init__(self):
    ...        self.string = "abc"
    ...        self.a = 1
    ...        self._big_private_name = True
    ...        self.number = 10

    ...    def method(self):
    ...        self.var = -1
    ...
    >>> t = TT()
    >>> t.method()
    >>> t
    <instance of __main__.TT inherits from (logging_extensions.inspectable.Inspectable)>
    ID: 0x2b7e19d57e0
    (Inspector:                 <class 'logging_extensions.inspectable.Inspectable.Inspector'>
    a:                         1
    class_attr:                23.43
    cls_method:                <classmethod(<function _test_inspectable.<locals>.TT.cls_method at 0x000002B7E1E19A20>)>
    method:                    <function _test_inspectable.<locals>.TT.method at 0x000002B7E1F4C790>
    number:                    10
    static_methoddddddddddddd: <staticmethod(<function _test_inspectable.<locals>.TT.static_methoddddddddddddd at 0x000002B7E1F4C550>)>
    string:                    'abc'
    var:                       -1
    _big_private_name:         True)


**LevelFilter**

A filter that accepts one or more logging levels in the constructor, all levels not included in the filter will be discarded.

*example*:

.. code-block:: python

    >>> import logging
    >>> from logging_extensions import LevelFilter, setup_root_logger_format
    >>> setup_root_logger_format(logging.DEBUG)
    >>> log = logging.getLogger(__name__)
    >>> log.addFilter(LevelFilter(logging.DEBUG, logging.ERROR))
    >>> log.debug('debug message')
    [2022-05-18 16:45:39 +0300][14980][ERROR][__main__.<module>: 1] : debug message
    >>> log.info('info message')
    >>> log.warning('warning message')
    >>> log.error('error message')
    [2022-05-18 16:45:51 +0300][14980][ERROR][__main__.<module>: 1] : error message

