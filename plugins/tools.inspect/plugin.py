def register(ctx):

    def inspect_cmd(ctx, *a):
        if not a:
            print("Użycie: inspect <ścieżka>")
            return
        path = a[0]
        try:
            info = ctx.fs.info(path)
            print("[inspect]")
            for k, v in info.items():
                print(f"  {k}: {v}")
        except Exception as e:
            print("[inspect] Błąd:", e)

    ctx.register_command("inspect", inspect_cmd, "Metadane pliku/katalogu.", "tools")
