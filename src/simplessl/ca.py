
from script.argp import ArgP, ArgPRoot, ArgPRun
from script.attr import StrAttr


class CaCore(ArgPRoot):

    dir = ArgP(StrAttr, value='.',
               description='Where a CA stores the data it needs to do its work.')

    def __call__(self):
        print(self.dir.__get__(self, type(self)))
        print("dir is " + str(self.dir))


if __name__ == '__main__':
    ArgPRun(CaCore)
