from os import getcwd
from os.path import join
from simplessl.utils import IO


PRIVATE = 'private'
NEW_CERTS = 'newcerts'
SERIAL = 'serial'
INDEX_TXT = 'index.txt'
OPENSSL_CNF = 'openssl.cnf'
CACERT_PEM = 'cacert.pem'
CAKEY_PEM = 'cakey.pem'
REQ_PEM = 'req.pem'


class CertificateAuthority(IO):

    def __init__(self, dir=None, silent=False, defaults=False, **kargs):
        super().__init__(dir=dir, silent=silent, defaults=defaults, **kargs)
        self._log('\n A CA (Certificate Authority) signs other certificates.')
        self._log(' For more information, see https://en.wikipedia.org/wiki/Certificate_authority.')
        self._log('\nThe CA directory is where a CA stores the data it needs to do its work.')
        self.dir = self._read('dir', 'What is the CA directory?', default=getcwd())

    def create(self):
        self._log('\n Creating or verifying a CA at {}', self.dir)
        self._assert_dir(self.dir)
        self._assert_dir(self.dir, PRIVATE, mode=0o700)
        self._assert_dir(self.dir, NEW_CERTS)
        self._assert_file(self.dir, SERIAL, content=lambda: '01\n', checks=[('^(\\d+)\n$', 'Serial number')])
        self._assert_file(self.dir, INDEX_TXT)
        self._assert_file(self.dir, OPENSSL_CNF, content=self._openssl_cnf)
        self._assert_file(self.dir, CACERT_PEM, content=self._create_ca_cert, checks=[('-- BEGIN CERTIFICATE --', 'PEM header')])
        self._assert_file(self.dir, CAKEY_PEM, checks=[('-- BEGIN KEY --', 'Header (PEM format)')])

    def _create_ca_cert(self):
        self._log('\n The CA needs a certificate and associated key to sign other certificates.')
        self._log(' A new \'self-signed\' certificate can be generated.')
        self._log(' Alternatively, an existing certificate can be imported.')
        if self._menu('\nSelect certificate source:', ('Generate a new, \'self-signed\' CA certificate.', ('Import an existing CA certificate.', 'import-cacert'))):
            return self._import_ca_cert()
        else:
            return self._self_signed_ca()

    def _import_ca_cert(self):
        self._copy_file(self.dir, CACERT_PEM, option='import-cacert', prompt='\nCA certificate to import?')
        self._copy_file(self.dir, PRIVATE, CAKEY_PEM, option='import-cakey', prompt='\nCA key to import?')

    def _self_signed_ca(self):
        self._log('\n Generating the certificate request to create a new CA')
        req = CertificateRequest(self.args)
        req.generate(join(self.dir, REQ_PEM))

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

