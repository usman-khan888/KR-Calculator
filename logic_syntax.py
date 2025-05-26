from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Union, Any
from structure import Literal
    
@dataclass(frozen=True)
class Var:
    name: str
    def __str__(self):
        return f"{self.name}"


@dataclass(frozen=True)
class Const:
    name: str
    value: Any = None

@dataclass(frozen=True)
class Func:
    name: str
    args: Tuple[Term, ...]

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
        return f"({self.provided} → {self.then})"

@dataclass(frozen=True)
class Iff:
    left: Formula
    right: Formula
    def __str__(self):
        return f"({self.left} ↔ {self.right})"

@dataclass(frozen=True)
class ForAll:
    var: str
    sub: Formula
    def __str__(self):
        return f"∀{self.var}.({self.sub})"

@dataclass(frozen=True)
class Exists:
    var: str
    sub: Formula
    def __str__(self):
        return f"∃{self.var}.({self.sub})"


Term = Union[Var, Const, Func]

Formula = Union[
    Literal, Not, And, Or, Implies, Iff,
    ForAll, Exists
]