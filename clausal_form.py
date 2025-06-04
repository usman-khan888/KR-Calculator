from logic_syntax import *
from structure import *
from itertools import count


_var_counter = count()

UNIVERSAL = "u"
EXISTENTIAL = "e"
CONSTANT = "c"



def clausal_form_converter(formula: Formula) -> List[Clause]:
    f1 = _eliminate_iff_imp(formula)
    f2 = _push_not_inward(f1)
    f3 = _standardize_vars(f2)
    f4 = _skolemize(f3)
    f5 = _to_prenex(f4)
    f6 = _drop_universals(f5)
    f7 = _distribute_or_over_and(f6)
    return _extract_clauses(f7)

def _eliminate_iff_imp(formula: Formula) -> Formula:
    f = _eliminate_iff(formula)
    return _eliminate_imp(f)

def _eliminate_iff(formula: Formula) -> Formula:
    # A ↔ B  ≡  (A→B) ∧ (B→A)
    if isinstance(formula, Iff):
        left = _eliminate_iff(formula.left)
        right = _eliminate_iff(formula.right)
        return And(Implies(left, right), Implies(right, left))
    
    if isinstance(formula, Implies):
        return Implies(_eliminate_iff(formula.provided), _eliminate_iff(formula.then))
    
    if isinstance(formula, And):
        return And(_eliminate_iff(formula.left), _eliminate_iff(formula.right))
    
    if isinstance(formula, Or):
        return Or(_eliminate_iff(formula.left), _eliminate_iff(formula.right))
    
    if isinstance(formula, Not):
        return Not(_eliminate_iff(formula.sub))
    
    if isinstance(formula, ForAll):
        return ForAll(formula.var, _eliminate_iff(formula.sub))
    
    if isinstance(formula, Exists):
        return Exists(formula.var, _eliminate_iff(formula.sub))
    
    return formula


def _eliminate_imp(formula: Formula) -> Formula:
    # A→B  ≡  ¬A ∨ B
    if isinstance(formula, Implies):
        return Or(Not(_eliminate_imp(formula.provided)), _eliminate_imp(formula.then))
    
    if isinstance(formula, And):
        return And(_eliminate_imp(formula.left), _eliminate_imp(formula.right))
    
    if isinstance(formula, Or):
        return Or(_eliminate_imp(formula.left), _eliminate_imp(formula.right))
    
    if isinstance(formula, Not):
        return Not(_eliminate_imp(formula.sub))
    
    if isinstance(formula, ForAll):
        return ForAll(formula.var, _eliminate_imp(formula.sub))
    
    if isinstance(formula, Exists):
        return Exists(formula.var, _eliminate_imp(formula.sub))
    
    return formula

def _push_not_inward(f: Formula) -> Formula:
    if isinstance(f, Not):
        sub = f.sub

        if isinstance(sub, Not):
            return _push_not_inward(sub.sub)  # ¬¬A ≡ A
        
        if isinstance(sub, And):
            # ¬(A∧B) ≡ ¬A ∨ ¬B
            return Or(_push_not_inward(Not(sub.left)), _push_not_inward(Not(sub.right)))
        
        if isinstance(sub, Or):
            # ¬(A∨B) ≡ ¬A ∧ ¬B
            return And(_push_not_inward(Not(sub.left)), _push_not_inward(Not(sub.right)))
        
        if isinstance(sub, ForAll):
            # ¬∀x.A ≡ ∃x.¬A
            return Exists(sub.var, _push_not_inward(Not(sub.sub)))
        
        if isinstance(sub, Exists):
            # ¬∃x.A ≡ ∀x.¬A
            return ForAll(sub.var, _push_not_inward(Not(sub.sub)))
        
        if isinstance(sub, Literal):
            return sub.negate()
        
        return f
    
    if isinstance(f, And):
        return And(_push_not_inward(f.left), _push_not_inward(f.right))
    
    if isinstance(f, Or):
        return Or(_push_not_inward(f.left), _push_not_inward(f.right))
    
    if isinstance(f, ForAll):
        return ForAll(f.var, _push_not_inward(f.sub))
    
    if isinstance(f, Exists):
        return Exists(f.var, _push_not_inward(f.sub))
    
    return f # Literal


def _standardize_vars(formula: Formula) -> Formula:
    return _standardize_helper(formula, {})

def _standardize_helper(f: Formula, env: Dict[Var, Var]) -> Formula:
    if isinstance(f, ForAll) or isinstance(f, Exists):
        old_var = f.var
        new_name = f"{old_var.name}_{next(_var_counter)}"
        new_var = Var(name=new_name, type=old_var.type, domain=old_var.domain)

        new_env = env.copy()
        new_env[old_var] = new_var

        return type(f)(new_var, _standardize_helper(f.sub, new_env))

    elif isinstance(f, Not):
        return Not(_standardize_helper(f.sub, env))

    elif isinstance(f, And):
        return And(_standardize_helper(f.left, env), _standardize_helper(f.right, env))

    elif isinstance(f, Or):
        return Or(_standardize_helper(f.left, env), _standardize_helper(f.right, env))

    elif isinstance(f, Literal):
        new_args = []
        for arg in f.args:
            if isinstance(arg, Var):
                if arg in env:
                    new_args.append(env[arg])
                else:
                    new_args.append(arg)
            elif isinstance(arg, Function):
                standardized_func = _nested_standardize_function(arg, env)
                new_args.append(standardized_func)
            else:
                new_args.append(arg)

        new_args = tuple(new_args)
        return Literal(f.name, new_args, f.positive)
    return f
    
        
def _nested_standardize_function(f: Function, env: Dict[Var, Var]) -> Function:
    new_args = []
    for a in f.args:
        if isinstance(a, Var) and a in env:
            new_args.append(env[a])
        elif isinstance(a, Function):
            new_args.append(_nested_standardize_function(a, env))
        else:
            new_args.append(a)
    return Function(f.name, tuple(new_args), f.range)



def _skolemize(f: Formula) -> Formula:
    return _skolemize_helper(f, [], {})

def _skolemize_helper(f: Formula, uvars: List[Var], env: Dict[str, Any]) -> Formula:
    if isinstance(f, ForAll):
        new_sub = _skolemize_helper(f.sub, uvars + [f.var], env)
        return ForAll(f.var, new_sub)

    elif isinstance(f, Exists):
        name = f"sk_{next(_var_counter)}"
        if uvars:
            sk_term = Function(name="f"+name, args=tuple(uvars), range=f.var.type)
        else:
            sk_term = Var(name="c"+name, type=CONSTANT, domain=f.var.domain)

        new_env = env.copy()
        new_env[f.var.name] = sk_term
        return _skolemize_helper(f.sub, uvars, new_env)

    elif isinstance(f, Not):
        return Not(_skolemize_helper(f.sub, uvars, env))

    elif isinstance(f, And):
        return And(_skolemize_helper(f.left, uvars, env), _skolemize_helper(f.right, uvars, env))

    elif isinstance(f, Or):
        return Or(_skolemize_helper(f.left, uvars, env), _skolemize_helper(f.right, uvars, env))
    
    elif isinstance(f, Literal):
        new_args = []
        for arg in f.args:
            if isinstance(arg, Var):
                if arg.name in env:
                    new_args.append(env[arg.name])
                else:
                    new_args.append(arg)
            elif isinstance(arg, Function):
                skolemized_func = _nested_skolemize_function(arg, uvars, env)
                new_args.append(skolemized_func)
            else:
                new_args.append(arg)
        new_args = tuple(new_args)
        return Literal(f.name, new_args, f.positive)

    return f

def _nested_skolemize_function(f: Function, uvars: List[Var], env: Dict[str, Any]) -> Function:
    new_args = []
    for arg in f.args:
        if isinstance(arg, Var):
            if arg.name in env:
                new_args.append(env[arg.name])
            else:
                new_args.append(arg)
        elif isinstance(arg, Function):
            new_args.append(_nested_skolemize_function(arg, uvars, env))
        else:
            new_args.append(arg)

    return Function(f.name, tuple(new_args), range=f.range)


def _to_prenex(f: Formula) -> Formula:
    quantifiers, body = _pull_quantifiers(f) 
    for q in quantifiers:
        body = ForAll(q.var, body)
    return body

def _pull_quantifiers(f: Formula) -> tuple[list[ForAll], Formula]:
    if isinstance(f, ForAll):
        qs, body = _pull_quantifiers(f.sub)
        qs.append(f)
        return qs, body
    elif isinstance(f, And):
        ql1, f1 = _pull_quantifiers(f.left)
        ql2, f2 = _pull_quantifiers(f.right)
        ql1.extend(ql2)
        return ql1, And(f1, f2)
    elif isinstance(f, Or):
        ql1, f1 = _pull_quantifiers(f.left)
        ql2, f2 = _pull_quantifiers(f.right)
        ql1.extend(ql2)
        return ql1, Or(f1, f2)
    else:
        return [], f

    
def _drop_universals(f: Formula):
    while isinstance(f, ForAll):
        f = f.sub
    return f

def _distribute_or_over_and(f: Formula) -> Formula:
    if isinstance(f, Or):
        # Must run the function over left and right first. It changes there format, then we check if ours matches the distributive format
        left = _distribute_or_over_and(f.left)
        right = _distribute_or_over_and(f.right)

        # A ∨ (B ∧ C) → (A ∨ B) ∧ (A ∨ C)
        if isinstance(right, And):
            return And(
                _distribute_or_over_and(Or(left, right.left)),
                _distribute_or_over_and(Or(left, right.right))
            )

        # (A ∧ B) ∨ C → (A ∨ C) ∧ (B ∨ C)
        if isinstance(left, And):
            return And(
                _distribute_or_over_and(Or(left.left, right)),
                _distribute_or_over_and(Or(left.right, right))
            )
        
        return Or(left, right)

    elif isinstance(f, And):
        return And(_distribute_or_over_and(f.left), _distribute_or_over_and(f.right))

    elif isinstance(f, Not):
        return Not(_distribute_or_over_and(f.sub))
    
    return f

def _extract_clauses(f: Formula) -> List[Clause]:
    if isinstance(f, And):
        return _extract_clauses(f.left) + _extract_clauses(f.right)
    else:
        return [Clause(frozenset(_collect_literals(f)))]

def _collect_literals(f: Formula) -> List[Formula]:
    if isinstance(f, Literal):
        return [f]
    elif isinstance(f, Or):
        return _collect_literals(f.left) + _collect_literals(f.right)
    else:
        raise ValueError(f"Expected Literal or Not(Literal) or Or, got: {type(f).__name__}")

