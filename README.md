👉 I built this project with the help of AI for code suggestions and explanations.

# 🎯 DFA Equivalence Checker

This project is a **Python tool to check the equivalence of two Deterministic Finite Automata (DFAs)**.  
It uses the **cross-product construction method** to determine whether two DFAs accept the same language.  

If the DFAs are not equivalent, the program generates a **counterexample string** (a string accepted by one DFA but rejected by the other).  
It also supports **visualization of the DFAs** using [Graphviz](https://graphviz.org/).

---

## 🚀 Features
- Input DFAs in structural form (states, alphabet, transition function, start state, accept states).
- Implements **cross-product construction** for equivalence checking.
- Finds and displays a **counterexample string** if the DFAs are not equivalent.
- **Visualizes** both DFAs as `.png` images using Graphviz.

---

## 🛠️ Requirements
- Python 3.x  
- [Graphviz (System Software)](https://graphviz.gitlab.io/download/)  
- Python Graphviz package  

Install the Python package:
```bash
pip install graphviz
