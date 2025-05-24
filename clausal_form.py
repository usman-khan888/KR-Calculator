from logic_syntax import *
from structure import *

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


def _standardize_vars(f2):
    

if __name__ == '__main__':

    # Example: (P ↔ ¬Q) → R
    f = Implies(
        Iff(Var("P"), Not(Var("Q"))),
        Var("R")
        )

    print(_push_not_inward(_eliminate_iff_imp(f)))

    assert _push_not_inward(Not(Not(Var("P")))) == Var("P")
    print(str(_push_not_inward(Not(And(Var("P"),Var("Q"))))))

