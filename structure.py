from dataclasses import dataclass
from typing import Tuple, FrozenSet, Dict, List, Any, Set

@dataclass(frozen=True)
class Literal:
    name: str
    args: Tuple[Any, ...]
    positive: bool = True

    def negate(self) -> "Literal":
        return Literal(self.name, self.args, not self.positive)
    
    def __str__(self) -> str:
        prefix = "" if self.positive else "¬"
        joined = ", ".join(map(str, self.args))
        return f"{prefix}{self.name}({joined})"
        
    

@dataclass(frozen=True)
class Clause:
    literals: FrozenSet[Literal]

    def __str__(self) -> str:
        return " ∨ ".join(map(str, self.literals))

class KB:
    def __init__(self, clauses: list[Clause] | None = None):
        self.clauses: list[Clause] = []
        self._clause_set: Set[Clause] = set()
        self.index: dict[Literal, list[Clause]] = {}
        if clauses:
            for c in clauses:
                self.add_clause(c)

    def add_clause(self, clause: Clause) -> None:
            if clause in self._clause_set:
                print("already exists")
            else:
                self._clause_set.add(clause)
                self.clauses.append(clause)
                for lit in clause.literals:
                    self.index.setdefault(lit, []).append(clause)


    