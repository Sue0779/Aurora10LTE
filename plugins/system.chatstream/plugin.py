import json

def _save_profile(ctx):
    ctx.profile_path.parent.mkdir(parents=True, exist_ok=True)
    ctx.profile_path.write_text(json.dumps(ctx.profile, indent=2, ensure_ascii=False))

def register(ctx):

    def chat_on(ctx, *a):
        ctx.profile["streaming"] = True
        _save_profile(ctx)
        print("[chat_on] Streaming w profilu: ON")

    def chat_off(ctx, *a):
        ctx.profile["streaming"] = False
        _save_profile(ctx)
        print("[chat_off] Streaming w profilu: OFF")

    ctx.register_command("chat_on", chat_on, "Włącza streaming modelu (ustawienie w profilu).", "ai")
    ctx.register_command("chat_off", chat_off, "Wyłącza streaming modelu (ustawienie w profilu).", "ai")
