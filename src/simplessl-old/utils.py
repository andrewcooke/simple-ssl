from os.path import join, exists, isdir, dirname, isfile, realpath
from os import makedirs, stat, chmod
from re import compile


INITIALISED = '_initialised'


def dash(option): return option.replace('_', '-')
def underscore(option): return option.replace('-', '_')

def lines(max_len, text):
    while text:
        best, line = None, ''
        while text and len(line) < max_len:
            best = line
            word, space, text = text.partition(' ')
            if word:
                if line.endswith('.'): line += ' '
                if line: line += ' '
                line += word
            if len(line) > max_len:
                yield best
                best, line = None, line[len(best):].strip()
        if line: yield line


class Cmd:

    def __init__(self, silent=False, defaults=False, **kargs):
        self.__silent = silent
        self.__defaults = defaults or silent
        self.__args = kargs
        if INITIALISED not in self.__args:
            if self.__defaults:
                intro = 'No values will be read from the user (--defaults is set).'
            else:
                intro = 'Default values are displayed in [...] and prompts start with >.'
            intro += '\n[--opt=\'xxx\'] means that the default value is xxx, set by --opt.'
            intro += '\n[--opt, default \'xxx\'] means that --opt was not given on the command line.'
            self._explain(intro)
            self.__args[INITIALISED] = True


    def _newline(self):
        self.__log('')

    def _output(self, template, *args, **kargs):
        '''
        display high-priority information.  Often used with input().
        '''
        if not self.__silent:
            self.__indent(' ', template, *args, **kargs)

    def _explain(self, template, *args, **kargs):
        '''
        display lower priority, contextual information.
        '''
        if not self.__silent:
            self._newline()
            self.__indent('   ', template, *args, **kargs)

    def _progress(self, template, *args, **kargs):
        '''
        display low priority progress data.
        '''
        if not self.__silent:
            self.__indent('   ... ', template, *args, **kargs)

    def __indent(self, offset, template, *args, **kargs):
        if not self.__silent:
            text = template.format(*args, **kargs)
            for paragraph in text.splitlines():
                for line in lines(78 - len(offset), paragraph):
                    self.__log('{0}{1}', offset, line)

    def __log(self, template, *args, **kargs):
        if not self.__silent:
            print(template.format(*args, **kargs))

    def _get(self, name):
        return self.__args.get(name, None)

    def _read(self, title, option, default=None):
        '''
        read a value from the user.  if the user was previously prompted, that
        value is returned immediately.  otherwise, the user is prompted, with
        the default coming from a command line option, if defined.
        '''
        self._newline()
        self._output(title)
        _option = underscore(option)
        previous = '_' + _option
        if previous in self.__args:
            default = self.__args[previous]
            prompt = '[{default}]'.format(default=default)
        elif _option in self.__args and self.__args[_option] is not None:
            default = self.__args[_option]
            prompt = '[--{option}={default!r}]'.format(option=option, default=default)
        else:
            prompt = '[--{option}, default {default!r}]'.format(option=option, default=default)
        if previous not in self.__args and not self.__defaults:
            value = input(' ' + prompt + '> ')
            if value: default = value
        else:
            self._output(prompt)
        if not default: raise ValueError('No value for --%s' % option)
        self.__args[previous] = default
        return default

    def _menu(self, title, choices, default=0):
        self._newline()
        self._output(title)
        reason = ''
        for i, choice in enumerate(choices):
            if isinstance(choice, tuple):
                choice, option = choice
                _option = underscore(option)
                if _option in self.__args and self.__args[_option] is not None:
                    reason = ' (--%s given)' % option
                    default = i
            self._output('{0}: {1}', i, choice)
        prompt = '[default %d%s]' % (default, reason)
        if self.__defaults:
            self._output(prompt)
            return default
        while True:
            value = input(' ' + prompt + '> ')
            try:
                if not value: value = default
                value = int(value)
                if 0 <= value < len(choices): return value
            except ValueError:
                self.__log('Enter an integer to select an option, or press return for the default.')

    def _assert_dir(self, *path, mode=None):
        path = join(*path)
        if exists(path):
            self._progress('Checking directory {}', path)
        else:
            self._progress('Creating directory {}', path)
            makedirs(path, mode=mode if mode is not None else 0o777)
        if not isdir(path): raise IOError('%s is not a directory' % path)
        if mode is not None and stat(path)[0] & 0o777 != mode: raise IOError('Permissions on %s are not %o' % (path, mode))

    def _assert_file(self, *path, mode=None, content=None, checks=None):
        path = join(*path)
        if exists(path):
            self._progress('Checking file {}', path)
        else:
            self._progress('Creating file {}', path)
            makedirs(dirname(path), mode=mode if mode is not None else 0o777, exist_ok=True)
            # do this before opening so that we don't mess up checks on file
            if content is not None: content = content()
            with open(path, 'w') as out:
                if content is not None: out.write(content)
        if not isfile(path): raise IOError('%s is not a directory' % path)
        if mode is not None and stat(path)[0] & 0o777 != mode: chmod(path, mode)
        if checks is not None:
            with open(path, 'r') as inp: text = inp.read()
            for pattern, name in checks:
                rx = compile(pattern)
                match = rx.search(text)
                if match:
                    data = match.group(1) if match.groups else match.group(0)
                    self._progress('{0}: {1}', name, data)
                else:
                    raise ValueError('%s missing in %s (bad file contents)' % (name, path))

    def _copy_file(self, *path, mode=None, option=None, prompt=None):
        path = join(*path)
        if exists(path): raise IOError('%s already exists' % path)
        source = self._read(option, prompt)
        if not exists(source) or not isfile(source): raise IOError('%s is not a file' % source)
        self._progress('Copying {0} to {1}', source, path)
        with open(source, 'r') as inp, open(path, 'w') as out:
            out.write(inp.read())
        # TODO mode

    @property
    def args(self):
        args = dict(self.__args)
        args['silent'] = self.__silent
        args['defaults'] = self.__defaults
        return args

    @staticmethod
    def io_arguments(parser):
        group = parser.add_argument_group('common IO arguments')
        group.add_argument('--defaults', action='store_true', help='use defaults (no interactive user input)')
        group.add_argument('--silent', action='store_true', help='suppress all output except errors')
        group.add_argument('--stacktrace', action='store_true', help='display stack trace on errors')

    @classmethod
    def parse(cls, parser):
        cls.io_arguments(parser)
        args = parser.parse_args()
        try:
            instance = cls(**vars(args))
            instance.run()
        except BaseException as e:
            print('\nERROR:', e)
            print()
            if args.stacktrace: raise
