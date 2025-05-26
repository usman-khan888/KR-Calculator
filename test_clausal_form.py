import pytest
from logic_syntax import Var, Not, And, Or, Implies, Iff, ForAll, Exists
from structure import Literal
from clausal_form import _eliminate_iff, _eliminate_imp, _push_not_inward, _standardize_vars, _to_prenex

# Use Literal instead of Var for formula-level atoms
P = Literal("P", ())
Q = Literal("Q", ())
R = Literal("R", ())

# --- Tests for _eliminate_iff ---

def test_eliminate_iff_simple():
    f = Iff(P, Q)
    out = _eliminate_iff(f)
    assert isinstance(out, And)
    assert isinstance(out.left, Implies)
    assert out.left.provided == P and out.left.then == Q
    assert isinstance(out.right, Implies)
    assert out.right.provided == Q and out.right.then == P

def test_eliminate_iff_nested_in_or():
    f = Or(Iff(P, Q), R)
    out = _eliminate_iff(f)
    assert isinstance(out, Or)
    assert isinstance(out.left, And)
    assert isinstance(out.left.left, Implies)
    assert isinstance(out.left.right, Implies)
    assert out.right == R

def test_eliminate_iff_pass_through():
    f = And(P, Q)
    out = _eliminate_iff(f)
    assert out == f

def test_eliminate_imp_basic():
    f = Implies(P, Q)
    out = _eliminate_imp(f)
    assert isinstance(out, Or)
    assert isinstance(out.left, Not) and out.left.sub == P
    assert out.right == Q

def test_eliminate_imp_inside_and():
    f = And(Implies(P, Q), R)
    out = _eliminate_imp(f)
    assert isinstance(out, And)
    assert isinstance(out.left, Or)
    assert out.left.left == Not(P)
    assert out.left.right == Q
    assert out.right == R

def test_eliminate_imp_no_change():
    f = Or(P, Q)
    out = _eliminate_imp(f)
    assert out == f

def test_push_not_double_negation():
    f = Not(Not(P))
    out = _push_not_inward(f)
    assert out == P

def test_push_not_on_and():
    f = Not(And(P, Q))
    out = _push_not_inward(f)
    assert isinstance(out, Or)
    assert out.left == Not(P)
    assert out.right == Not(Q)

def test_push_not_on_or():
    f = Not(Or(P, Q))
    out = _push_not_inward(f)
    assert isinstance(out, And)
    assert out.left == Not(P)
    assert out.right == Not(Q)

def test_push_not_on_quantifiers():
    f1 = Not(ForAll("x", P))
    f2 = Not(Exists("y", Q))
    out1 = _push_not_inward(f1)
    out2 = _push_not_inward(f2)
    assert isinstance(out1, Exists)
    assert out1.var == "x" and isinstance(out1.sub, Not)
    assert out1.sub.sub == P
    assert isinstance(out2, ForAll)
    assert out2.var == "y" and isinstance(out2.sub, Not)
    assert out2.sub.sub == Q

def test_push_not_literals_are_preserved():
    f = Not(P)
    out = _push_not_inward(f)
    assert out == f

def test_single_quantifier():
    f = ForAll("x", Literal("L", (Var("x"),)))
    out = _standardize_vars(f)
    assert isinstance(out, ForAll)
    assert out.var.startswith("x_")
    assert out.sub == Literal("L", (Var(out.var),))

def test_nested_quantifiers_same_name():
    inner = Exists("x", And(Literal("L", (Var("x"),)), Literal("L", (Var("x"),))))
    f = ForAll("x", inner)
    out = _standardize_vars(f)
    assert isinstance(out, ForAll)
    assert isinstance(out.sub, Exists)
    assert out.var != out.sub.var
    assert out.sub.sub.left == Literal("L", (Var(out.sub.var),))
    assert out.sub.sub.right == Literal("L", (Var(out.sub.var),))

def test_quantifiers_different_names():
    inner = Exists("y", And(Literal("L", (Var("x"),)), Literal("L", (Var("y"),))))
    f = ForAll("x", inner)
    out = _standardize_vars(f)
    forall_var = out.var
    exists_var = out.sub.var
    assert out.sub.sub.left == Literal("L", (Var(forall_var),))
    assert out.sub.sub.right == Literal("L", (Var(exists_var),))

def test_shadowing_is_local():
    inner = Exists("x", Or(Literal("A", (Var("x"),)), Literal("B", (Var("x"),))))
    f = ForAll("x", And(Literal("P", (Var("x"),)), inner))
    out = _standardize_vars(f)
    outer_var = out.var
    inner_var = out.sub.right.var
    assert outer_var != inner_var
    assert out.sub.left == Literal("P", (Var(outer_var),))
    assert out.sub.right.sub.left == Literal("A", (Var(inner_var),))
    assert out.sub.right.sub.right == Literal("B", (Var(inner_var),))

def test_prenex_flat():
    f = ForAll("x", Exists("y", And(P, Q)))
    out = _to_prenex(f)
    assert isinstance(out, ForAll)
    assert isinstance(out.sub, Exists)
    assert isinstance(out.sub.sub, And)

def test_prenex_nested():
    inner = Exists("y", Q)
    mid = ForAll("x", And(P, inner))
    f = Exists("z", mid)
    out = _to_prenex(f)
    assert isinstance(out, Exists)
    assert isinstance(out.sub, ForAll)
    assert isinstance(out.sub.sub, Exists)

def test_prenex_or():
    inner = Exists("y", Q)
    f = ForAll("x", Or(P, inner))
    out = _to_prenex(f)
    assert isinstance(out, ForAll)
    assert isinstance(out.sub, Exists)
    assert isinstance(out.sub.sub, Or)

def test_prenex_no_quantifiers():
    f = And(P, Q)
    out = _to_prenex(f)
    assert out == f

def test_prenex_mixed_branches():
    left = P
    right = ForAll("y", Q)
    f = Exists("x", And(left, right))
    out = _to_prenex(f)
    assert isinstance(out, Exists)
    assert isinstance(out.sub, ForAll)
    assert isinstance(out.sub.sub, And)
