import pytest
from logic_syntax import Var, Not, And, Or, Implies, Iff, ForAll, Exists, Function
from structure import Literal, Clause
from clausal_form import _eliminate_iff_imp, _eliminate_iff, _eliminate_imp, _push_not_inward, _standardize_vars, _skolemize, _to_prenex, _drop_universals, _distribute_or_over_and, _extract_clauses, clausal_form_converter

UNIVERSAL = "u"
EXISTENTIAL = "e"
CONSTANT = "c"


#Eliminate iff tests
def test_eliminate_iff_simple():
    A = Literal("A", ())
    B = Literal("B", ())
    f = Iff(A, B)
    result = _eliminate_iff(f)

    assert isinstance(result, And)
    assert isinstance(result.left, Implies)
    assert result.left.provided == A
    assert result.left.then == B

    assert isinstance(result.right, Implies)
    assert result.right.provided == B
    assert result.right.then == A

def test_eliminate_iff_nested():
    A = Literal("A", ())
    B = Literal("B", ())
    C = Literal("C", ())
    inner = Iff(A, B)
    outer = Iff(inner, C)
    result = _eliminate_iff(outer)

    assert isinstance(result, And)
    assert isinstance(result.left, Implies)
    assert isinstance(result.right, Implies)
    assert isinstance(result.left.provided, And)

def test_eliminate_iff_in_or():
    A = Literal("A", ())
    B = Literal("B", ())
    C = Literal("C", ())
    f = Or(Iff(A, B), C)
    result = _eliminate_iff(f)

    assert isinstance(result, Or)
    assert isinstance(result.left, And)
    assert isinstance(result.left.left, Implies)
    assert isinstance(result.left.right, Implies)
    assert result.right == C

def test_eliminate_iff_passthrough():
    A = Literal("A", ())
    B = Literal("B", ())
    f = And(A, B)
    result = _eliminate_iff(f)

    assert result == f

#Eliminate imp tests
def test_eliminate_imp_simple():
    A = Literal("A", ())
    B = Literal("B", ())
    f = Implies(A, B)
    result = _eliminate_imp(f)

    assert isinstance(result, Or)
    assert isinstance(result.left, Not)
    assert result.left.sub == A
    assert result.right == B

def test_eliminate_imp_in_and():
    A = Literal("A", ())
    B = Literal("B", ())
    C = Literal("C", ())
    f = And(Implies(A, B), C)
    result = _eliminate_imp(f)

    assert isinstance(result, And)
    left = result.left
    assert isinstance(left, Or)
    assert isinstance(left.left, Not)
    assert left.left.sub == A
    assert left.right == B
    assert result.right == C

def test_eliminate_imp_passthrough():
    A = Literal("A", ())
    B = Literal("B", ())
    f = Or(A, B)
    result = _eliminate_imp(f)
    assert result == f

#Not Tests

def test_push_not_double_negation():
    A = Literal("A", ())
    f = Not(Not(A))
    result = _push_not_inward(f)
    assert result == A

def test_push_not_on_and():
    A = Literal("A", ())
    B = Literal("B", ())
    f = Not(And(A, B))
    result = _push_not_inward(f)

    assert isinstance(result, Or)
    assert result.left == A.negate()
    assert result.right == B.negate()

def test_push_not_on_or():
    A = Literal("A", ())
    B = Literal("B", ())
    f = Not(Or(A, B))
    result = _push_not_inward(f)

    assert isinstance(result, And)
    assert result.left == A.negate()
    assert result.right == B.negate()

from logic_syntax import ForAll, Exists, Var

def test_push_not_on_forall():
    x = Var("x", "u")
    A = Literal("A", (x,))
    f = Not(ForAll(x, A))
    result = _push_not_inward(f)

    assert isinstance(result, Exists)
    assert result.var == x
    assert isinstance(result.sub, Literal)
    assert result.sub == A.negate()

def test_push_not_on_exists():
    x = Var("x", "e")
    A = Literal("A", (x,))
    f = Not(Exists(x, A))
    result = _push_not_inward(f)

    assert isinstance(result, ForAll)
    assert result.var == x
    assert isinstance(result.sub, Literal)
    assert result.sub == A.negate()

def test_push_not_literal_remains():
    A = Literal("A", ())
    f = Not(A)
    result = _push_not_inward(f)
    assert result == A.negate()

# Standardize Vars Test

def test_standardize_single_quantifier():
    x = Var("x", "u")
    f = ForAll(x, Literal("P", (x,)))
    result = _standardize_vars(f)

    assert isinstance(result, ForAll)
    assert result.var.name.startswith("x_")
    assert result.sub == Literal("P", (result.var,))

def test_standardize_nested_same_name():
    x_outer = Var("x", "u")
    x_inner = Var("x", "e")
    inner = Exists(x_inner, And(Literal("P", (x_outer,)), Literal("Q", (x_inner,))))
    f = ForAll(x_outer, inner)

    result = _standardize_vars(f)

    assert isinstance(result, ForAll)
    assert isinstance(result.sub, Exists)
    assert result.var.name != result.sub.var.name

    assert result.sub.sub.left == Literal("P", (result.var,))
    assert result.sub.sub.right == Literal("Q", (result.sub.var,))

def test_standardize_different_names():
    x = Var("x", "u")
    y = Var("y", "e")
    f = ForAll(x, Exists(y, Literal("R", (x, y))))
    result = _standardize_vars(f)

    forall_var = result.var
    exists_var = result.sub.var
    assert forall_var.name != exists_var.name
    assert result.sub.sub == Literal("R", (forall_var, exists_var))

def test_standardize_shadowing_is_local():
    x = Var("x", "u")
    inner = Exists(x, Or(Literal("A", (x,)), Literal("B", (x,))))
    f = ForAll(x, inner)
    result = _standardize_vars(f)

    outer = result.var
    inner = result.sub.var
    assert outer != inner
    assert result.sub.sub.left == Literal("A", (inner,))
    assert result.sub.sub.right == Literal("B", (inner,))

# Skolemize Test

def test_skolemize_constant():
    y = Var("y", "e")
    f = Exists(y, Literal("P", (y,)))

    transformed = _skolemize(_standardize_vars(_push_not_inward(_eliminate_iff_imp(f))))
    assert isinstance(transformed, Literal)
    arg = transformed.args[0]
    assert isinstance(arg, Var)
    assert arg.name.startswith("csk_")

def test_skolemize_function_single_universal():
    x = Var("x", "u")
    y = Var("y", "e")
    f = ForAll(x, Exists(y, Literal("P", (x, y))))

    transformed = _skolemize(_standardize_vars(_push_not_inward(_eliminate_iff_imp(f))))
    assert isinstance(transformed, ForAll)
    assert isinstance(transformed.sub, Literal)
    
    x_var = transformed.var
    y_arg = transformed.sub.args[1]
    assert isinstance(y_arg, Function)
    assert x_var in y_arg.args

def test_skolemize_function_multi_universal():
    x = Var("x", "u")
    z = Var("z", "u")
    y = Var("y", "e")
    f = ForAll(x, ForAll(z, Exists(y, Literal("R", (x, y, z)))))

    transformed = _skolemize(_standardize_vars(_push_not_inward(_eliminate_iff_imp(f))))
    assert isinstance(transformed, ForAll)
    assert isinstance(transformed.sub, ForAll)
    assert isinstance(transformed.sub.sub, Literal)

    func = transformed.sub.sub.args[1]
    assert isinstance(func, Function)
    arg_names = {v.name for v in func.args}
    assert transformed.var.name in arg_names
    assert transformed.sub.var.name in arg_names

def test_skolemize_mixed_scope_and():
    x = Var("x", "u")
    y = Var("y", "e")
    z = Var("z", "e")
    
    left = ForAll(x, Exists(y, Literal("P", (x, y))))
    right = Exists(z, Literal("Q", (z,)))
    f = And(left, right)

    transformed = _skolemize(_standardize_vars(_push_not_inward(_eliminate_iff_imp(f))))
    assert isinstance(transformed, And)
    left_lit = transformed.left.sub
    right_lit = transformed.right

    assert isinstance(left_lit.args[1], Function)
    assert isinstance(right_lit.args[0], Var)
    assert right_lit.args[0].name.startswith("csk_")

def test_skolemize_disjunction_scoped():
    x = Var("x", "u")
    y = Var("y", "e")

    left = ForAll(x, Literal("P", (x,)))
    right = Exists(y, Literal("Q", (y,)))
    f = Or(left, right)

    transformed = _skolemize(_standardize_vars(_push_not_inward(_eliminate_iff_imp(f))))
    assert isinstance(transformed, Or)
    assert isinstance(transformed.left, ForAll)
    assert isinstance(transformed.left.sub, Literal)
    assert isinstance(transformed.right, Literal)
    assert isinstance(transformed.right.args[0], Var)
    assert transformed.right.args[0].name.startswith("csk_")

# Prenix Tests

def test_prenex_flat_and():
    x = Var("x", "u")
    y = Var("y", "u")
    f = And(ForAll(x, Literal("P", (x,))), ForAll(y, Literal("Q", (y,))))
    result = _to_prenex(f)

    assert isinstance(result, ForAll)
    assert isinstance(result.sub, ForAll)
    assert isinstance(result.sub.sub, And)

def test_prenex_flat_or():
    x = Var("x", "u")
    y = Var("y", "u")
    f = Or(ForAll(x, Literal("A", (x,))), ForAll(y, Literal("B", (y,))))
    result = _to_prenex(f)

    assert isinstance(result, ForAll)
    assert isinstance(result.sub, ForAll)
    assert isinstance(result.sub.sub, Or)

def test_prenex_nested_forall():
    x = Var("x", "u")
    y = Var("y", "u")
    f = ForAll(x, ForAll(y, Literal("R", (x, y))))
    result = _to_prenex(f)

    assert isinstance(result, ForAll)
    assert isinstance(result.sub, ForAll)
    assert isinstance(result.sub.sub, Literal)

def test_prenex_mixed_branches():
    x = Var("x", "u")
    y = Var("y", "u")
    left = Literal("L", (x,))
    right = ForAll(y, Literal("R", (y,)))
    f = And(left, right)
    result = _to_prenex(f)

    assert isinstance(result, ForAll)
    assert isinstance(result.sub, And)

def test_prenex_no_quantifiers():
    a = Literal("A", ())
    b = Literal("B", ())
    f = And(a, b)
    result = _to_prenex(f)

    assert result == f

# Drop Universal tests

def test_drop_single_forall():
    x = Var("x", UNIVERSAL)
    f = ForAll(x, Literal("P", (x,)))
    result = _drop_universals(f)
    assert isinstance(result, Literal)
    assert result.name == "P"

def test_drop_multiple_foralls():
    x = Var("x", UNIVERSAL)
    y = Var("y", UNIVERSAL)
    inner = Literal("Q", (x, y))
    f = ForAll(x, ForAll(y, inner))
    result = _drop_universals(f)
    assert isinstance(result, Literal)
    assert result.name == "Q"
    assert result.args == (x, y)

def test_no_forall_to_drop():
    x = Var("x", UNIVERSAL)
    y = Var("y", UNIVERSAL)
    f = Or(Literal("P", (x,)), Literal("Q", (y,)))
    result = _drop_universals(f)
    assert isinstance(result, Or)
    assert result.left.name == "P"
    assert result.right.name == "Q"

# Distribute Or over And test

def test_or_distributes_over_and_right():
    x = Var("x", UNIVERSAL)
    y = Var("y", UNIVERSAL)
    z = Var("z", UNIVERSAL)

    P = Literal("P", (x,))
    Q = Literal("Q", (y,))
    R = Literal("R", (z,))

    f = Or(P, And(Q, R))
    result = _distribute_or_over_and(f)

    assert isinstance(result, And)
    assert isinstance(result.left, Or)
    assert isinstance(result.right, Or)
    assert result.left.left == P
    assert result.left.right == Q
    assert result.right.left == P
    assert result.right.right == R

def test_or_distributes_over_and_left():
    x = Var("x", UNIVERSAL)
    y = Var("y", UNIVERSAL)
    z = Var("z", UNIVERSAL)

    P = Literal("P", (x,))
    Q = Literal("Q", (y,))
    R = Literal("R", (z,))

    f = Or(And(Q, R), P)
    result = _distribute_or_over_and(f)

    assert isinstance(result, And)
    assert isinstance(result.left, Or)
    assert isinstance(result.right, Or)
    assert result.left.left == Q
    assert result.left.right == P
    assert result.right.left == R
    assert result.right.right == P

def test_nested_distribution():
    x = Var("x", UNIVERSAL)
    y = Var("y", UNIVERSAL)
    z = Var("z", UNIVERSAL)
    w = Var("w", UNIVERSAL)

    P = Literal("P", (x,))
    Q = Literal("Q", (y,))
    R = Literal("R", (z,))
    S = Literal("S", (w,))

    inner = Or(P, And(Q, R))
    f = Or(inner, S)
    result = _distribute_or_over_and(f)

    assert isinstance(result, And)
    assert isinstance(result.left, Or)
    assert isinstance(result.right, Or)

# Extract Clauses Tests

def test_extract_clauses_from_simple_and():
    x = Var("x", UNIVERSAL)
    y = Var("y", UNIVERSAL)
    P = Literal("P", (x,))
    Q = Literal("Q", (y,))

    f = And(P, Q)
    clauses = _extract_clauses(f)

    assert len(clauses) == 2
    assert Clause({P}) in clauses
    assert Clause({Q}) in clauses

def test_extract_clauses_from_or():
    x = Var("x", UNIVERSAL)
    y = Var("y", UNIVERSAL)
    P = Literal("P", (x,))
    Q = Literal("Q", (y,))

    f = Or(P, Q)
    clauses = _extract_clauses(f)

    assert len(clauses) == 1
    assert Clause({P, Q}) == clauses[0]

def test_extract_clauses_from_nested_and_or():
    x = Var("x", UNIVERSAL)
    y = Var("y", UNIVERSAL)
    z = Var("z", UNIVERSAL)
    P = Literal("P", (x,))
    Q = Literal("Q", (y,))
    R = Literal("R", (z,))

    f = And(Or(P, Q), Or(Q, R))
    clauses = _extract_clauses(f)

    assert len(clauses) == 2
    assert Clause({P, Q}) in clauses
    assert Clause({Q, R}) in clauses

def test_extract_clauses_with_negation():
    x = Var("x", UNIVERSAL)
    y = Var("y", UNIVERSAL)
    P = Literal("P", (x,))
    Q = Literal("Q", (y,))

    f = And(Or(P, Not(Q)), Q)
    clauses = _extract_clauses(f)

    assert len(clauses) == 2
    assert Clause({P, Not(Q)}) in clauses
    assert Clause({Q}) in clauses

# Other Tests

def test_full_pipeline_basic():
    x = Var("x", UNIVERSAL)
    y = Var("y", EXISTENTIAL)

    formula = ForAll(x, Implies(Literal("P", (x,)), Exists(y, Literal("Q", (x, y)))))
    clauses = clausal_form_converter(formula)

    assert isinstance(clauses, list)
    assert all(isinstance(c, Clause) for c in clauses)
    assert any(any(lit.name == "Q" for lit in clause.literals) for clause in clauses)


def test_skolem_naming_conventions():
    x = Var("x", UNIVERSAL)
    y = Var("y", EXISTENTIAL)

    formula = ForAll(x, Exists(y, Literal("Q", (x, y))))
    skolemized = _skolemize(_standardize_vars(_push_not_inward(_eliminate_iff_imp(formula))))
    arg = skolemized.sub.args[1]

    if isinstance(arg, Var):
        assert arg.name.startswith("csk_")
    elif isinstance(arg, Function):
        assert arg.name.startswith("fsk_")
    else:
        assert False, "Unexpected Skolem term type"


def test_deep_quantifier_nesting():
    x = Var("x", UNIVERSAL)
    y = Var("y", EXISTENTIAL)
    z = Var("z", UNIVERSAL)

    inner = ForAll(z, Literal("R", (x, y, z)))
    exists = Exists(y, And(Literal("Q", (y,)), inner))
    formula = ForAll(x, exists)

    clauses = clausal_form_converter(formula)

    assert all(isinstance(c, Clause) for c in clauses)
    clause_str = "\n".join(str(c) for c in clauses)
    assert "R" in clause_str
    assert "Q" in clause_str


def test_literal_negation_equivalence():
    x = Var("x", UNIVERSAL)
    lit1 = Not(Literal("P", (x,)))
    lit1 = _push_not_inward(lit1)
    lit2 = Literal("P", (x,), positive=False)

    assert lit1 == lit2
    assert hash(lit1) == hash(lit2)


def test_clause_with_duplicate_literals():
    x = Var("x", UNIVERSAL)
    lit = Literal("P", (x,))
    f = Or(lit, lit)

    clauses = _extract_clauses(f)
    assert len(clauses) == 1
    assert Clause({lit}) in clauses