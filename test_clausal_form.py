import pytest
from logic_syntax import Var, Not, And, Or, Implies, Iff, ForAll, Exists
from clausal_form import _eliminate_iff, _eliminate_imp, _push_not_inward, _standardize_vars, _to_prenex

# Aliases for brevity
P = Var("P")
Q = Var("Q")
R = Var("R")

# --- Tests for _eliminate_iff ---

def test_eliminate_iff_simple():
    f = Iff(Var("P"), Var("Q"))
    out = _eliminate_iff(f)
    assert isinstance(out, And)
    assert isinstance(out.left, Implies)
    assert out.left.provided == Var("P") and out.left.then == Var("Q")
    assert isinstance(out.right, Implies)
    assert out.right.provided == Var("Q") and out.right.then == Var("P")

def test_eliminate_iff_nested_in_or():
    f = Or(Iff(Var("P"), Var("Q")), Var("R"))
    out = _eliminate_iff(f)
    assert isinstance(out, Or)
    assert isinstance(out.left, And)
    assert isinstance(out.left.left, Implies)
    assert isinstance(out.left.right, Implies)
    assert out.right == Var("R")

def test_eliminate_iff_pass_through():
    f = And(Var("P"), Var("Q"))
    out = _eliminate_iff(f)
    assert out == f

def test_eliminate_imp_basic():
    f = Implies(Var("P"), Var("Q"))
    out = _eliminate_imp(f)
    assert isinstance(out, Or)
    assert isinstance(out.left, Not) and out.left.sub == Var("P")
    assert out.right == Var("Q")

def test_eliminate_imp_inside_and():
    f = And(Implies(Var("P"), Var("Q")), Var("R"))
    out = _eliminate_imp(f)
    assert isinstance(out, And)
    assert isinstance(out.left, Or)
    assert out.left.left == Not(Var("P"))
    assert out.left.right == Var("Q")
    assert out.right == Var("R")

def test_eliminate_imp_no_change():
    f = Or(Var("P"), Var("Q"))
    out = _eliminate_imp(f)
    assert out == f

def test_push_not_double_negation():
    f = Not(Not(Var("P")))
    out = _push_not_inward(f)
    assert out == Var("P")

def test_push_not_on_and():
    f = Not(And(Var("P"), Var("Q")))
    out = _push_not_inward(f)
    assert isinstance(out, Or)
    assert out.left == Not(Var("P"))
    assert out.right == Not(Var("Q"))

def test_push_not_on_or():
    f = Not(Or(Var("P"), Var("Q")))
    out = _push_not_inward(f)
    assert isinstance(out, And)
    assert out.left == Not(Var("P"))
    assert out.right == Not(Var("Q"))

def test_push_not_on_quantifiers():
    f1 = Not(ForAll("x", Var("P")))
    f2 = Not(Exists("y", Var("Q")))
    out1 = _push_not_inward(f1)
    out2 = _push_not_inward(f2)
    assert isinstance(out1, Exists)
    assert out1.var == "x" and isinstance(out1.sub, Not)
    assert out1.sub.sub == Var("P")
    assert isinstance(out2, ForAll)
    assert out2.var == "y" and isinstance(out2.sub, Not)
    assert out2.sub.sub == Var("Q")

def test_push_not_liters_are_preserved():
    # ¬P should stay ¬P
    f = Not(Var("P"))
    out = _push_not_inward(f)
    assert out == f

def test_single_quantifier():
    f = ForAll("x", Var("x"))
    out = _standardize_vars(f)
    assert isinstance(out, ForAll)
    assert out.var.startswith("x_")
    assert out.sub == Var(out.var)

def test_nested_quantifiers_same_name():
    inner = Exists("x", And(Var("x"), Var("x")))
    f = ForAll("x", inner)
    out = _standardize_vars(f)

    assert isinstance(out, ForAll)
    assert isinstance(out.sub, Exists)
    assert out.var != out.sub.var
    assert out.sub.sub.left == Var(out.sub.var)
    assert out.sub.sub.right == Var(out.sub.var)

def test_quantifiers_different_names():
    inner = Exists("y", And(Var("x"), Var("y")))
    f = ForAll("x", inner)
    out = _standardize_vars(f)

    forall_var = out.var
    exists_var = out.sub.var
    assert out.sub.sub.left == Var(forall_var)
    assert out.sub.sub.right == Var(exists_var)

def test_shadowing_is_local():
    inner = Exists("x", Or(Var("x"), Var("x")))
    f = ForAll("x", And(Var("x"), inner))
    out = _standardize_vars(f)

    outer_var = out.var
    inner_var = out.sub.right.var
    assert outer_var != inner_var
    assert out.sub.left == Var(outer_var)
    assert out.sub.right.sub.left == Var(inner_var)
    assert out.sub.right.sub.right == Var(inner_var)

def test_prenex_flat():
    # ∀x. ∃y. (P ∧ Q) — already in prenex
    f = ForAll("x", Exists("y", And(Var("P"), Var("Q"))))
    out = _to_prenex(f)
    assert isinstance(out, ForAll)
    assert isinstance(out.sub, Exists)
    assert isinstance(out.sub.sub, And)

def test_prenex_nested():
    # ∃z. (∀x. (P ∧ ∃y. Q)) → ∃z. ∀x. ∃y. (P ∧ Q)
    inner = Exists("y", Var("Q"))
    mid = ForAll("x", And(Var("P"), inner))
    f = Exists("z", mid)
    out = _to_prenex(f)
    assert isinstance(out, Exists)
    assert isinstance(out.sub, ForAll)
    assert isinstance(out.sub.sub, Exists)

def test_prenex_or():
    # ∀x. (P ∨ ∃y. Q) → ∀x. ∃y. (P ∨ Q)
    inner = Exists("y", Var("Q"))
    f = ForAll("x", Or(Var("P"), inner))
    out = _to_prenex(f)
    assert isinstance(out, ForAll)
    assert isinstance(out.sub, Exists)
    assert isinstance(out.sub.sub, Or)

def test_prenex_no_quantifiers():
    # P ∧ Q — no quantifiers
    f = And(Var("P"), Var("Q"))
    out = _to_prenex(f)
    assert out == f

def test_prenex_mixed_branches():
    # ∃x. (P ∧ ∀y. Q) → ∃x. ∀y. (P ∧ Q)
    left = Var("P")
    right = ForAll("y", Var("Q"))
    f = Exists("x", And(left, right))
    out = _to_prenex(f)
    assert isinstance(out, Exists)
    assert isinstance(out.sub, ForAll)
    assert isinstance(out.sub.sub, And)

