def register(ctx):

    # ========================================
    #  SAFETY: formatowanie wpisu w commands[]
    # ========================================
    def _describe_entry(name, entry):
        """
        Zwraca opis komendy NIE WYWOŁUJĄC entry.
        Obsługuje:
          – funkcję
          – dict (metadane)
          – inne typy (błąd)
        """
        t = type(entry).__name__

        # FUNKCJA – OK
        if callable(entry):
            return f"(funkcja: {t})"

        # SŁOWNIK – OK
        if isinstance(entry, dict):
            return entry.get("help", "(brak opisu)")

        # FORMAT NIEZNANY
        return f"[nieznany obiekt: {t}]"

    # ========================================
    #  LISTA PLUGINÓW / KOMEND
    # ========================================
    def plugin_list(cmd_ctx, *a):
        print("[plugin list]")

        for name in sorted(cmd_ctx.commands.keys()):
            entry = cmd_ctx.commands[name]
            desc = _describe_entry(name, entry)
            print(f"  {name:16} – {desc}")

    # ========================================
    #  ALIAS: 'plugin'
    # ========================================
    def plugin_cmd(cmd_ctx, *a):
        return plugin_list(cmd_ctx, *a)

    # ========================================
    #  REJESTRACJA
    # ========================================
    ctx.register_command(
        "plugin_list",
        plugin_list,
        "Lista komend zarejestrowanych w systemie.",
        "system"
    )

    ctx.register_command(
        "plugin",
        plugin_cmd,
        "Plugin manager – lista komend.",
        "system"
    )
