from __future__ import annotations
from dataclasses import dataclass
from typing import Union



    
@dataclass(frozen=True)
class Var:
    name: str

@dataclass(frozen=True)
class Not:
    sub: Formula

@dataclass(frozen=True)
class And:
    left: Formula
    right: Formula

@dataclass(frozen=True)
class Or:
    left: Formula
    right: Formula

@dataclass(frozen=True)
class Implies:
    provided: Formula
    then: Formula

@dataclass(frozen=True)
class Iff:
    left: Formula
    right: Formula

@dataclass(frozen=True)
class ForAll:
    var: str
    sub: Formula

@dataclass(frozen=True)
class Exists:
    var: str
    sub: Formula

Formula = Union[
    Var, Not, And, Or, Implies, Iff,
    ForAll, Exists
]