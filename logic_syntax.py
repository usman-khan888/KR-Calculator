from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Union, Any, Optional
from structure import Literal
    
@dataclass(frozen=True)
class Var:
    name: str
    type: str
    domain: str = None
    def __str__(self):
        return f"{self.name}"

@dataclass(frozen=True)
class Function:
    name: str
    args: Tuple[Var, ...]
    range: str = None

    def __str__(self):
        return f"{self.name}({', '.join(map(str, self.args))})"

@dataclass(frozen=True)
class Not:
    sub: Formula
    def __str__(self):
        return f"¬({self.sub})"

@dataclass(frozen=True)
class And:
    left: Formula
    right: Formula
    def __str__(self):
        return f"({self.left} ∧ {self.right})"

@dataclass(frozen=True)
class Or:
    left: Formula
    right: Formula
    def __str__(self):
        return f"({self.left} ∨ {self.right})"

@dataclass(frozen=True)
class Implies:
    provided: Formula
    then: Formula
    def __str__(self):
        return f"{self.provided} → {self.then}"

@dataclass(frozen=True)
class Iff:
    left: Formula
    right: Formula
    def __str__(self):
        return f"{self.left} ↔ {self.right}"

@dataclass(frozen=True)
class ForAll:
    var: Var
    sub: Formula
    domain: str = None
    def __str__(self):
        return f"∀{self.var}.{self.sub}"

@dataclass(frozen=True)
class Exists:
    var: Var
    sub: Formula
    domain: str = None
    def __str__(self):
        return f"∃{self.var.name}.{self.sub}"


Formula = Union[
    Literal, Not, And, Or, Implies, Iff,
    ForAll, Exists
]