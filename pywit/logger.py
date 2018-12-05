import time

from shutil import get_terminal_size

lines = [
    """uuuuuuuuuuuuuuuuuuuu""",
    """u" uuuuuuuuuuuuuuuuuu "u""",
    """u" u$$$$$$$$$$$$$$$$$$$$u "u""",
    """u" u$$$$$$$$$$$$$$$$$$$$$$$$u "u""",
    """u" u$$$$$$$$$$$$$$$$$$$$$$$$$$$$u "u""",
    """u" u$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$u "u""",
    """u" u$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$u "u""",
    """$ $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ $""",
    """$ $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ $""",
    """$ $$$" ... "$...  ...$" ... "$$$  ... "$$$ $""",
    """$ $$$u `"$$$$$$$  $$$  $$$$$  $$  $$$  $$$ $""",
    """$ $$$$$$uu "$$$$  $$$  $$$$$  $$  ''' u$$$ $""",
    """$ $$$""$$$  $$$$  $$$u "$$$" u$$  $$$$$$$$ $""",
    """$ $$$$....,$$$$$..$$$$$....,$$$$..$$$$$$$$ $""",
    """$ $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ $""",
    """'u "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$" u'""",
    """'u "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$" u'""",
    """'u "$$$$$$$$$$$$$$$$$$$$$$$$$$$$" u'""",
    """'u "$$$$$$$$$$$$$$$$$$$$$$$$" u'""",
    """'u "$$$$$$$$$$$$$$$$$$$$" u'""",
    """'u uuuuuuuuuuuuuuuuuu u'""",
    """uuuuuuuuuuuuuuuuuuuu"""]


class Logger():
    def __init__(self, level=1):
        self.level = level
        self.funcs = []

    def log(self, str, lvl):
        if lvl <= self.level:
            if lvl == 0:
                warnstr = "[{}] {}".format(self.funcs[-1], str)
                self.print_warning(warnstr)
            else:
                print("[%s] " % time.ctime(), end='')
                if lvl == 1:
                    print("%s" % str)
                else:
                    print("[Debug] ", end='')
                    print("[%s] " % self.funcs[-1], end='')
                    print("%s" % str)

    def add_func(self, str):
        self.funcs.append(str)

    def pop_func(self):
        self.funcs.pop()

    def set_level(self, lvl):
        if lvl < 4 and lvl > 0:
            self.level = lvl

    def print_warning(self, str):
        col = get_terminal_size().columns
        for i in range(3):
            print("|" * col)
        for line in lines:
            print(" " * ((col - len(line)) // 2) + line)
        for i in range(3):
            print("|" * col)
        for i in range(3):
            print(" ")
        tstr = time.ctime()
        tspace = (col - len(tstr)) // 2
        space = (col - len(str)) // 2
        for i in range(5):
            print(" " * tspace + tstr + " " * tspace)
            print(" " * space + str + " " * space)
        for i in range(3):
            print(" ")
        for i in range(3):
            print("|" * col)
