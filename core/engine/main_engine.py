import sys

PY_MAJOR_VERSION, PY_MINOR_VERSION = sys.version_info[:2]
if (PY_MAJOR_VERSION, PY_MINOR_VERSION) < (3, 5):
    raise Exception('Python 版本需要 3.5 或以上, 当前版本为 %s.%s 请升级 Python' % (PY_MAJOR_VERSION, PY_MINOR_VERSION))


class MainEngine:
    def __init__(self):
