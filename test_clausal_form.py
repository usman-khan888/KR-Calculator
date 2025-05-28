import pytest
from logic_syntax import Var, Not, And, Or, Implies, Iff, ForAll, Exists, Function
from structure import Literal
from clausal_form import _eliminate_iff_imp, _eliminate_iff, _eliminate_imp, _push_not_inward, _standardize_vars, _skolemize, _to_prenex

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
    assert result.left == Not(A)
    assert result.right == Not(B)

def test_push_not_on_or():
    A = Literal("A", ())
    B = Literal("B", ())
    f = Not(Or(A, B))
    result = _push_not_inward(f)

    assert isinstance(result, And)
    assert result.left == Not(A)
    assert result.right == Not(B)

from logic_syntax import ForAll, Exists, Var

def test_push_not_on_forall():
    x = Var("x", "u")
    A = Literal("A", (x,))
    f = Not(ForAll(x, A))
    result = _push_not_inward(f)

    assert isinstance(result, Exists)
    assert result.var == x
    assert isinstance(result.sub, Not)
    assert result.sub.sub == A

def test_push_not_on_exists():
    x = Var("x", "e")
    A = Literal("A", (x,))
    f = Not(Exists(x, A))
    result = _push_not_inward(f)

    assert isinstance(result, ForAll)
    assert result.var == x
    assert isinstance(result.sub, Not)
    assert result.sub.sub == A

def test_push_not_literal_remains():
    A = Literal("A", ())
    f = Not(A)
    result = _push_not_inward(f)
    assert result == f

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
