import os, textwrap

def register(ctx):

    def _wrap(txt):
        print(textwrap.fill(txt, width=78))

    def diag_basic(ctx, *a):
        print("[diag basic]")
        print("Aurora root:", ctx.root)
        print("Profil:", ctx.profile)
        api = os.getenv("OPENAI_API_KEY")
        print("OPENAI_API_KEY:", "OK" if api else "BRAK")

    def diag_openai(ctx, *a):
        print("[diag openai]")
        if not os.getenv("OPENAI_API_KEY"):
            print("BRAK OPENAI_API_KEY – pomijam test OpenAI.")
            return
        try:
            chunks = []
            for ch in ctx.ai.stream("ping"):
                chunks.append(ch)
                if len("".join(chunks)) > 40:
                    break
            print("OK: model odpowiada.")
        except Exception as e:
            print("BŁĄD AI:", e)

    def diag_fs(ctx, *a):
        print("[diag fs]")
        try:
            items = ctx.fs.ls("~")
            print(f"OK: FS działa, ls ~ → {len(items)} elementów.")
        except Exception as e:
            print("BŁĄD FS:", e)

    def diag_exec(ctx, *a):
        print("[diag exec]")
        try:
            res = ctx.exec.run(["ls"])
            print(f"OK: Exec działa, returncode {res['returncode']}")
        except Exception as e:
            print("BŁĄD Exec:", e)

    def diag(ctx, *a):
        diag_basic(ctx)
        diag_openai(ctx)
        diag_fs(ctx)
        diag_exec(ctx)

    ctx.register_command("diag_basic", diag_basic, "Podstawowe informacje o systemie.")
    ctx.register_command("diag_openai", diag_openai, "Test połączenia z OpenAI.")
    ctx.register_command("diag_fs", diag_fs, "Test FSAPI.")
    ctx.register_command("diag_exec", diag_exec, "Test ExecAPI.")
    ctx.register_command("diag", diag, "Pełna diagnostyka systemu Aurora.")
