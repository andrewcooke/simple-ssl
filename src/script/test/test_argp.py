
from logging import basicConfig, DEBUG, debug
from unittest import TestCase

from script.argp import ArgPOpt, ArgPRun
from script.base import CmdBase, ClsAttr, InsAttr


basicConfig(level=DEBUG)


class Foo(CmdBase):

    foo = ArgPOpt(InsAttr)


class ArgPTest(TestCase):

    def test_parser(self):
        debug('test_parser')
        argp = ArgPRun(Foo)
        parser = argp.build_parser()
        args = parser.parse_args(['--foo', 'poop'])
        assert args.foo == 'poop', args


class Bar(CmdBase):
    bar = ArgPOpt(InsAttr)

class Foo2(CmdBase):
    bar = ArgPOpt(Bar)
    foo = ArgPOpt(InsAttr)
    def __call__(self): pass


class NestedTest(TestCase):

    def test_nested(self):
        debug('test_nested')
        argp = ArgPRun(Foo2)
        parser = argp.build_parser()
        args = parser.parse_args(['--foo', 'poop', '--bar-bar', 'doop'])
        assert args.foo == 'poop', args
        cmd = argp.construct(args, {})
        assert cmd.bar.bar._default == 'doop', cmd.bar.bar._default
