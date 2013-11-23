
from logging import debug

from script.attr import TypedAttr, InsAttr


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

# for more complex projects, commands can be nested.  this gives a natural
# grouping for attributes and allows the use of a common prefix in their
# names.  the downside of grouping is that it is harder to share global (for
# all commands) configuration.  so we also broadcast a "root" element that
# can be delegated to when needed.

# nesting also modifies further the names of instance attributes, which
# inherit parent names as prefixes.


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
        if isinstance(itype, ClsAttr):  # making a copy to add argparse, for example
            debug('copying %s to %s' % (itype, self))
            self._itype = itype._itype
            self._name = itype._name
            self._args = itype._args
            self._kargs = itype._kargs
        else:
            self._itype = itype
            self._name = name
            self._args = args
            self._kargs = kargs

    def to_instance(self, root, prefix, values=None):
        kargs = dict(self._kargs)
        if values is not None:
            if issubclass(self._itype, CmdBase):
                debug('propagating values to embedded CmdBase')
                kargs['values'] = \
                    dict((name[len(self._name)+1:], value)
                         for name, value in values.items()
                         if name.startswith(self._name))
            elif self._name in values:
                debug('setting value to %r for %s' % (values[self._name], self._name))
                kargs['value'] = values[self._name]
        debug('instantiating %s %s with %r %r' % (self._itype, self._name, self._args, kargs))
        if not prefix.endswith('-'): prefix += '-'
        return self._itype(name=prefix + self._name, *self._args, root=root, **kargs)


class CmdMeta(type):
    '''
    Metaclass that configures class attributes as command line parameters.
    '''

    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        for name, value in instances(ClsAttr, dct): value._name = name


class CmdBase(metaclass=CmdMeta):
    '''
    Converts class to instance attributes.  Users should subclass this (or a
    child).
    '''

    def __init__(self, name='--', **ignored):
        self._name = name

    def __new__(cls, *args, root=None, name='--', values=None, **kargs):
        debug('creating %r with %r %r' % (cls, args, kargs))
        instance = super(CmdBase, cls).__new__(cls)
        if root is None: root = instance
        if values is None: values = {}
        for attr, value in instances(ClsAttr, cls):
            debug('converting %s from class to instance attribute' % attr)
            setattr(instance, attr, value.to_instance(root=root, prefix=name, values=values))
        return instance


class CmdRoot(CmdBase):

    defaults = ClsAttr(InsAttr(TypedAttr, type=bool))

    def prompt(self, name, value):
        if name == '--defaults': return  # circular!
        if not self.defaults: return  # should not ask the user
        return value

