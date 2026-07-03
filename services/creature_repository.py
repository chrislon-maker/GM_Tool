import json
from app.models.enemy import Enemy

def load_enemies(path: str) -> list[Enemy]:
    with open(path, encoding="utf-8") as file:
        raw = json.load(file)
    return [Enemy(**entry) for entry in raw]

def save_enemies(path: str, enemies: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(enemies, file, indent=2, ensure_ascii=False)