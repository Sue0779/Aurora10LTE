import shlex

def register(ctx):

    def exec_cmd(ctx, *a):
        if not a:
            print("Użycie: exec <komenda ...>")
            print("Przykład: exec ls -la")
            return
        argv = list(a)
        res = ctx.exec.run(argv)
        print("[exec] cmd:", " ".join(res["cmd"]))
        print("[exec] returncode:", res["returncode"])
        if res["stdout"]:
            print("--- STDOUT ---")
            print(res["stdout"].rstrip())
        if res["stderr"]:
            print("--- STDERR ---")
            print(res["stderr"].rstrip())

    ctx.register_command("exec", exec_cmd, "ExecAPI 2.0 – bezpieczne uruchamianie komend.", "system")
