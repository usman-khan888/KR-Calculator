from logic_syntax import *
from structure import *
from itertools import count


_var_counter = count()




def clausal_form_converter(formula: Formula) -> List[Clause]:
    f1 = _eliminate_iff_imp(formula)
    f2 = _push_not_inward(f1)
    f3 = _standardize_vars(f2)
    f4 = _to_prenex(f3)
    f5 = _skolemize(f4)
    f6 = _drop_universals(f5)
    f7 = _distribute_or_over_and(f6)
    flat = _flatten_ands(f7)
    return _extract_clauses(flat)

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
        
        return f  # Not(Var)
    
    if isinstance(f, And):
        return And(_push_not_inward(f.left), _push_not_inward(f.right))
    
    if isinstance(f, Or):
        return Or(_push_not_inward(f.left), _push_not_inward(f.right))
    
    if isinstance(f, ForAll):
        return ForAll(f.var, _push_not_inward(f.sub))
    
    if isinstance(f, Exists):
        return Exists(f.var, _push_not_inward(f.sub))
    
    return f # Var


def _fresh_var(base: str) -> str:
    return f"{base}_{next(_var_counter)}"

def _standardize_vars(formula: Formula) -> Formula:
    return _standardize_helper(formula, {})

def _standardize_helper(f: Formula, env: Dict[str, str]) -> Formula:
    if isinstance(f, Var):
        return Var(env.get(f.name, f.name))

    if isinstance(f, ForAll):
        new_var = _fresh_var(f.var)
        new_env = env.copy()
        new_env[f.var] = new_var
        return ForAll(new_var, _standardize_helper(f.sub, new_env))

    if isinstance(f, Exists):
        new_var = _fresh_var(f.var)
        new_env = env.copy()
        new_env[f.var] = new_var
        return Exists(new_var, _standardize_helper(f.sub, new_env))

    if isinstance(f, Not):
        return Not(_standardize_helper(f.sub, env))

    if isinstance(f, And):
        return And(_standardize_helper(f.left, env), _standardize_helper(f.right, env))
    if isinstance(f, Or):
        return Or(_standardize_helper(f.left, env), _standardize_helper(f.right, env))
    if isinstance(f, Implies):
        return Implies(_standardize_helper(f.provided, env), _standardize_helper(f.then, env))
    if isinstance(f, Iff):
        return Iff(_standardize_helper(f.left, env), _standardize_helper(f.right, env))

    return f


def _to_prenex(f: Formula) -> Formula:
    quantifiers, matrix = _pull_quantifiers(f) # Gets a list of quantifiers in order and the formula that follows without any quantifiers
    # Rebuilds the statements starting with the quantifiers from right to left
    for q in reversed(quantifiers):
        if isinstance(q, ForAll):
            matrix = ForAll(q.var, matrix)
        else:
            matrix = Exists(q.var, matrix)
    return matrix

def _pull_quantifiers(f: Formula) -> tuple[list[Union[ForAll, Exists]], Formula]:
    #Remove the quantifier and ands it into a list to preserve order
    if isinstance(f, (ForAll, Exists)):
        qs, body = _pull_quantifiers(f.sub)
        return [f] + qs, body
    elif isinstance(f, And):
        ql1, f1 = _pull_quantifiers(f.left)
        ql2, f2 = _pull_quantifiers(f.right)
        return ql1 + ql2, And(f1, f2)
    elif isinstance(f, Or):
        ql1, f1 = _pull_quantifiers(f.left)
        ql2, f2 = _pull_quantifiers(f.right)
        return ql1 + ql2, Or(f1, f2)
    else:
        return [], f

    

if __name__ == '__main__':

    # Example: (P ↔ ¬Q) → R
    f = Implies(
        Iff(Var("P"), Not(Var("Q"))),
        Var("R")
        )

    print(_push_not_inward(_eliminate_iff_imp(f)))

    assert _push_not_inward(Not(Not(Var("P")))) == Var("P")
    print(str(_push_not_inward(Not(And(Var("P"),Var("Q"))))))

