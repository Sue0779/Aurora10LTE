C_RESET = "\033[0m"
C_CMD   = "\033[34m"  # niebieski

def register(ctx):
    def help_cmd(ctx, *args):
        print("Dostępne komendy:")
        for name, data in sorted(ctx.commands.items()):
            help_text = data.get("help", "")
            print(f"  {C_CMD}{name:<15}{C_RESET} – {help_text}")
    ctx.register_command("help", help_cmd, "Lista komend.")
