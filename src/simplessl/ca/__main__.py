from argparse import ArgumentParser
from os import getcwd

from simplessl.ca import CA


def ca():
    parser = ArgumentParser(prog='python -m simplessl.ca')
    actions = parser.add_argument_group('actions')
    actions.add_argument('--create', action='store_true', help='create a new CA')
    parser.add_argument('--dir', action='store', help='the CA directory [%s]' % getcwd())
    parser.add_argument('--silent', action='store_true', help='suppress all output')
    parser.add_argument('--defaults', action='store_true', help='use defaults (no prompt)')
    args = parser.parse_args()
    ca = CA(**vars(args))
    if args.create: ca.create()
    else: ca.auto()

if __name__ == '__main__':
    ca()
