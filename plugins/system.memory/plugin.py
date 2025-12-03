import json

def _path(ctx):
    mdir = ctx.root / "memory"
    mdir.mkdir(parents=True, exist_ok=True)
    return mdir / "global.memory.json"

def _load(ctx):
    p = _path(ctx)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except:
        return {}

def _save(ctx, data):
    p = _path(ctx)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def register(ctx):

    def memory_show(ctx, *a):
        data = _load(ctx)
        print("[memory show] Klucze:", list(data.keys()))
        for k, v in data.items():
            print(f"- {k}: {v}")

    def memory_set(ctx, *a):
        if len(a) < 2:
            print("Użycie: memory_set <klucz> <wartość>")
            return
        key = a[0]
        value = " ".join(a[1:])
        data = _load(ctx)
        data[key] = value
        _save(ctx, data)
        print(f"[memory set] {key} = {value}")

    def memory_purge(ctx, *a):
        _save(ctx, {})
        print("[memory purge] Wyczyściono pamięć globalną.")

    def memory_export(ctx, *a):
        data = _load(ctx)
        print(json.dumps(data, indent=2, ensure_ascii=False))

    def memory_import(ctx, *a):
        if len(a) < 1:
            print("Użycie: memory_import <plik.json>")
            return
        import os, json as _json
        path = os.path.expanduser(a[0])
        try:
            data = _json.loads(open(path,"r",encoding="utf-8").read())
            _save(ctx, data)
            print("[memory import] Zaimportowano z pliku:", path)
        except Exception as e:
            print("[memory import] Błąd importu:", e)

    def memory_cmd(ctx, *a):
        return memory_show(ctx, *a)

    ctx.register_command("memory", memory_cmd, "Pamięć Aurory (globalne klucze).", "system")
    ctx.register_command("memory_show", memory_show, "Wyświetla zawartość pamięci.", "system")
    ctx.register_command("memory_set", memory_set, "Ustawia klucz w pamięci.", "system")
    ctx.register_command("memory_purge", memory_purge, "Czyści pamięć globalną.", "system")
    ctx.register_command("memory_export", memory_export, "Eksportuje pamięć jako JSON.", "system")
    ctx.register_command("memory_import", memory_import, "Importuje pamięć z pliku JSON.", "system")
