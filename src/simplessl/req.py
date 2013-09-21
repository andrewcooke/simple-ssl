from argparse import ArgumentParser
from os import getcwd
from simplessl.utils import Cmd


DEFAULT_TMP = '/tmp'

class CertificateRequest(Cmd):

    def __init__(self, dir=None, tmp=DEFAULT_TMP, request=False, silent=False, defaults=False, **kargs):
        super().__init__(dir=dir, tmp=tmp, request=request, silent=silent, defaults=defaults, **kargs)

    def run(self):
        if self._get('generate'): self.request()

    def request(self):
        self._explain('''A certificate request is a file that contains the data needed by a CA (Certificate Authority) to generate a signed certificate.''')
        self.dir = self._read('What is the destination directory for the request?', 'dir', default=getcwd())
        self.tmp = self._read('What is the destination directory for the request?', 'dir', default=getcwd())


if __name__ == '__main__':
    parser = ArgumentParser(prog='python -m simplessl.req', description='Generate a request (for a CA to sign), or a self-signed certificate.')
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--self-sign', action='store_true', help='generate a self-signed certificate')
    actions.add_argument('--request', action='store_true', help='generate a request')
    parser.add_argument('--dir', action='store', help='where to save the request [%s]' % getcwd())
    parser.add_argument('--tmp', action='store', help='where to generate the temporary configuration file [%s]' % DEFAULT_TMP)
    CertificateRequest.parse(parser)
