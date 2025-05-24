from structure import *
        
    
if __name__ == '__main__':
    P = Literal("P", ())
    notP = P.negate()
    Q = Literal("Q", ())
    R = Literal("R", ())

    # Build clauses
    c1 = Clause(frozenset({notP, Q}))          # ¬P ∨ Q
    c2 = Clause(frozenset({P, R}))             # P ∨ R
    c3 = Clause(frozenset({R.negate(), Q}))    # ¬R ∨ Q

    kb = KB([c1, c2, c3])

    print("Knowledge Base Clauses:")
    for clause in kb.clauses:
        print(clause)
    
    # after kb = KB([c1, c2, c3])
for lit in [P, notP, Q, R]:
    print(f"{lit} appears in clauses:",
          [str(c) for c in kb.index.get(lit, [])])

