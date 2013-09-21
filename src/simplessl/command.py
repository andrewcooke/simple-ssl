from argparse import ArgumentParser


class Option:

    def __init__(self, description, default=None, group=None):
        self.description = description
        self.default = default
        self.group = group


def TypedOpt(cast):

    class _TypedOpt(Option):

        def __get__(self, instance, owner):
            return cast(super().__get__(instance, owner))

    return _TypedOpt


BoolOpt = TypedOpt(bool)


OPTION_ATTRIBUTES = '_option_attributes'


class OptionDict(dict):

    def __init__(self):
        self[OPTION_ATTRIBUTES] = {}

    def __setitem__(self, key, value):
        if isinstance(value, Option):
            value.name = key
            self[OPTION_ATTRIBUTES][key] = value
        super().__setitem__(key, value)


class CommandMeta(type):

    @classmethod
    def __prepare__(metacls, name, bases):
        return OptionDict()


class Command(metaclass=CommandMeta):

    no_prompt = BoolOpt('Disable user prompts?', group='behaviour')
    no_log = BoolOpt('Disable logging', group='behaviour')
    stack_trace = BoolOpt('Display stack trace on error?', group='behaviour')
    debug = BoolOpt('Display debug messages?')

    def __init__(self, options):
        self._option_values = options

    @classmethod
    def _parse_args(cls):
        parser = ArgumentParser(prog='python -m ' % cls.__module__, description=cls.__doc__)
        groups = {}
        for option in cls.option_attributes.values():
            if option.group:
                if option.group not in groups:
                    groups[option.group] = parser.add_argument_group(option.group)
                option.add_to(groups[option.group])
            else:
                option.add_to(parser)
        args = parser.parse_args()
        cls(options=vars(args))
        cls.run()

