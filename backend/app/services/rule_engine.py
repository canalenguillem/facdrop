"""Motor de reglas (spec §11).

Lógica PURA de coincidencia: dado un correo (dict) y las reglas del usuario,
devuelve la primera regla que coincide por prioridad. No toca BD ni servicios
externos, por eso es único y testeable. En la Fase 6 el servicio de procesado
lo usará para enrutar los adjuntos a Dropbox.

El `email` es un dict con al menos:
  { "label_id": str, "from": str, "subject": str, "has_attachments": bool }
"""


class RuleEngine:
    def find_matching_rule(self, email: dict, rules: list):
        """Primera regla activa que coincide (menor priority = antes), o None."""
        for rule in sorted(rules, key=lambda r: r.priority):
            if not rule.is_active:
                continue
            if self._matches(email, rule):
                return rule
        return None

    def _matches(self, email: dict, rule) -> bool:
        # 1. La etiqueta de origen debe coincidir.
        if email.get("label_id") != rule.source_label.gmail_label_id:
            return False
        # 2. Remitente (si la regla lo define).
        if rule.from_email and rule.from_email.lower() not in email.get("from", "").lower():
            return False
        # 3. El asunto contiene (si la regla lo define).
        if (
            rule.subject_contains
            and rule.subject_contains.lower() not in email.get("subject", "").lower()
        ):
            return False
        # 4. Requiere adjunto.
        if rule.has_attachment and not email.get("has_attachments", False):
            return False
        return True
