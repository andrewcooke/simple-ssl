
from argparse import ArgumentParser

from script.base import ClsAttr, instances, CmdBase, CmdRoot


class ArgP(ClsAttr):

    def add_argument(self, parser, prefix='--'):
        if issubclass(self._itype, CmdBase):
            for name, value in instances(ArgP, self._itype):
                value.add_argument(parser, prefix=prefix + name + '-')
        else:
            parser.add_argument(prefix + self._name)


class ArgPRun:

    def __init__(self, cmd, **kargs):
        self._cmd = cmd
        parser = self.build_parser()
        self.construct(parser.parse_args(), kargs)()

    def build_parser(self):
        parser = ArgumentParser(description=self._cmd.__doc__)
        for name, value in instances(ArgP, self._cmd):
            value.add_argument(parser)
        return parser

    def construct(self, args, kargs):
        kargs = dict(kargs)
        kargs['values'] = vars(args)
        return self._cmd(**kargs)


class ArgPRoot(CmdRoot):
    '''
    Includes useful utilities (printing, etc).
    '''

    defaults = ArgP(CmdRoot.defaults)
