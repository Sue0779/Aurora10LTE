import os

def register(ctx):

    def find_cmd(ctx, *a):
        if len(a) < 2:
            print("Użycie: find <katalog> <fragment_nazwy>")
            return
        root = os.path.expanduser(a[0])
        pattern = a[1]
        print(f"[find] Szukam w {root} nazw zawierających: {pattern}")
        for r, dirs, files in os.walk(root):
            for f in files:
                if pattern in f:
                    print(os.path.join(r, f))

    ctx.register_command("find", find_cmd, "Wyszukuje pliki po fragmencie nazwy.", "tools")
