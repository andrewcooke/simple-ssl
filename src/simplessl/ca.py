
from script.argp import ArgP
from script.base import CmdBase, InsAttr


class CaDir(InsAttr):




class CaCore(CmdBase):

    dir = ArgP(CaDir, value='.',
               description='Where a CA stores the data it needs to do its work.')

