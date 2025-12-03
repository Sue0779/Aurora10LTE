import json
from pathlib import Path

from openai import OpenAI


class AIPRIMARY:
    """
    Główny moduł AI w Aurorze.

    - obsługuje jednorazowe pytania '@...' (ask)
    - trzyma trwałą pamięć konwersacji w ~/.aurora/ai/history.json
    - jest niezależny od AI-Kernel (system.ai_kernel) i agenta (ai auto/ai plan)
    """

    def __init__(self, ctx):
        self.ctx = ctx
        self.client = OpenAI()

        self.ai_dir = ctx.root / "ai"
        self.ai_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.ai_dir / "history.json"

    # -----------------------------
    #  PAMIĘĆ KONWERSACJI (Opcja A)
    # -----------------------------
    def _load_history(self):
        if not self.history_path.exists():
            return []
        try:
            return json.loads(self.history_path.read_text())
        except Exception:
            return []

    def _save_history(self, history):
        try:
            self.history_path.write_text(
                json.dumps(history, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            print(f"[ai memory] Błąd zapisu historii: {e}")
            self.ctx.log.error(f"AI history save failed: {e}")

    def _build_messages(self, user_content: str):
        """
        Tworzy pełny kontekst do wysłania do modelu:
        - system prompt
        - CAŁA dotychczasowa historia (Opcja A – pełna pamięć)
        - bieżące pytanie użytkownika
        """
        history = self._load_history()

        system_msg = {
            "role": "system",
            "content": (
                "Jesteś modułem AI w systemie AuroraOS uruchomionym w powłoce "
                "terminalowej użytkownika na Linuksie. Odpowiadasz po polsku, "
                "precyzyjnie, technicznie, bez ozdobników, zwięźle, ale rzeczowo. "
                "Jeśli pytanie dotyczy systemu Aurora, tłumaczysz jego działanie "
                "na poziomie eksperckim, ale czytelnym."
            ),
        }

        messages = [system_msg]
        # historia to lista dictów {"role": "user"|"assistant", "content": "..."}
        messages.extend(history)
        messages.append({"role": "user", "content": user_content})
        return messages, history

    # -----------------------------
    #  JEDNORAZOWA ODPOWIEDŹ (@...)
    # -----------------------------
    def ask(self, content: str):
        """
        Wywoływane z CLI przez prefiks '@' – np.:
          @wyjaśnij czym jest AuroraOS
        """
        model = self.ctx.profile.get("model", "gpt-5.1")
        messages, history = self._build_messages(content)

        try:
            resp = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,
            )
            reply = resp.choices[0].message.content
        except Exception as e:
            print(f"[ai error] {e}")
            self.ctx.log.error(f"AI error: {e}")
            return

        print(f"ai[{model}]: {reply}")

        # Aktualizacja pełnej historii (Opcja A)
        history.append({"role": "user", "content": content})
        history.append({"role": "assistant", "content": reply})
        self._save_history(history)

    # -----------------------------
    #  /chat – STUB (żeby nie wywalało)
    # -----------------------------
    def chat(self, model: str | None = None):
        """
        Stub: /chat nie jest jeszcze pełnym trybem czatu.
        Używaj prefiksu '@' – ma trwałą pamięć między sesjami.
        """
        print("[chat] Tryb /chat nie jest jeszcze zaimplementowany.")
        print("       Użyj prefiksu '@' do zadawania pytań (z pamięcią historii).")
