from pathlib import Path

def register(ctx):

    def policy(ctx, *a):
        print("[policy]")
        print("AuroraOS – zasady bezpieczeństwa wykonania:")
        print()
        print("1) ExecAPI:")
        print("   - Biała lista komend: ls, cat, stat, find, head, tail, wc, python3")
        print("   - Czarna lista m.in.: rm, sudo, mount, dd, kill, systemctl, iptables, curl, wget, ssh, nc, telnet")
        print("   - Timeout na procesy, ograniczona liczba kroków.")
        print()
        print("2) FSAPI:")
        print("   - Ścieżki są rozwijane przez ~ oraz normalizowane.")
        print("   - Sandbox jest zakotwiczony w katalogu domowym użytkownika.")
        print()
        print("3) Plug-iny:")
        print("   - Ładowane z:", ctx.root / "plugins")
        print("   - Błędy przy rejestracji pluginu nie zatrzymują powłoki – są logowane.")
        print()
        print("4) LLM:")
        print("   - AI nie może samodzielnie wykonywać komend poza ExecAPI.")
        print("   - Decyzje o wykonaniu są zawsze jawne na poziomie powłoki.")

    ctx.register_command("policy", policy, "Zasady bezpieczeństwa Aurory.", "system")
