import os
import shutil
from pathlib import Path
import datetime
import json

def _now():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def _aurora_root(ctx):
    return ctx.root

def _wrapper_path():
    return Path.home() / ".local" / "bin" / "aurora"

def _baseline_dir(ctx):
    return ctx.root / "baseline"

def register(ctx):

    def snapshot_create(cmd_ctx, *a):
        """Tworzy nowy snapshot Aurory (core + plugins + wrapper)."""
        snap_name = f"baseline_{_now()}"
        snap_dir = _baseline_dir(cmd_ctx) / snap_name

        print(f"Nowy snapshot: {snap_name}")
        ans = input("Utworzyć snapshot? (tak/nie): ").strip().lower()
        if ans not in ("tak", "t", "yes", "y"):
            print("Przerwano.")
            return

        root = _aurora_root(cmd_ctx)
        core = root / "core"
        plugins = root / "plugins"
        wrapper = _wrapper_path()

        snap_dir.mkdir(parents=True, exist_ok=False)
        (snap_dir / "core").mkdir()
        (snap_dir / "plugins").mkdir()

        # Kopiuj core/
        print("[1] Kopiuję core/ ...")
        for f in core.iterdir():
            if f.is_file() and f.suffix == ".py":
                shutil.copy2(f, snap_dir / "core" / f.name)

        # Kopiuj plugins/
        print("[2] Kopiuję plugins/ ...")
        shutil.copytree(plugins, snap_dir / "plugins", dirs_exist_ok=True)

        # Kopiuj wrapper
        print("[3] Kopiuję wrapper aurora ...")
        if wrapper.exists():
            shutil.copy2(wrapper, snap_dir / "wrapper_aurora")
        else:
            print("[WARN] Wrapper ~.local/bin/aurora nie istnieje")

        # Metadata
        print("[4] Tworzę metadata.json ...")
        meta = {
            "name": snap_name,
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "aurora_root": str(root),
            "wrapper": str(wrapper),
        }
        with open(snap_dir / "metadata.json", "w") as fp:
            json.dump(meta, fp, indent=2)

        print("\n[OK] Snapshot zapisany w:")
        print(f"     {snap_dir}")
        print("Snapshot dostępny dla: doctor, doctor_verify, doctor_repair")

    ctx.register_command(
        "snapshot_create",
        snapshot_create,
        "Tworzy snapshot Aurory (core/plugins/wrapper) z potwierdzeniem.",
        "system",
    )

