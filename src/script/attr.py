

class InsAttr:
    '''
    Base class for instance attributes.  Subclasses exist on instances and
    are responsible for prompting the user, caching values, etc.
    '''

    def __init__(self, name, root=None, value=None, **kargs):
        self._name = name
        self._root = root
        self._value = value
        self._prompted = False
        for name, value in kargs.items(): setattr(self, '_' + name, value)

    def __get__(self, cmd, cls):
        if not self._prompted:
            self._value = self._root.prompt(self._name, self._value)
            self._prompted = True
        return self.post_process(self._value)

    def post_process(self, value):
        return value


class TypedAttr(InsAttr):

    def __init__(self, name, type, root=None, value=None, **kargs):
        self._type = type
        super().__init__(name, root=root, value=value, **kargs)

    def __get__(self, cmd, cls):
        if not self._prompted:
            self._value = self._root.prompt(self._name, self._value)
            self._prompted = True
        return self._type(self._value)


class StrAttr(TypedAttr):

    def __init__(self, name, root=None, value=None, **kargs):
        super().__init__(name, str, root=root, value=value, **kargs)


class BoolAttr(TypedAttr):

    def __init__(self, name, root=None, value=None, **kargs):
        super().__init__(name, bool, root=root, value=value, **kargs)
