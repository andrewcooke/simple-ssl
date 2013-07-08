
from os.path import join, exists, isdir
from os import makedirs, stat


class IO:

    def __init__(self, silent=False, defaults=False, **args):
        self.__silent = silent
        self.__defaults = defaults or silent
        self.__args = args
        if self.__defaults:
            self._log('\nNo values will be read from the user (--defaults is set).')
        else:
            self._log('\nDefault values are displayed in [...] and prompts end in >.')

    def _log(self, template, *args, **kargs):
        if not self.__silent:
            print(template.format(*args, **kargs))

    def _read(self, option, default, template, *args, **kargs):
        self._log(template, *args, **kargs)
        if option in self.__args and self.__args[option] is not None:
            default = self.__args[option]
            prompt = '[--{option}={default!r}]'.format(option=option, default=default)
        else:
            prompt = '[--{option}, default {default!r}]'.format(option=option, default=default)
        if not self.__defaults:
            value = input(prompt + ' > ')
            if value: default = value
        else:
            self._log(prompt)
        if not default: raise ValueError('No value for --%s', option)
        return default

    def _assert_dir(self, *path, mode=None):
        path = join(*path)
        if exists(path):
            self._log('Checking {}', path)
        else:
            self._log('Creating {}', path)
            makedirs(path, mode=mode if mode is not None else 0o777)
        if not isdir(path): raise IOError('%s is not a directory' % path)
        if mode is not None and stat(path)[0] & 0o777 != mode: raise IOError('permissions on %s are not %o' % (path, mode))
