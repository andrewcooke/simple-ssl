from os.path import join, exists, isdir, dirname, isfile, realpath
from os import makedirs, stat, chmod
from re import compile


class IO:

    def __init__(self, silent=False, defaults=False, **args):
        self.__silent = silent
        self.__defaults = defaults or silent
        self.__args = args
        if self.__defaults:
            self._log('\nNo values will be read from the user (--defaults is set).')
        else:
            self._log('\nDefault values are displayed in [...] and prompts end in >.')
        self._log('[--opt=\'xxx\'] means that the default value is xxx, set by --opt.')
        self._log('[--opt, default \'xxx\'] means that --opt was not given on the command line.')

    def _log(self, template, *args, **kargs):
        if not self.__silent:
            print(template.format(*args, **kargs))

    def _read(self, option, template, *args, default=None):
        '''
        read a value from the user.  if the user was previously prompted, that
        value is returned immediately.  otherwise, the user is prompted, with
        the default coming from a command line option, if defined.
        '''
        self._log(template, *args)
        previous = '_' + option
        if previous in self.__args:
            default = self.__args[previous]
            prompt = '[{default}]'.format(default=default)
        elif option in self.__args and self.__args[option] is not None:
            default = self.__args[option]
            prompt = '[--{option}={default!r}]'.format(option=option, default=default)
        else:
            prompt = '[--{option}, default {default!r}]'.format(option=option, default=default)
        if previous not in self.__args or not self.__defaults:
            value = input(prompt + ' > ')
            if value: default = value
        else:
            self._log(prompt)
        if not default: raise ValueError('No value for --%s' % option)
        self.__args[previous] = default
        return default

    def _assert_dir(self, *path, mode=None):
        path = join(*path)
        if exists(path):
            self._log('Checking directory {}', path)
        else:
            self._log('Creating directory {}', path)
            makedirs(path, mode=mode if mode is not None else 0o777)
        if not isdir(path): raise IOError('%s is not a directory' % path)
        if mode is not None and stat(path)[0] & 0o777 != mode: raise IOError('Permissions on %s are not %o' % (path, mode))

    def _assert_file(self, *path, mode=None, content=None, checks=None):
        path = join(*path)
        if exists(path):
            self._log('Checking file {}', path)
        else:
            self._log('Creating file {}', path)
            makedirs(dirname(path), mode=mode if mode is not None else 0o777, exist_ok=True)
            with open(path, 'w') as out:
                if content is not None: out.write(content())
        if not isfile(path): raise IOError('%s is not a directory' % path)
        if mode is not None and stat(path)[0] & 0o777 != mode: chmod(path, mode)
        if checks is not None:
            with open(path, 'r') as inp: text = inp.read()
            for pattern, name in checks:
                rx = compile(pattern)
                match = rx.search(text)
                if match:
                    data = match.group(1) if match.groups else match.group(0)
                    self._log('{0}: {1}', name, data)
                else:
                    raise ValueError('No %s in %s' % (name.lower(), path))

    @property
    def args(self):
        args = dict(self.__args)
        args['silent'] = self.__silent
        args['defaults'] = self.__defaults
        return args


def io_arguments(parser):
    parser.add_argument('--defaults', action='store_true', help='use defaults (no interactive user input)')
    parser.add_argument('--silent', action='store_true', help='suppress all output except errors')
    parser.add_argument('--stacktrace', action='store_true', help='display stack trace on errors')
