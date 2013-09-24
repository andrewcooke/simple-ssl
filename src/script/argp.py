
from argparse import ArgumentParser

from script.base import ClsAttr, instances, CmdBase


class ArgPOpt(ClsAttr):

    def add_argument(self, parser, prefixes=()):
        if issubclass(self._itype, CmdBase):
            for name, value in instances(ArgPOpt, self._itype):
                value.add_argument(parser, prefixes=prefixes + (name,))
        else:
            prefix = '--' + '-'.join(prefixes)
            if prefixes: prefix += '-'
            parser.add_argument(prefix + self._name)


class ArgPRun:

    def __init__(self, cmd):
        self._cmd = cmd

    def __call__(self, **kargs):
        parser = self.build_parser()
        self.construct(parser.parse_args(), kargs)()

    def construct(self, args, kargs):
        kargs = dict(kargs)
        kargs['defaults'] = vars(args)
        return self._cmd(**kargs)

    def build_parser(self):
        parser = ArgumentParser(description=self._cmd.__doc__)
        for name, value in instances(ArgPOpt, self._cmd):
            value.add_argument(parser)
        return parser
