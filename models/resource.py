from dataclasses import dataclass, field

@dataclass
class Resource:
    current: int
    maximum: int
    minimum: int | None = None

    def lose(self, amount: int) -> None:
        self.current = max(0, self.current - amount)

    def restore(self, amount: int) -> None:
        self.current = min(self.maximum, self.current + amount)