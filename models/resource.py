from dataclasses import dataclass, field

@dataclass
class Resource:
    initial: int
    current: initial
    maximum: int | None = None
    minimum: int | None = None

    def reset(self):
        self.current = self.initial

    def lose(self, amount: int) -> None:
        if self.minimum is None:
            self.current = self.current - amount
        else:
            self.current = min(self.maximum, self.current + amount)

    def restore(self, amount: int) -> None:
        if self.maximum is None:
            self.current = self.current + amount
        else:
            self.current = min(self.maximum, self.current + amount)