from typing import Optional
from datetime import datetime


class SecurityLogger:
    def log_event(
        self,
        event_type: str,
        text: str,
        label: str,
        reason: str,
        action: str,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Very simple logger for now; later you can plug in proper logging/JSON/DB.

        event_type: "input" or "output"
        action: "allow" | "block" | "sanitize"
        """
        timestamp = datetime.utcnow().isoformat()
        print(
            f"[{timestamp}] [{event_type}] user={user_id} "
            f"label={label} action={action} reason={reason} text={text[:80]!r}"
        )
