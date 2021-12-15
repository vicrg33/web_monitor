import os
import stat


def set_rw(operation, name, exc):
    os.chmod(name, stat.S_IWRITE)
