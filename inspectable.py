

class Inspectable:
    """ Mixin-class need for detailed representation inherited classes

    Flags (must be defined in class namespace)

        __multiline_repr__ - multiline format

        __include_methods__ - include to out methods

    Example (doctest):
    >>> class Test(Inspectable):
    ...     def __init__(self):
    ...         self.a = 10
    ...         self._p = 'c'
    ...         self.x = [1, 2, 3]
    >>> t = Test()
    >>> t #doctest: +ELLIPSIS
    <instance of ....Test inherits from (....Inspectable)> ID: 0x... (Inspector: <...> a: 10 x: [1, 2, 3] _p: 'c')
    """

    class Inspector:

        def __init__(self, multiline=False, include_methods=False):
            self.include_methods = include_methods
            self.multiline = multiline

        @staticmethod
        def get_fullname(obj) -> str:
            if inspect.isclass(obj):
                return f'{obj.__module__}.{obj.__name__}'
            return f'{type(obj).__module__}.{type(obj).__name__}'

        @staticmethod
        def compare_attributes(x: str, y: str) -> int:
            result = None
            if x.startswith('_') and y.startswith('_'):
                result = (-1 if x > y else (0 if x == y else 1))
            elif x.startswith('_') and (not y.startswith('_')):
                result = 1
            elif (not x.startswith('_')) and y.startswith('_'):
                result = -1

            return result if result is not None else (1 if x > y else (0 if x == y else -1))

        @staticmethod
        def get_attributes(cls) -> set[tuple]:
            attributes = set(cls.__dict__.items())
            for cls in cls.__mro__:
                attributes.update(cls.__dict__.items())
            return attributes

        @staticmethod
        def calculate_indent(names: dict) -> int:
            result = 0
            for name in names:
                if result < len(name):
                    result = len(name)

            return result + 1

        def format_attributes(self, attributes: dict) -> list[str]:
            indent = self.calculate_indent(attributes) if self.multiline else 1
            result = []
            for key, val in attributes.items():
                if (self.include_methods is False
                        and isinstance(val, (types.FunctionType, classmethod, staticmethod))):
                    continue

                if not (key.startswith('__') and key.endswith('__')):
                    result.append(f'{key}:{" " * (indent - len(key))}{val!r}'
                                  if self.multiline else f'{key}: {val!r}')
            return result

        def repr(self, instance) -> str:
            delimiter = '\n' if self.multiline else ' '

            template = ('<instance of {} inherits from ({})>'
                        + delimiter + 'ID: {}' + delimiter + '({})')

            attrs = instance.__dict__
            attrs.update(self.get_attributes(instance.__class__))
            attrs = self.format_attributes(attrs)
            attrs.sort(key=functools.cmp_to_key(self.compare_attributes))

            bases = ', '.join([self.get_fullname(cls) for cls in instance.__class__.__bases__])
            return template.format(self.get_fullname(instance),
                                   bases, hex(id(instance)), delimiter.join(attrs))

    def __repr__(self) -> str:
        multiline = getattr(self, '__multiline_repr__', False)
        include_methods = getattr(self, '__include_methods__', False)

        return self.Inspector(multiline, include_methods).repr(self)
