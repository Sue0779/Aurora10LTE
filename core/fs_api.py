import os, pathlib

HOME = str(pathlib.Path.home())
ROOT = HOME  # sandbox teraz jest HOME — to jest poprawne z perspektywy usera

def _clean(path):
    # 1) rozwijanie tyldy:
    path = os.path.expanduser(path)

    # 2) normalizacja:
    path = os.path.realpath(path)

    # 3) sandbox — blokuje tylko wyjście poza HOME
    if not path.startswith(HOME):
        raise Exception("Wyjście poza sandbox.")

    return path

class FSAPI:
    def __init__(self, ctx):
        self.ctx = ctx

    def ls(self, path="."):
        p = _clean(path)
        return os.listdir(p)

    def tree(self, path, depth=5):
        p = _clean(path)
        result = []
        for root, dirs, files in os.walk(p):
            lvl = root.replace(p,"").count(os.sep)
            if depth and lvl > depth:
                continue
            result.append({"dir": root, "dirs": dirs, "files": files})
        return result

    def cat(self, path, max_bytes=200000):
        p = _clean(path)
        size = os.path.getsize(p)
        if size > max_bytes:
            raise Exception("Plik za duży do odczytu.")
        with open(p,"r",encoding="utf-8",errors="ignore") as f:
            return f.read()

    def write(self, path, text):
        p = _clean(path)
        with open(p,"w",encoding="utf-8") as f:
            f.write(text)

    def append(self, path, text):
        p = _clean(path)
        with open(p,"a",encoding="utf-8") as f:
            f.write(text)

    def info(self, path):
        p = _clean(path)
        st = os.stat(p)
        return {
            "path": p,
            "size": st.st_size,
            "mtime": st.st_mtime,
            "mode": st.st_mode
        }
