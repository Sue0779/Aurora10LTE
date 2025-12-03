from pathlib import Path
import time, json

def _sessions_dir(ctx):
    sdir = ctx.root / "sessions"
    sdir.mkdir(parents=True, exist_ok=True)
    return sdir

def register(ctx):

    def load_list(ctx, *a):
        sdir = _sessions_dir(ctx)
        print("[load list] Dostępne pliki sesji:")
        for p in sorted(sdir.glob("*.json")):
            print(" -", p.name)

    def load_save(ctx, *a):
        """Zapisuje snapshot profilu i pamięci."""
        sdir = _sessions_dir(ctx)
        ts = time.strftime("%Y%m%d_%H%M%S")
        path = sdir / f"session_{ts}.json"
        data = {
            "profile": ctx.profile,
        }
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print("[load save] Zapisano:", path)

    def load_cmd(ctx, *a):
        if not a:
            print("Użycie: load <list|save>")
            print("  load list  – lista zapisanych sesji")
            print("  load save  – zapisuje bieżący stan profilu")
            return
        sub = a[0]
        if sub == "list":
            return load_list(ctx)
        if sub == "save":
            return load_save(ctx)
        print("Nieznana subkomenda load:", sub)

    ctx.register_command("load", load_cmd, "System sesji (lista/zapis).", "system")
