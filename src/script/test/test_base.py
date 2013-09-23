
from unittest import TestCase
from script.base import InsAttr, ClsAttr, CmdBase


class Foo(CmdBase):
    foo = ClsAttr(InsAttr)


class AttrTest(TestCase):
    
    def test_foo(self):
        assert isinstance(Foo.foo, ClsAttr), type(Foo.foo)
        foo = Foo()
        assert foo.foo._name == 'foo', foo.foo._name
        assert isinstance(foo.foo, InsAttr), type(foo.foo)
