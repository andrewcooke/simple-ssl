from os import getcwd
from os.path import join
from simplessl.utils import IO


PRIVATE = 'private'
NEW_CERTS = 'newcerts'
SERIAL = 'serial'
INDEX_TXT = 'index.txt'
OPENSSL_CNF = 'openssl.cnf'
CACERT_PEM = 'cacert.pem'
REQ_PEM = 'req.pem'


class CertificateAuthority(IO):

    def __init__(self, dir=None, silent=False, defaults=False, **kargs):
        super().__init__(dir=dir, silent=silent, defaults=defaults, **kargs)
        self._log('\nA CA (Certificate Authority) signs other certificates.')
        self._log('For more information, see https://en.wikipedia.org/wiki/Certificate_authority.')
        self._log('The CA directory is where a CA stores the data it needs to do its work.')
        self.dir = self._read('dir', 'What is the CA directory?', default=getcwd())

    def create(self):
        self._log('\nCreating or verifying a CA at {}', self.dir)
        self._assert_dir(self.dir)
        self._assert_dir(self.dir, PRIVATE, mode=0o700)
        self._assert_dir(self.dir, NEW_CERTS)
        self._assert_file(self.dir, SERIAL, content=lambda: '01\n', checks=[('^(\\d+)\n$', 'Serial number')])
        self._assert_file(self.dir, INDEX_TXT)
        self._assert_file(self.dir, OPENSSL_CNF, content=self._openssl_cnf)

    def _openssl_cnf(self):
        return '''
[ ca ]
default_ca = simple_ssl_ca

[ simple_ssl_ca ]
dir              = {dir}
database         = $dir/{index_text}
new_certs_dir    = $dir/{new_certs}

certificate      = $dir/{cacert_pem}
serial           = $dir/{serial}
private_key      = $dir/{private}/cakey.pem
RANDFILE         = $dir/{private}/.rand

default_days     = 365
default_crl_days = 30
default_md       = md5
policy           = simple_ssl_ca_policy
email_in_dn      = no
name_opt         = simple_ssl_ca
cert_opt         = simple_ssl_ca
copy_extensions  = none

[ simple_ssl_ca_policy ]
countryName            = optional
stateOrProvinceName    = optional
organizationName       = optional
organizationalUnitName = optional
commonName             = supplied
emailAddress           = optional
'''.format(dir=self.dir, index_text=INDEX_TXT, new_certs=NEW_CERTS, cacert_pem=CACERT_PEM, serial=SERIAL, private=PRIVATE)

    def _cacert_pem(self):
        self._log('\nGenerating request to create a new CA')
        req = CertificateRequest(self.args)
        req.generate(join(self.dir, REQ_PEM))

    def auto(self):
        print('auto')
