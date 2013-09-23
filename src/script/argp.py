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
        args = parser.parse_args()
        cmd = self._cmd(**dict(chain(vars(args).items(), kargs.items())))
        cmd()

    def build_parser(self):
        parser = ArgumentParser(description=self._cmd.__doc__)
        for name, value in instances(ArgPOpt, self._cmd):
            value.add_argument(parser)
        return parser
