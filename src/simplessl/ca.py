
from argparse import ArgumentParser
from os import getcwd
from os.path import join
from simplessl.req import CertificateRequest
from simplessl.utils import Cmd


class CertificateAuthority(Cmd):

    PRIVATE = 'private'
    NEW_CERTS = 'newcerts'
    SERIAL = 'serial'
    INDEX_TXT = 'index.txt'
    OPENSSL_CNF = 'openssl.cnf'
    CACERT_PEM = 'cacert.pem'
    CAKEY_PEM = 'cakey.pem'
    REQ_PEM = 'req.pem'

    def __init__(self, dir=None, create=False, import_cacert=None, import_cakey=None, silent=False, defaults=False, **kargs):
        super().__init__(dir=dir, create=create, import_cacert=import_cacert, import_cakey=import_cakey, silent=silent, defaults=defaults, **kargs)

    def run(self):
        if self._get('create'): self.create()

    def create(self):
        self._explain('Creating or verifying a CA:')
        self._explain('A CA (Certificate Authority) signs other certificates. For more information see https://en.wikipedia.org/wiki/Certificate_authority.')
        self._explain('The CA directory is where a CA stores the data it needs to do its work.')
        self.dir = self._read('Enter the CA directory:', 'dir', default=getcwd())
        self._explain('Creating or verifying a CA at {}', self.dir)
        self._assert_dir(self.dir)
        self._assert_dir(self.dir, self.PRIVATE, mode=0o700)
        self._assert_dir(self.dir, self.NEW_CERTS)
        self._assert_file(self.dir, self.SERIAL, content=lambda: '01\n', checks=[('^(\\d+)\n$', 'Serial number')])
        self._assert_file(self.dir, self.INDEX_TXT)
        self._assert_file(self.dir, self.OPENSSL_CNF, content=self.__openssl_cnf)
        self._assert_file(self.dir, self.CACERT_PEM, content=self.__create_ca_cert, checks=[('-- BEGIN CERTIFICATE --', 'Header (PEM format)')])
        self._assert_file(self.dir, self.CAKEY_PEM, checks=[('-- BEGIN KEY --', 'Header (PEM format)')])

    def __create_ca_cert(self):
        self._explain('The CA needs a certificate and associated key to sign other certificates. A new \'self-signed\' certificate can be generated. Alternatively, an existing certificate can be imported.')
        if self._menu('Select certificate source:', ['Generate a new, \'self-signed\' CA certificate.', ('Import an existing CA certificate.', 'import-cacert')]):
            return self.__import_ca_cert()
        else:
            return self.__self_signed_ca()

    def __import_ca_cert(self):
        self._copy_file(self.dir, self.CACERT_PEM, option='import-cacert', prompt='\nCA certificate to import?')
        self._copy_file(self.dir, self.PRIVATE, self.CAKEY_PEM, option='import-cakey', prompt='\nCA key to import?')

    def __self_signed_ca(self):
        self._explain('Generating the certificate request to create a new CA:')
        req = CertificateRequest(**self.args)
        req.generate(join(self.dir, self.REQ_PEM))

    def __openssl_cnf(self):
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
'''.format(dir=self.dir, index_text=self.INDEX_TXT, new_certs=self.NEW_CERTS, cacert_pem=self.CACERT_PEM, serial=self.SERIAL, private=self.PRIVATE)


if __name__ == '__main__':
    parser = ArgumentParser(prog='python -m simplessl.ca', description='Create or use a CA (Certificate Authority).')
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--create', action='store_true', help='create a new CA')
    parser.add_argument('--import-cacert', metavar='PATH', action='store', help='the CA certificate to import')
    parser.add_argument('--import-cakey', metavar='PATH', action='store', help='the CA key to import')
    parser.add_argument('--dir', action='store', help='the CA directory [%s]' % getcwd())
    CertificateAuthority.parse(parser)
