def register(ctx):

    def fs_ls(ctx, *a):
        path = a[0] if a else "~"
        try:
            items = ctx.fs.ls(path)
            print(f"[fs_ls] {path}:")
            for it in items:
                print(" ", it)
        except Exception as e:
            print("[fs_ls] Błąd:", e)

    def fs_cat(ctx, *a):
        if not a:
            print("Użycie: fs_cat <plik>")
            return
        path = a[0]
        try:
            txt = ctx.fs.cat(path)
            print(txt, end="")
        except Exception as e:
            print("[fs_cat] Błąd:", e)

    def fs_tree(ctx, *a):
        if not a:
            print("Użycie: fs_tree <katalog> [głębokość]")
            return
        path = a[0]
        depth = int(a[1]) if len(a) > 1 else 3
        try:
            tree = ctx.fs.tree(path, depth=depth)
            for node in tree:
                print(node["dir"])
                for d in node["dirs"]:
                    print("  [D]", d)
                for f in node["files"]:
                    print("  [F]", f)
        except Exception as e:
            print("[fs_tree] Błąd:", e)

    def fs_info(ctx, *a):
        if not a:
            print("Użycie: fs_info <plik/katalog>")
            return
        path = a[0]
        try:
            info = ctx.fs.info(path)
            print("[fs_info]")
            for k, v in info.items():
                print(f"  {k}: {v}")
        except Exception as e:
            print("[fs_info] Błąd:", e)

    def fs_cmd(ctx, *a):
        print("Użycie FS:")
        print("  fs_ls [ścieżka]")
        print("  fs_cat <plik>")
        print("  fs_tree <katalog> [głębokość]")
        print("  fs_info <ścieżka>")

    ctx.register_command("fs_ls", fs_ls, "Lista plików w katalogu.", "fs")
    ctx.register_command("fs_cat", fs_cat, "Odczyt pliku.", "fs")
    ctx.register_command("fs_tree", fs_tree, "Drzewo katalogów.", "fs")
    ctx.register_command("fs_info", fs_info, "Metadane pliku/katalogu.", "fs")
    ctx.register_command("fs", fs_cmd, "Pomoc FSAPI.", "fs")
