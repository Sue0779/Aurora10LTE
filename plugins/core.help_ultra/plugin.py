import textwrap

BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
GRAY = "\033[90m"
RESET = "\033[0m"
BOLD = "\033[1m"

def register(ctx):

    # =============================
    # Baza danych komend i opisów
    # =============================
    COMMAND_DOCS = {
        "help": "Wyświetla listę dostępnych komend lub szczegółowy opis.",
        "diag": "Pełna diagnostyka systemu Aurora.",
        "fs_ls": "Lista plików w sandboxie.",
        "fs_tree": "Drzewo katalogów.",
        "fs_cat": "Odczyt pliku.",
        "profile_show": "Pokazuje bieżący profil.",
        "profile_set": "Ustawia wartość w profilu.",
        "doctor": "Sprawdza stan instalacji Aurory.",
        "exec": "Wykonuje bezpieczne komendy systemowe.",
        "ai": "AI-Kernel – silnik analizy (wkrótce w pełnej wersji).",
        "agent": "Agent krokowy AI.",
    }

    MODULE_DOCS = {
        "ai": "Silnik AI odpowiedzialny za streaming, modele, powłokę AI i chat.",
        "fs": "System plików w sandboxie, z ograniczeniami bezpieczeństwa.",
        "exec": "Bezpieczny executor poleceń – whitelist + blacklist.",
        "profile": "System profili i konfiguracji runtime.",
        "diag": "Diagnostyka Aurory.",
        "doctor": "Zaawansowana diagnostyka strukturalna instalacji.",
    }

    # ================
    # FORMATOWANIE
    # ================
    def title(t):
        print(f"{BOLD}{CYAN}=== {t} ==={RESET}")

    def section(t):
        print(f"\n{BOLD}{YELLOW}{t}{RESET}")

    def line(txt):
        print(textwrap.fill(txt, width=78))

    # ================
    # GŁÓWNA KOMENDA HELP
    # ================
    def help_cmd(ctx, *args):
        # -----------------------------------
        # HELP BEZ ARGUMENTÓW → lista komend
        # -----------------------------------
        if not args:
            title("AURORA – PODRĘCZNIK UŻYTKOWNIKA")
            section("Dostępne komendy:")

            for name in sorted(ctx.commands.keys()):
                doc = COMMAND_DOCS.get(name, "(brak opisu)")
                print(f"  {BLUE}{name:15}{RESET} – {doc}")

            section("Moduły systemowe:")
            for m, doc in MODULE_DOCS.items():
                print(f"  {CYAN}{m}{RESET} – {doc}")

            print()
            print(f"Więcej: {BOLD}help <komenda>{RESET}")
            print(f"         {BOLD}help <moduł>{RESET}")
            print(f"         {BOLD}tutorial{RESET}")
            return

        # -----------------------------------
        # help <nazwa> → szczegółowy opis
        # -----------------------------------
        target = args[0]

        # Komenda?
        if target in COMMAND_DOCS:
            title(f"Help: {target}")
            line(COMMAND_DOCS[target])
            return

        # Moduł?
        if target in MODULE_DOCS:
            title(f"Moduł: {target}")
            line(MODULE_DOCS[target])
            return

        # Nieznane
        print(f"{YELLOW}Brak dokumentacji dla:{RESET} {target}")

    # ================
    # TUTORIAL
    # ================
    def tutorial_cmd(ctx, *a):
        title("AURORA – SZYBKI START")
        section("1. Uruchomienie")
        line("Napisz 'aurora' w terminalu, aby uruchomić powłokę systemu AuroraOS.")

        section("2. Chat z AI")
        line("Użyj: /chat lub /chat -m gpt-5.1 aby wejść w tryb rozmowy strumieniowej.")

        section("3. Jednorazowa analiza AI")
        line("Poprzedź tekst znakiem '@':  @wyjaśnij czym jest AuroraOS")

        section("4. AI jako interpreter")
        line("Aurora może wykonywać kroki systemowe i je analizować (AI-Kernel 2.0).")

        section("5. System plików")
        line("Użyj fs_ls, fs_cat, fs_tree aby nawigować po sandboxie.")

        section("6. Bezpieczeństwo")
        line("ExecAPI blokuje niebezpieczne komendy (rm, sudo, dd itd.).")

        section("7. Diagnostyka")
        line("Użyj: diag  oraz: doctor  do pełnych testów instalacji.")

    # Rejestracja komend
    ctx.register_command("help", help_cmd, "System pomocy.")
    ctx.register_command("tutorial", tutorial_cmd, "Samouczek.")
