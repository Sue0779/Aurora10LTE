import readline
import os

from core.context import AuroraContext
from core.plugin_loader import load_plugins

RESET = "\033[0m"
YELLOW = "\033[93m"
CYAN = "\033[96m"

# ======================================================
#            DWU-WYRAZOWY PARSER KOMEND
# ======================================================
def process_command(ctx, line):

    line = line.strip()
    if not line:
        return

    # rozbij komendę NA SAMYM POCZĄTKU
    parts = line.split()

    # SPECJALNE: obsługa ai <sub> <args...>
    if parts[0] == "ai" and len(parts) >= 2:
        sub = parts[1]
        rest = parts[2:]
        return ctx.call("ai", sub, *rest)

    # Tryb AI – jednorazowe pytania
    if line.startswith("@"):
        return ctx.ai.ask(line[1:].strip())

    # Alias: chat / chat -m <model>
    if line.startswith("chat"):
        parts = line.split()
        if len(parts) == 1:
            return ctx.ai.chat()
        if len(parts) == 3 and parts[1] == "-m":
            return ctx.ai.chat(model=parts[2])
        print("Użycie: chat lub chat -m <model>")
        return

    # Tryb chat z ukośnikiem
    if line.startswith("/chat"):
        parts = line.split()
        if len(parts) == 1:
            return ctx.ai.chat()
        if len(parts) == 3 and parts[1] == "-m":
            return ctx.ai.chat(model=parts[2])
        print("Użycie: /chat lub /chat -m <model>")
        return

    # 1-słowo → klasyczna komenda
    if len(parts) == 1:
        cmd = parts[0]
        return ctx.call(cmd)

    # DWU-WYRAZOWE KOMENDY
    mod = parts[0]
    sub = parts[1]
    rest = parts[2:]

    # snapshot create → snapshot_create
    combined = f"{mod}_{sub}"
    if combined in ctx.commands:
        return ctx.call(combined, *rest)

    # jeśli istnieje moduł → deleguj subkomendę
    if mod in ctx.commands:
        return ctx.call(mod, sub, *rest)

    print(f"Nieznana komenda: {line}")


def _completer_factory(ctx):
    def complete(text, state):
        options = [name for name in ctx.commands.keys() if name.startswith(text)]
        options.sort()
        if state < len(options):
            return options[state]
        return None
    return complete


# ======================================================
#             GŁÓWNA FUNKCJA CLI
# ======================================================
def _prompt(ctx):
    profile = "default"
    if isinstance(ctx.profile, dict) and "name" in ctx.profile:
        profile = ctx.profile["name"]
    return f"{YELLOW}[{profile}] aurora>{RESET} "
def main():
    root = os.path.expanduser("~/.aurora")
    ctx = AuroraContext(root)

    # Załaduj pluginy
    from core.plugin_loader import load_plugins as _load
    _load(ctx)

    # TAB-completion
    readline.parse_and_bind("tab: complete")
    readline.set_completer(_completer_factory(ctx))

    print(f"{CYAN}Aurora 10 LTE — modułowa powłoka AI{RESET}")
    while True:
        try:
            line = input(_prompt(ctx))
        except (EOFError, KeyboardInterrupt):
            print()
            break
        try:
            process_command(ctx, line)
        except Exception as e:
            print(f"{YELLOW}[BŁĄD] {e}{RESET}")
            ctx.log.error(f"CLI error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
