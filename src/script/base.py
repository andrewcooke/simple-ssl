
# the classes here are intended to support the writing of scripts that
# require input from the user.  the input can be supplied on the command
# line when invoking the script, or as an interactive prompt.  each input
# value is associated with an attribute.

# on the class, the attribute defines what inputs are to be read from the
# command line.  on the instance, attribute access triggers prompting if
# required.

# conversion from class to instance attribute is done by CmdBase.__new__;
# the command line functionality is carefully separated into argparse-specific
# classes (which can be replaced to support optparse, or whatever).

# typical use case:
# - programmer defines a script using classes, marking attributes
# - at run time:
#   - CmdMeta creates class, setting names on attributes.
#   - ArgPRun collects ArgPOpt attributes, generates appropriate argparse
#     specification, parses command line and instantiates the class.
#   - CmdBase converts class to instance attributes on creation.
#   - Command line values are passed to the __init__, where they are
#     used to set values.
#   - the __call__ method triggers script execution.
#   - when an attribute is accessed, it may prompt the user, cache the
#     value, etc.
from logging import debug


def instances(cls, container):
    try: container = vars(container)
    except TypeError: pass
    for name, value in container.items():
        if isinstance(value, cls): yield name, value


class ClsAttr:
    '''
    Base class for class attributes.  This is the class that CmdMeta
    checks for to set the name.
    '''

    def __init__(self, itype, name=None, *args, **kargs):
        self._itype = itype
        self._name = name
        self._args = args
        self._kargs = kargs

    def set_name(self, name):
        if not self._name: self._name = name

    def to_instance(self, defaults=None):
        kargs = dict(self._kargs)
        if defaults is not None:
            if issubclass(self._itype, CmdBase):
                debug('propagating defaults to embedded CmdBase')
                kargs['defaults'] = defaults
            elif self._name in defaults:
                debug('setting default to %r for %s' % (defaults[self._name], self._name))
                kargs['default'] = defaults[self._name]
        debug('instantiating %s %s with %r %r' % (self._itype, self._name, self._args, kargs))
        return self._itype(name=self._name, *self._args, **kargs)


class InsAttr:
    '''
    Base class for instance attributes.  Subclasses exist on instances and
    are responsible for prompting the user, caching values, etc.
    '''

    def __init__(self, name, default=None):
        self._name = name
        self._default = default


class CmdMeta(type):
    '''
    Metaclass that configures class attributes as command line parameters.
    '''

    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        for name, value in instances(ClsAttr, dct):
            value.set_name(name)


class CmdBase(metaclass=CmdMeta):
    '''
    Converts class to instance attributes.  Users should subclass this (or a
    child).
    '''

    def __init__(self, name=None, defaults=None):
        '''
        defaults is ignored here; it was used by __new__.
        '''
        self._name = name

    def __new__(cls, *args, defaults=None, **kargs):
        if defaults is None: defaults = {}
        debug('creating %r with %r %r' % (cls, args, kargs))
        instance = super(CmdBase, cls).__new__(cls)
        for name, value in instances(ClsAttr, cls):
            debug('converting %s from class to instance attribute' % name)
            setattr(instance, name, value.to_instance(defaults=defaults))
        return instance
