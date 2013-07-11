from argparse import ArgumentParser
from os import getcwd

from simplessl.ca import CertificateAuthority
from simplessl.utils import io_arguments


def run():
    parser = ArgumentParser(prog='python -m simplessl.ca')
    actions = parser.add_argument_group('actions')
    actions.add_argument('--create', action='store_true', help='create a new CA')
    parser.add_argument('--import-cacert', action='store', help='the CA certificate to import')
    parser.add_argument('--import-cakey', action='store', help='the CA key to import')
    parser.add_argument('--dir', action='store', help='the CA directory [%s]' % getcwd())
    io_arguments(parser)
    args = parser.parse_args()
    try:
        ca = CertificateAuthority(**vars(args))
        ca.create()
    except BaseException as e:
        print('\nERROR:', e)
        print()
        if args.stacktrace: raise

if __name__ == '__main__':
    run()
