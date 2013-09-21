from unittest import TestCase
from simplessl.command import Option, Command


class OptionTest(TestCase):

    class Foo(Command):

        dir = Option('The directory for ...')

    def test_dir(self):
        foo = OptionTest.Foo()
        assert foo.dir.name == 'dir'
        assert len(foo.options) == 1
