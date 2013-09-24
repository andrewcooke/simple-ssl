from argparse import ArgumentParser
from itertools import chain

from script.base import ClsAttr, instances


class ArgPOpt(ClsAttr):

    def add_argument(self, parser):
        parser.add_argument('--' + self._name)


class ArgPRun:

    def __init__(self, cmd):
        self._cmd = cmd

    def __call__(self, **kargs):
        parser = self.build_parser()
        self.run(parser.parse_args(), kargs)

    def run(self, args, kargs):
        kargs = dict(kargs)
        kargs['defaults'] = vars(args)
        cmd = self._cmd(**kargs)
        cmd()

    def build_parser(self):
        parser = ArgumentParser(description=self._cmd.__doc__)
        for name, value in instances(ArgPOpt, self._cmd):
            value.add_argument(parser)
        return parser
