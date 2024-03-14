from dataclasses import dataclass

@dataclass
class Add:
    inputs: list[str]
    output: str

    def __str__(self) -> str:
        return "add at lower"
        


