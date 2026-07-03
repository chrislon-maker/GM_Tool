from dataclasses import dataclass, field
from typing import Callable


@dataclass
class StatusEffect:
    name: str
    remaining_rounds: int | None = None
    modifiers: dict[str, int] = field(default_factory=dict)

    def tick(self) -> bool:
        if self.remaining_rounds is None:
            return False

        self.remaining_rounds -= 1
        return self.remaining_rounds <= 0