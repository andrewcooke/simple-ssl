from argparse import ArgumentParser
from os import getcwd

from simplessl.ca import CertificateAuthority
from simplessl.utils import io_arguments


def ca():
    parser = ArgumentParser(prog='python -m simplessl.req')
    parser.add_argument('--dir', action='store', help='the destination directory [%s]' % getcwd())
    io_arguments(parser)
    args = parser.parse_args()
    try:
        ca = CertificateRequest(**vars(args))
        if args.create: ca.create()
        else: ca.auto()
    except BaseException as e:
        print(e)
        if args.stacktrace: raise

if __name__ == '__main__':
    ca()
