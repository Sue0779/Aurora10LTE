def dump(ctx):
    print("=== DEBUG: ctx.commands ===")
    for name, obj in ctx.commands.items():
        print(f"- {name}: {type(obj)}")
        if isinstance(obj, dict):
            print("  [BAD] Komenda jest dict, nie callable!")
    print("==============================")
