import json
import textwrap
import io
import contextlib
from openai import OpenAI

client = OpenAI()

CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


# ============================================================
#  LOW-LEVEL: wywołanie LLM (chat.completions)
# ============================================================

def _call_llm(messages, model="gpt-5.1"):
    """
    messages: lista słowników [{'role':'system'/'user'/'assistant','content':'...'}]
    """
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
    )
    return resp.choices[0].message.content


# ============================================================
#  TOOLS: integracja FSAPI / ExecAPI z agentem
# ============================================================

def _tool_fs_ls(ctx, args):
    path = args[0] if args else "~"
    try:
        entries = ctx.fs.ls(path)
        if isinstance(entries, (list, tuple)):
            return "\n".join(str(e) for e in entries)
        return str(entries)
    except Exception as e:
        return f"[fs_ls ERROR] {e}"


def _tool_fs_tree(ctx, args):
    path = args[0] if args else "~"
    depth = int(args[1]) if len(args) > 1 else 2
    try:
        # FSAPI.tree nie przyjmuje nazwanych argumentów max_depth
        tree_str = ctx.fs.tree(path, depth)
        return str(tree_str)
    except Exception as e:
        return f"[fs_tree ERROR] {e}"


def _tool_fs_cat(ctx, args):
    if not args:
        return "[fs_cat] Użycie: fs_cat <plik>"
    path = args[0]
    try:
        content = ctx.fs.cat(path)
        return str(content)
    except Exception as e:
        return f"[fs_cat ERROR] {e}"


def _tool_fs_info(ctx, args):
    if not args:
        return "[fs_info] Użycie: fs_info <plik/katalog>"
    path = args[0]
    try:
        info = ctx.fs.info(path)
        if isinstance(info, dict):
            return json.dumps(info, indent=2, ensure_ascii=False)
        return str(info)
    except Exception as e:
        return f"[fs_info ERROR] {e}"


def _tool_exec(ctx, args):
    if not args:
        return "[exec] Użycie: exec <komenda ...>"
    cmd = " ".join(args)
    try:
        code, out, err = ctx.exec.run(cmd)
        out = out or ""
        err = err or ""
        return f"$ {cmd}\n[exit {code}]\n{out}\n{err}"
    except Exception as e:
        return f"[exec ERROR] {e}"


TOOLS = {
    "fs_ls": _tool_fs_ls,
    "fs_tree": _tool_fs_tree,
    "fs_cat": _tool_fs_cat,
    "fs_info": _tool_fs_info,
    "exec": _tool_exec,
}


# ============================================================
#  PROMPT SYSTEMOWY AGENA
# ============================================================

AGENT_SYSTEM_PROMPT = """
Jesteś agentem AI działającym wewnątrz systemu AuroraOS.
Masz do dyspozycji NARZĘDZIA (TOOLS), które są wykonywane przez powłokę.

Dostępne TOOLS:
- fs_ls <path?>                – lista plików (domyślnie katalog domowy),
- fs_tree <path?> <depth?>     – drzewo katalogów (domyślnie depth=2),
- fs_cat <path>                – podgląd pliku tekstowego,
- fs_info <path>               – metadane pliku/katalogu (rozmiar, typ, itp.),
- exec <komenda ...>           – wykonanie bezpiecznych komend systemowych.

ZASADY:
1. ZAWSZE najpierw wyjaśnij sobie w myślach (w polu "thought"), co chcesz zrobić.
2. Jeśli potrzebujesz danych z systemu, użyj odpowiedniego TOOL:
   - DO listowania → fs_ls / fs_tree
   - DO czytania pliku → fs_cat
   - DO metadanych → fs_info
   - DO prostych komend systemowych → exec
3. Jeśli nie potrzebujesz już więcej narzędzi, ustaw "tool" na null, "finish" na true
   i wpisz końcową odpowiedź w "final_answer".
4. ZWRACAJ WYŁĄCZNIE POPRAWNY JSON (bez komentarzy, bez tekstu przed/po).

FORMAT ODPOWIEDZI (JSON):
{
  "thought": "krótkie wyjaśnienie po polsku, co teraz robisz",
  "tool": "fs_ls" | "fs_tree" | "fs_cat" | "fs_info" | "exec" | null,
  "args": ["lista argumentów jako stringi"],
  "finish": false | true,
  "final_answer": "jeśli finish=true – kompletna odpowiedź dla użytkownika; w przeciwnym razie pusty string"
}
""".strip()


def _shorten(text, limit=1200):
    text = str(text)
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[ucięto]..."


# ============================================================
#  PARSER MULTI-JSON (wiele ramek w jednej odpowiedzi)
# ============================================================

def _parse_tool_decision(raw):
    """
    Obsługa:
    - pojedynczy poprawny JSON,
    - wiele obiektów JSON sklejonych jeden po drugim.
    Strategia:
      * jeśli znajdę wiele obiektów, wybieram:
        - najpierw pierwszy z polem 'tool' nie-null
        - w przeciwnym razie ostatni obiekt.
    """
    raw = raw.strip()
    # Najpierw prosty przypadek – pojedynczy JSON
    try:
        return json.loads(raw)
    except Exception:
        pass

    # Próba ekstrakcji wielu obiektów JSON na podstawie nawiasów klamrowych
    objs = []
    buf = ""
    depth = 0
    in_string = False
    escape = False

    for ch in raw:
        if in_string:
            buf += ch
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            buf += ch
            continue

        if ch == "{":
            depth += 1
            buf += ch
            continue

        if ch == "}":
            depth -= 1
            buf += ch
            if depth == 0 and buf.strip():
                candidate = buf.strip()
                try:
                    obj = json.loads(candidate)
                    objs.append(obj)
                except Exception:
                    # ignorujemy śmieci
                    pass
                buf = ""
            continue

        if depth > 0:
            buf += ch

    if not objs:
        raise ValueError("Nie udało się sparsować żadnego obiektu JSON z odpowiedzi modelu.")

    # Wybór obiektu sterującego
    chosen = None
    for o in objs:
        if isinstance(o, dict) and o.get("tool") not in (None, "", "null"):
            chosen = o
            break
    if chosen is None:
        chosen = objs[-1]

    return chosen


# ============================================================
#  INTERCEPTOR: uruchamianie komend jako TOOLS
# ============================================================

def _tool_simple_cmd(ctx, cmd_name, args):
    """
    Użycie istniejącej komendy Aurory jako narzędzia AI.
    Przechwytuje stdout + zwraca wynik jako string.
    """
    entry = ctx.commands.get(cmd_name)
    if not entry:
        return f"[TOOL ERROR] unknown command: {cmd_name}"

    handler = entry.get("handler")
    if not callable(handler):
        return f"[TOOL ERROR] handler for {cmd_name} is not callable"

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            result = handler(ctx, *args)
        except Exception as e:
            return f"[TOOL ERROR] {e}"

    out = buf.getvalue()
    if result is not None:
        return str(result)
    return out.strip() if out.strip() else "(empty)"


def _run_tool(ctx, tool_name, args):
    """
    Unified tool runner with stdout interception:
    - jeśli tool_name jest w TOOLS → używamy zarejestrowanego narzędzia,
    - w przeciwnym razie próbujemy użyć istniejącej komendy Aurory.
    """
    # Najpierw dedykowane narzędzia
    if tool_name in TOOLS:
        try:
            return TOOLS[tool_name](ctx, args)
        except Exception as e:
            return f"[TOOL EXEC ERROR] {e}"

    # Następnie spróbujmy potraktować to jako zwykłą komendę
    return _tool_simple_cmd(ctx, tool_name, args)


# ============================================================
#  AGENT: PLAN (bez wykonywania narzędzi)
# ============================================================

def _agent_plan(ctx, goal):
    model = ctx.profile.get("model", "gpt-5.1") if isinstance(ctx.profile, dict) else "gpt-5.1"

    prompt = f"""
CEL:
{goal}

ZADANIE:
Przygotuj SZCZEGÓŁOWY PLAN działań, które mógłby wykonać agent AuroraOS,
korzystając z narzędzi: fs_ls, fs_tree, fs_cat, fs_info, exec.

Wypisz:
1. Kroki (1, 2, 3, ...)
2. Dla każdego kroku: cel, przykładowe narzędzie, przykładowe argumenty, spodziewany wynik.

Odpowiadaj po polsku, w formie uporządkowanej listy.
    """.strip()

    messages = [
        {"role": "system", "content": "Jesteś asystentem planującym działania w systemie AuroraOS."},
        {"role": "user", "content": prompt},
    ]
    answer = _call_llm(messages, model=model)
    print(f"{CYAN}[ai plan] PLAN DZIAŁANIA DLA CELU:{RESET} {goal}")
    print(answer)
    if hasattr(ctx, "log"):
        ctx.log.info("[ai plan] goal=%s\n%s", goal, answer)


# ============================================================
#  AGENT: AUTO (wielokrokowy z tool-calling)
# ============================================================

def _agent_run(ctx, goal, max_steps=30):
    model = ctx.profile.get("model", "gpt-5.1") if isinstance(ctx.profile, dict) else "gpt-5.1"

    history = []
    last_observation = ""

    print(f"{CYAN}[ai auto] CEL:{RESET} {goal}")

    for step in range(1, max_steps + 1):
        print(f"{YELLOW}[ai auto] Krok {step}/{max_steps} – planuję...{RESET}")

        user_payload = {
            "goal": goal,
            "history": history,
            "last_observation": _shorten(last_observation),
        }

        messages = [
            {"role": "system", "content": AGENT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Zwróć WYŁĄCZNIE JSON w opisanym formacie, bez dodatkowego tekstu.\n"
                    + json.dumps(user_payload, ensure_ascii=False, indent=2)
                ),
            },
        ]

        raw = _call_llm(messages, model=model)
        if hasattr(ctx, "log"):
            ctx.log.info("[ai auto] STEP %d RAW:\n%s", step, raw)

        try:
            tool_decision = _parse_tool_decision(raw)
        except Exception:
            print(f"{RED}[ai auto] BŁĄD PARSOWANIA JSON ODP.:{RESET}")
            print(_shorten(raw, 800))
            break

        thought = tool_decision.get("thought", "")
        tool_name = tool_decision.get("tool", None)
        args = tool_decision.get("args", []) or []
        finish = bool(tool_decision.get("finish", False))
        final_answer = tool_decision.get("final_answer", "")

        print(f"{GREEN}[ai auto] myśl:{RESET} {thought}")

        history.append(
            {
                "step": step,
                "thought": thought,
                "tool": tool_name,
                "args": args,
                "observation": _shorten(last_observation),
            }
        )

        if finish or tool_name is None:
            print(f"{CYAN}[ai auto] ZAKOŃCZENIE:{RESET}")
            print(final_answer or "(brak final_answer)")
            break

        # Wykonanie narzędzia przez interceptor
        print(f"{YELLOW}[ai auto] TOOL:{RESET} {tool_name} {args}")
        observation = _run_tool(ctx, tool_name, args)
        last_observation = _shorten(observation)

        print(f"{CYAN}[ai auto] OBSERVATION:{RESET}")
        print(last_observation)

    else:
        print(f"{YELLOW}[ai auto] Osiągnięto maksymalną liczbę kroków ({max_steps}).{RESET}")
        if hasattr(ctx, "log"):
            ctx.log.warning("[ai auto] max_steps reached for goal=%s", goal)


# ============================================================
#  PROSTA KOMENDA: ai <pytanie...>
# ============================================================

def _ai_simple(ctx, question):
    model = ctx.profile.get("model", "gpt-5.1") if isinstance(ctx.profile, dict) else "gpt-5.1"

    system = """
Jesteś asystentem systemu AuroraOS.
Odpowiadasz po polsku, konkretnie i technicznie, bez infantylizacji.
Jeśli pytanie dotyczy plików, powłoki, pluginów – sugeruj użycie
narzędzi (fs_ls, fs_cat, exec, itp.), ale ich nie wykonujesz.
    """.strip()

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]
    answer = _call_llm(messages, model=model)
    print(f"{CYAN}[ai]{RESET} {answer}")
    # Lekki logging
    if hasattr(ctx, "log"):
        ctx.log.info("[ai simple] Q=%s\nA=%s", question, answer)


# ============================================================
#  REJESTRACJA KOMENDY `ai`
# ============================================================

def register(ctx):

    def ai(cmd_ctx, *args):
        if not args:
            print("Użycie:")
            print("  ai <pytanie ...>        – zwykłe pytanie do modelu")
            print("  ai auto <cel ...>       – agent wieloetapowy z narzędziami")
            print("  ai plan <cel ...>       – tylko plan działań, bez wykonywania")
            return

        sub = args[0]

        if sub == "auto":
            goal = " ".join(args[1:]).strip()
            if not goal:
                print("Użycie: ai auto <cel ...>")
                return
            return _agent_run(cmd_ctx, goal)

        if sub == "plan":
            goal = " ".join(args[1:]).strip()
            if not goal:
                print("Użycie: ai plan <cel ...>")
                return
            return _agent_plan(cmd_ctx, goal)

        # fallback: zwykłe pytanie
        question = " ".join(args).strip()
        return _ai_simple(cmd_ctx, question)

    ctx.register_command(
        "ai",
        ai,
        "AI-Kernel 3.1 – pytania, plan, auto (agent z tool-calling i multi-JSON).",
        "system",
    )
