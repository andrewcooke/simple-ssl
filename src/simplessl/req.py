from simplessl.utils import IO


class CertificateRequest(IO):

    def __init__(self, dir=None, silent=False, defaults=False, **kargs):
        super().__init__(dir=dir, silent=silent, defaults=defaults, **kargs)
        self._log('\nA certificate request contains .')
        self.dir = self._read('dir', getcwd(), 'What is the destination directory for the request?')

