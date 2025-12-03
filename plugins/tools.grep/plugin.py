import os

def register(ctx):

    def grep_cmd(ctx, *a):
        if len(a) < 2:
            print("Użycie: grep <pattern> <plik|katalog>")
            return
        pattern = a[0]
        target = os.path.expanduser(a[1])

        def grep_file(path):
            try:
                with open(path,"r",encoding="utf-8",errors="ignore") as f:
                    for i, line in enumerate(f, start=1):
                        if pattern in line:
                            print(f"{path}:{i}: {line.rstrip()}")
            except:
                pass

        if os.path.isfile(target):
            grep_file(target)
        else:
            for r, dirs, files in os.walk(target):
                for f in files:
                    grep_file(os.path.join(r,f))

    ctx.register_command("grep", grep_cmd, "grep-like – wyszukuje pattern w plikach.", "tools")
