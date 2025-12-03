def register(ctx):
    def handler(ctx, *args):
        print(" ".join(args))
    ctx.register_command("echo", handler, "Echo zwraca argumenty.")
