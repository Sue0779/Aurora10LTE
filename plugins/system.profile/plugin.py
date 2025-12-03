import json

def register(ctx):

    def profile_show(ctx, *a):
        print("[profile show]")
        print("Plik profilu:", ctx.profile_path)
        print("Zawartość:", ctx.profile)

    def profile_set(ctx, *a):
        if len(a) < 2:
            print("Użycie: profile_set <klucz> <wartość>")
            return
        key = a[0]
        value = " ".join(a[1:])
        # prosta heurystyka typów
        if value.lower() in ("true", "false"):
            value = value.lower() == "true"
        else:
            try:
                if "." in value:
                    value = float(value)
                else:
                    value = int(value)
            except:
                pass
        ctx.profile[key] = value
        ctx.profile_path.parent.mkdir(parents=True, exist_ok=True)
        ctx.profile_path.write_text(json.dumps(ctx.profile, indent=2, ensure_ascii=False))
        print(f"[profile set] {key} = {value}")

    def profile_reload(ctx, *a):
        try:
            data = json.loads(ctx.profile_path.read_text())
            ctx.profile = data
            print("[profile reload] Profil przeładowany.")
        except Exception as e:
            print("[profile reload] Błąd:", e)

    def profile_cmd(ctx, *a):
        # alias: profile → profile_show
        return profile_show(ctx, *a)

    ctx.register_command("profile_show", profile_show, "Pokazuje bieżący profil.", "system")
    ctx.register_command("profile_set", profile_set, "Ustawia wartość w profilu.", "system")
    ctx.register_command("profile_reload", profile_reload, "Przeładowuje profil z pliku.", "system")
    ctx.register_command("profile", profile_cmd, "Manager profilu.", "system")
