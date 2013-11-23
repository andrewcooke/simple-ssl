
from logging import basicConfig, DEBUG, debug
from unittest import TestCase

from script.argp import ArgP, ArgPRun, ArgPRoot
from script.base import CmdBase, ClsAttr, InsAttr


basicConfig(level=DEBUG)


class Foo(CmdBase):
    foo = ArgP(InsAttr)

class ArgPTest(TestCase):

    def test_parser(self):
        debug('test_parser')
        argp = ArgPRun(Foo)
        parser = argp.build_parser()
        args = parser.parse_args(['--foo', 'poop'])
        assert args.foo == 'poop', args


class Bar(CmdBase):
    bar = ArgP(InsAttr)

class Foo2(ArgPRoot):
    bar = ArgP(Bar)
    foo = ArgP(InsAttr)
    def __call__(self): pass

class NestedTest(TestCase):

    def test_nested(self):
        debug('test_nested')
        argp = ArgPRun(Foo2)
        parser = argp.build_parser()
        args = parser.parse_args(['--foo', 'poop', '--bar-bar', 'doop'])
        assert args.foo == 'poop', args
        cmd = argp.construct(args, {})
        assert cmd.bar._name == '--bar', cmd.bar._name
        assert cmd.bar.bar._name == '--bar-bar', cmd.bar.bar._name
        assert cmd.bar.bar._value == 'doop', cmd.bar.bar._value
