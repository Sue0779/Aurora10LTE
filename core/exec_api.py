import subprocess, shlex, time, json, os

WHITELIST = {"ls","cat","stat","find","head","tail","wc","python3"}
BLACKLIST = {"rm","sudo","mount","dd","kill","systemctl","iptables",
             "curl","wget","ssh","nc","telnet"}

class ExecAPI:
    def __init__(self, ctx):
        self.ctx = ctx
        self.timeout = 8
        self.max_steps = 10

    def _sanitize(self, cmd):
        if not cmd:
            raise Exception("Pusta komenda.")
        prog = cmd[0]
        base = os.path.basename(prog)
        if base in BLACKLIST:
            raise Exception(f"Zabroniona komenda: {base}")
        if base not in WHITELIST:
            raise Exception(f"Komenda niedozwolona: {base}")
        return cmd

    def run(self, cmd):
        cmd = self._sanitize(cmd)
        try:
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            t0 = time.time()
            while p.poll() is None:
                if time.time() - t0 > self.timeout:
                    p.kill()
                    raise Exception("Timeout ExecAPI.")
                time.sleep(0.05)

            out, err = p.communicate()
            return {
                "cmd": cmd,
                "returncode": p.returncode,
                "stdout": out,
                "stderr": err
            }
        except Exception as e:
            raise Exception(f"ExecAPI błąd: {e}")

    def run_sequence(self, plan):
        if len(plan) > self.max_steps:
            raise Exception("Zbyt wiele kroków ExecAPI.")
        results = []
        for step in plan:
            if not isinstance(step, list):
                raise Exception("Plan: każdy krok musi być listą argv.")
            results.append(self.run(step))
        return results
