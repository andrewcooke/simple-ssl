from os import getcwd
from simplessl.utils import IO


PRIVATE = 'private'
NEW_CERTS = 'newcerts'


class CA(IO):

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self._log('\nA CA (Certificate Authority) signs other certificates.')
        self._log('For more information, see https://en.wikipedia.org/wiki/Certificate_authority.')
        self._log('The CA directory is where a CA stores the data it needs to do its work.')
        self.dir = self._read('dir', getcwd(), 'What is the CA directory?')

    def create(self):
        self._log('\nCreating or verifying a CA at {}', self.dir)
        self._assert_dir(self.dir)
        self._assert_dir(self.dir, PRIVATE, mode=0o700)
        self._assert_dir(self.dir, NEW_CERTS)

    def auto(self):
        print('auto')
