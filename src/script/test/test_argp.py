from unittest import TestCase
from script.argp import ArgPOpt, ArgPRun
from script.base import CmdBase, ClsAttr


class Foo(CmdBase):

    foo = ArgPOpt(ClsAttr)


class ArgPTest(TestCase):

    def test_parser(self):
        argp = ArgPRun(Foo)
        parser = argp.build_parser()
        args = parser.parse_args(['--foo', 'poop'])
        assert args.foo == 'poop', args


class Foo2(CmdBase):

    class Bar(CmdBase):
        bar = ArgPOpt(ClsAttr)

    foo = ArgPOpt(ClsAttr)


class NestedTest(TestCase):

    def test_nested(self):
        argp = ArgPRun(Foo2)
        parser = argp.build_parser()
        args = parser.parse_args(['--foo', 'poop', '--bar-bar', 'stinky'])
        assert args.foo == 'poop', args
        assert args.bar_bar == 'stinky'
