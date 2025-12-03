import os
import shutil
from pathlib import Path
import hashlib

def _baseline_root(ctx):
    return ctx.root / "baseline"

def _list_snapshots(ctx):
    b = _baseline_root(ctx)
    if not b.exists():
        return []
    snaps = []
    for p in b.iterdir():
        if p.is_dir() and p.name.startswith("baseline_"):
            snaps.append(p)
    snaps.sort(key=lambda p: p.name)
    return snaps

def _latest_snapshot(ctx):
    snaps = _list_snapshots(ctx)
    return snaps[-1] if snaps else None

def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def _status_line(ok: bool, label: str, detail: str = ""):
    prefix = "[OK]" if ok else "[WARN]"
    if detail:
        print(f"{prefix} {label}: {detail}")
    else:
        print(f"{prefix} {label}")

def _verify_core(ctx, snap):
    print("\n[doctor] Weryfikuję core/")
    core_now = ctx.root / "core"
    core_snap = snap / "core"
    files = [
        "cli.py",
        "context.py",
        "ai_primary.py",
        "fs_api.py",
        "exec_api.py",
        "plugin_loader.py",
        "__init__.py",
    ]
    results = {"ok": [], "missing": [], "modified": [], "no_baseline": []}

    for name in files:
        now_p = core_now / name
        snap_p = core_snap / name
        if not snap_p.exists():
            results["no_baseline"].append(name)
            _status_line(False, f"core/{name}", "brak w snapshotcie")
            continue
        if not now_p.exists():
            results["missing"].append(name)
            _status_line(False, f"core/{name}", "BRAK – można naprawić z snapshotu")
            continue
        if _hash_file(now_p) == _hash_file(snap_p):
            results["ok"].append(name)
            _status_line(True, f"core/{name}", "zgodne ze snapshotem")
        else:
            results["modified"].append(name)
            _status_line(False, f"core/{name}", "ZMIENIONE – różne od snapshotu")

    return results

def _verify_plugins(ctx, snap):
    print("\n[doctor] Weryfikuję plugins/")
    plug_now = ctx.root / "plugins"
    plug_snap = snap / "plugins"

    results = {"ok": [], "missing": [], "modified": [], "extra": []}

    if not plug_snap.exists():
        print("[WARN] Snapshot nie ma katalogu plugins/")
        return results

    # pluginy z snapshotu
    for p in plug_snap.iterdir():
        if not p.is_dir():
            continue
        name = p.name
        now_p = plug_now / name
        snap_plugin_py = p / "plugin.py"
        now_plugin_py = now_p / "plugin.py"

        if not now_p.exists():
            results["missing"].append(name)
            _status_line(False, f"plugin {name}", "BRAK – można przywrócić z snapshotu")
            continue

        if not snap_plugin_py.exists() or not now_plugin_py.exists():
            results["modified"].append(name)
            _status_line(False, f"plugin {name}", "brak plugin.py po którejś stronie")
            continue

        if _hash_file(now_plugin_py) == _hash_file(snap_plugin_py):
            results["ok"].append(name)
            _status_line(True, f"plugin {name}", "zgodny ze snapshotem")
        else:
            results["modified"].append(name)
            _status_line(False, f"plugin {name}", "ZMIENIONY – różny od snapshotu")

    # pluginy EXTRA (nie ma ich w snapshot)
    snap_names = {p.name for p in plug_snap.iterdir() if p.is_dir()}
    if plug_now.exists():
        for p in plug_now.iterdir():
            if p.is_dir() and p.name not in snap_names:
                results["extra"].append(p.name)
                _status_line(True, f"plugin {p.name}", "DODATKOWY (spoza snapshotu)")

    return results

def _verify_wrapper(ctx, snap):
    print("\n[doctor] Weryfikuję wrapper aurora")
    snap_wrap = snap / "wrapper_aurora"
    now_wrap = Path.home() / ".local" / "bin" / "aurora"
    res = {"status": "ok"}

    if not snap_wrap.exists():
        _status_line(False, "wrapper", "brak w snapshotcie")
        res["status"] = "no_baseline"
        return res

    if not now_wrap.exists():
        _status_line(False, "wrapper", "BRAK – można przywrócić z snapshotu")
        res["status"] = "missing"
        return res

    if _hash_file(now_wrap) == _hash_file(snap_wrap):
        _status_line(True, "wrapper", "zgodny ze snapshotem")
        res["status"] = "ok"
    else:
        _status_line(False, "wrapper", "ZMIENIONY – różny od snapshotu")
        res["status"] = "modified"

    return res

def _repair_core(ctx, snap):
    print("\n[doctor_repair] Naprawiam core/")
    core_now = ctx.root / "core"
    core_snap = snap / "core"
    files = [
        "cli.py",
        "context.py",
        "ai_primary.py",
        "fs_api.py",
        "exec_api.py",
        "plugin_loader.py",
        "__init__.py",
    ]
    for name in files:
        now_p = core_now / name
        snap_p = core_snap / name
        if not snap_p.exists():
            continue
        # Przywracamy brakujące lub różne od snapshotu
        if (not now_p.exists()) or (_hash_file(now_p) != _hash_file(snap_p)):
            shutil.copy2(snap_p, now_p)
            print(f"[REPAIR] core/{name} przywrócony ze snapshotu.")

def _repair_plugins(ctx, snap):
    print("\n[doctor_repair] Naprawiam plugins/")
    plug_now = ctx.root / "plugins"
    plug_snap = snap / "plugins"
    if not plug_snap.exists():
        print("[doctor_repair] Snapshot nie ma katalogu plugins/ – pomijam.")
        return
    for p in plug_snap.iterdir():
        if not p.is_dir():
            continue
        name = p.name
        now_p = plug_now / name
        snap_plugin_py = p / "plugin.py"
        now_plugin_py = now_p / "plugin.py"

        if not now_p.exists():
            shutil.copytree(p, now_p)
            print(f"[REPAIR] plugin {name} – brakujący, przywrócony ze snapshotu.")
            continue

        if not snap_plugin_py.exists():
            continue

        need_repair = False
        if not now_plugin_py.exists():
            need_repair = True
        else:
            if _hash_file(now_plugin_py) != _hash_file(snap_plugin_py):
                need_repair = True

        if need_repair:
            shutil.rmtree(now_p)
            shutil.copytree(p, now_p)
            print(f"[REPAIR] plugin {name} – nadpisany stanem snapshotu.")

def _repair_wrapper(ctx, snap):
    print("\n[doctor_repair] Naprawiam wrapper aurora")
    snap_wrap = snap / "wrapper_aurora"
    now_wrap = Path.home() / ".local" / "bin" / "aurora"
    if not snap_wrap.exists():
        print("[doctor_repair] Snapshot nie zawiera wrappera – pomijam.")
        return
    now_wrap.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(snap_wrap, now_wrap)
    print(f"[REPAIR] wrapper aurora przywrócony ze snapshotu.")

def register(ctx):

    def doctor(cmd_ctx, *a):
        """Szybka diagnostyka: core + plugins + wrapper."""
        snap = _latest_snapshot(cmd_ctx)
        if not snap:
            print("[doctor] Brak snapshotów. Uruchom aurora_snapshot.sh.")
            return
        print(f"[doctor] Używany snapshot: {snap.name}")
        _verify_core(cmd_ctx, snap)
        _verify_plugins(cmd_ctx, snap)
        _verify_wrapper(cmd_ctx, snap)
        print("\n[doctor] Gotowe. Użyj: doctor_verify lub doctor_repair.")

    def doctor_snapshots(cmd_ctx, *a):
        snaps = _list_snapshots(cmd_ctx)
        if not snaps:
            print("[doctor_snapshots] Brak snapshotów w ~/.aurora/baseline/")
            return
        print("[doctor_snapshots] Dostępne snapshoty:")
        for p in snaps:
            meta = p / "metadata.json"
            info = ""
            if meta.exists():
                try:
                    import json
                    d = json.loads(meta.read_text())
                    info = d.get("created","")
                except Exception:
                    pass
            print(f"  {p.name}  {info}")

    def _select_snapshot(cmd_ctx, args):
        snaps = _list_snapshots(cmd_ctx)
        if not snaps:
            print("[doctor] Brak snapshotów. Uruchom aurora_snapshot.sh.")
            return None
        if args:
            name = args[0]
            for p in snaps:
                if p.name == name:
                    return p
            print(f"[doctor] Nie znaleziono snapshotu: {name}")
            return None
        return snaps[-1]

    def doctor_verify(cmd_ctx, *a):
        snap = _select_snapshot(cmd_ctx, a)
        if not snap:
            return
        print(f"[doctor_verify] Sprawdzam względem snapshotu: {snap.name}")
        _verify_core(cmd_ctx, snap)
        _verify_plugins(cmd_ctx, snap)
        _verify_wrapper(cmd_ctx, snap)
        print("\n[doctor_verify] Zakończono weryfikację.")

    def doctor_repair(cmd_ctx, *a):
        snap = _select_snapshot(cmd_ctx, a)
        if not snap:
            return
        print(f"[doctor_repair] UWAGA: Przywracam stan z snapshotu: {snap.name}")
        print("Operacja obejmuje: core/, plugins/, wrapper aurora.")
        _repair_core(cmd_ctx, snap)
        _repair_plugins(cmd_ctx, snap)
        _repair_wrapper(cmd_ctx, snap)
        print("\n[doctor_repair] Naprawa zakończona. Uruchom ponownie powłokę aurora.")

    def doctor_fix(cmd_ctx, *a):
        """Alias kompatybilności – napraw wszystko."""
        return doctor_repair(cmd_ctx, *a)

    ctx.register_command("doctor", doctor, "Diagnostyka Aurory (core+plugins+wrapper).", "system")
    ctx.register_command("doctor_snapshots", doctor_snapshots, "Lista snapshotów Aurory.", "system")
    ctx.register_command("doctor_verify", doctor_verify, "Pełna weryfikacja względem snapshotu.", "system")
    ctx.register_command("doctor_repair", doctor_repair, "Naprawa core/plugins/wrapper ze snapshotu.", "system")
    ctx.register_command("doctor_fix", doctor_fix, "Alias: napraw wszystko (snapshot).", "system")
