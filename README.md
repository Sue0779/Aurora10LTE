Aurora 10 LTE — Modularna Powłoka AI dla Linux/Fedora

Nowa generacja lokalnych narzędzi AI, opartych na pluginach, sandboxie i inteligentnej automatyzacji.

Aurora10LTE to lekka, modularna, w pełni rozszerzalna powłoka AI, działająca jako „meta-warstwa” nad systemem Linux — łącząca interpretację komend, zewnętrzne pluginy, izolowany sandbox oraz agentowe modele LLM z obsługą tool-calling.

System jest projektowany jako własny ekosystem AI, który użytkownik może sam rozwijać: nowe komendy, własne pluginy, integracje, automatyzacje, snapshoty, profilowanie modeli i dynamiczną powłokę CLI.

✨ Najważniejsze funkcje
1. Modularna powłoka CLI

Kolorowany prompt ([default] aurora>).

Parser komend jedno- i dwuwyrazowych.

Obsługa aliasów (chat, /chat, @prompt).

Dynamiczne podpowiadanie (TAB-completion).

2. Architektura pluginów

Plugins/ zawiera kilkanaście modułów, m.in:

system.ai_kernel — agent LLM z multi-JSON i tool-calling.

system.chatstream — tryb ciągłego dialogu ze strumieniowaniem.

system.exec — sandboxowy interpreter komend.

system.fs — bezpieczne FSAPI (ls, tree, cat, info).

system.diag — diagnostyka rdzenia.

system.snapshot — snapshoty core/plugins/wrapper.

system.profile — profilowanie modelu i ustawień runtime.

core.help_ext, help_ultra, debug_commands — rozszerzone help & debug.

Każdy plugin rejestruje własny zestaw komend w runtime, co umożliwia tworzenie kompletnych rozszerzeń systemu.

3. AI-Kernel 3.1 (Agent)

Najbardziej zaawansowany komponent Aurory:

ai — zwykłe pytania.

ai plan — generowanie planów działania.

ai auto — w pełni autonomiczny agent wykonujący serię kroków z:

multi-JSON parsing,

unified run_tool (komendy i narzędzia),

logging każdego kroku,

obsługą błędów,

izolowanym dostępem do FSAPI i ExecAPI.

Agent może m.in:

przeglądać strukturę katalogów,

czytać pliki,

wykonywać bezpieczne komendy systemowe,

budować analizę krok po kroku,

kończyć gdy osiągnie cel.

4. Sandbox FSAPI + ExecAPI

Nie pozwala wyjść poza $HOME.

Każdy plik jest czyszczony i normalizowany.

Kontrolowana interpretacja komend systemowych (exec).

5. System sesji i pamięci

Zapisywanie/ładowanie sesji (load save, load list).

Pamięć trwała (memory, memory_set, memory_export, memory_import).

Profilowanie modeli (profile, profile_set, profile_show).

6. Snapshoty i autodiagnostyka

Tworzenie snapshotów core/plugins/wrapper.

Naprawa konfiguracji (doctor_repair, doctor_fix).

Weryfikacja integralności (doctor_verify).

Pełna diagnostyka (diag, diag_full).

📁 Struktura repozytorium
Aurora10LTE/
│
├── core/
│   ├── cli.py               # powłoka CLI, parsing, prompt, tab-completion
│   ├── context.py           # rdzeń runtime (komendy, FSAPI, ExecAPI, profil)
│   ├── ai_primary.py        # tryby: @prompt, chat, models
│   ├── fs_api.py            # sandbox FS (ls, tree, cat, info)
│   ├── exec_api.py          # sandbox exec
│   └── plugin_loader.py     # dynamiczne ładowanie pluginów
│
├── plugins/
│   ├── system.ai_kernel/    # agent AI 3.1 (auto, plan, multi-json)
│   ├── system.chatstream/
│   ├── system.exec/
│   ├── system.fs/
│   ├── system.diag/
│   ├── system.snapshot/
│   ├── system.profile/
│   ├── system.policy/
│   ├── system.plugin_manager/
│   ├── system.memory/
│   ├── tools.find/
│   ├── tools.grep/
│   ├── tools.inspect/
│   ├── core.echo/
│   ├── core.help_ext/
│   ├── core.help_ultra/
│   └── ...
│
├── installer/
│   └── setup.sh             # minimalny instalator (local-first)
│
└── README.md                # ten plik

🚀 Instalacja (Local-First, Linux/Fedora)
1. Pobierz repo
git clone git@github.com:TwojeRepo/Aurora10LTE.git
cd Aurora10LTE

2. Uruchom instalator
bash installer/setup.sh


Instalator:

tworzy ~/.aurora/,

kopiuje core i pluginy,

zakłada venv i instaluje zależności,

tworzy skrót aurora.

🧠 Przykłady użycia
Zwykłe pytanie
aurora> ai Jak działa Aurora?

Plan działań
aurora> ai plan sprawdz ~/.aurora

Agent wieloetapowy
aurora> ai auto przejrzyj pliki w ~/.aurora/core

Listowanie katalogu
aurora> fs_ls ~/.aurora/plugins

Podgląd pliku
aurora> fs_cat ~/.aurora/core/cli.py

Snapshot
aurora> snapshot_create

🛡️ Bezpieczeństwo

Aurora10LTE działa w modelu:

Local-First (cały runtime lokalnie),

Sandbox FSAPI z blokadą poza $HOME,

Kontrolowane tool-execution w agentach,

Brak ingerencji w system Linux (Audio, DBus, systemd, etc.).

🧩 Tworzenie własnych pluginów

Minimum:

def register(ctx):
    def hello(ctx, *args):
        print("Hello from plugin!")
    ctx.register_command("hello", hello, "Test plugin", "plugin")


Dodaj katalog:

~/.aurora/plugins/myplugin/plugin.py


i Aurora załaduje go automatycznie przy starcie.

📜 Licencja

Projekt udostępniany na licencji MIT,
z pełną swobodą modyfikacji i komercyjnego wykorzystania.
