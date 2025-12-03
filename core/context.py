import json
import sys
import logging
from pathlib import Path

from core.ai_primary import AIPRIMARY
from core.fs_api import FSAPI
from core.exec_api import ExecAPI
from core.plugin_loader import load_plugins


class AuroraContext:
    def __init__(self, root: str):
        # ROOT Aurory
        self.root = Path(root)

        # Rejestr komend – FORMAT C (dict)
        # { name: {"handler": func, "help": str, "group": str} }
        self.commands = {}
        self.command_help = {}
        self.command_group = {}

        # Profil runtime
        self.profile_path = self.root / "profiles" / "default.profile.json"
        self.profile = self._load_profile()

        # Ścieżki importów
        self._patch_sys_path()

        # Logger
        self.log = self._setup_logger()

        # Podsystemy
        self.ai = AIPRIMARY(self)
        self.fs = FSAPI(self)
        self.exec = ExecAPI(self)

        # Ładowanie pluginów
        load_plugins(self)

    # -------------------------------------
    # ŚCIEŻKI
    # -------------------------------------
    def _patch_sys_path(self):
        root = str(self.root)
        core = str(self.root / "core")
        plugins = str(self.root / "plugins")

        for p in (root, core, plugins):
            if p not in sys.path:
                sys.path.insert(0, p)

    # -------------------------------------
    # LOGGER
    # -------------------------------------
    def _setup_logger(self):
        log_dir = self.root / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "aurora.log"

        logger = logging.getLogger("Aurora")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            fh = logging.FileHandler(log_path)
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        return logger

    # -------------------------------------
    # PROFIL
    # -------------------------------------
    def _load_profile(self):
        if not self.profile_path.exists():
            return {}
        try:
            return json.loads(self.profile_path.read_text())
        except Exception:
            return {}

    # =====================================================
    #   REJESTRACJA KOMEND – FORMAT C (dict)
    # =====================================================
    def register_command(self, name, handler, help_text: str = "", group: str = "core"):
        """
        Jedyny poprawny format rejestracji:
        self.commands[name] = {
            "handler": <callable(ctx, *args)>,
            "help": "...",
            "group": "core|system|tools|fs|ai"
        }
        """
        self.commands[name] = {
            "handler": handler,
            "help": help_text,
            "group": group,
        }
        self.command_help[name] = help_text
        self.command_group[name] = group

    # ==========================================================
    #                WYWOŁYWANIE KOMEND
    # ==========================================================
    def call(self, name, *args):
        """Wywołuje komendę o nazwie name z argumentami args."""
        if name not in self.commands:
            print(f"Nieznana komenda: {name}")
            return

        entry = self.commands[name]

        # entry musi być dict = {'handler': func, 'help': "...", 'group': "..."}
        if not isinstance(entry, dict):
            print(f"[FATAL] Komenda '{name}' ma niepoprawny format (nie dict).")
            print(f"Obiekt: {entry}")
            return

        handler = entry.get("handler")
        if not callable(handler):
            print(f"[FATAL] Handler komendy '{name}' nie jest funkcją!")
            print(f"handler = {handler}")
            return

        try:
            return handler(self, *args)
        except Exception as e:
            print(f"[BŁĄD: {name}] {e}")
            self.log.error(f"Command '{name}' failed: {e}")
