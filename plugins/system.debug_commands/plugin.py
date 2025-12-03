def register(ctx):

    def debug_commands(cmd_ctx, *args):
        print("=== DEBUG: ctx.commands ===")
        for name, obj in cmd_ctx.commands.items():
            t = type(obj)
            print(f"- {name}: {t.__name__}")
            if not callable(obj):
                print(f"   [BAD] '{name}' nie jest funkcją!")
            if name in cmd_ctx.command_help:
                print(f"   help: {cmd_ctx.command_help[name]}")
            if name in cmd_ctx.command_group:
                print(f"   group: {cmd_ctx.command_group[name]}")
        print("========================================")

    ctx.register_command(
        "debug_commands",
        debug_commands,
        "Diagnoza rejestru komend — poprawny format funkcji.",
        "system",
    )
