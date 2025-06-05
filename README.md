## Attribution
Created by [usman-khan888](https://github.com/usman-khan888). Please credit this repo if you use or build on it.

# KR Calculator — A Logic Inference Engine

A Python-powered engine that takes in a knowledge base of logical clauses and determines the truth of a given statement using resolution refutation. The system includes a full CNF pipeline.

> Built for learners, tinkerers, and anyone curious about formal reasoning.

---

## 🧠 What This Project Does

- Converts logical formulas into **clausal form** (CNF)
- Standardizes variables to avoid capture
- Uses **resolution-based inference** to determine satisfiability
- Will allow users to create a KB and test clauses.
- Users will be able to write in natural language and the program will interpret and convert to FOL.
- Designed with scalability and efficiency in mind (version control, Docker, and clean architecture)

---

## 🌍 Why This Exists

I believe logic-based math can be taught in a more intuitive, hands-on way — and that tools like this can help people learn reasoning early, without the intimidation of dense theory.

This is part of my broader goal to create accessible, free tech that expands opportunity for others.

---

---

## Work in Progress

1. Unifiying and substituting variables.
2. Refutation Proof.
3. Knowledge Base storage and Data Structure.
4. Create Website where User can create KB's, convert logical statements into CNF and test statements under a system.
4. Using LLM to help converst NL statements into logical statements that can be plugged into the CNF pipeline.

---

## 🚀 Getting Started

### Requirements
- Python 3.10+
- Docker (optional but recommended)

### Run Locally
```bash
git clone https://github.com/usman-khan888/KR-Calculator.git
cd KR-Calculator
python resolution.py

