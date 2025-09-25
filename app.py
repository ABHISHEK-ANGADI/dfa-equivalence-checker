from flask import Flask, render_template, request
from collections import deque
import graphviz
import os

app = Flask(__name__)
IMAGE_FOLDER = 'static/dfa_images'
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# DFA Class
class DFA:
    def __init__(self, states, alphabet, transition, start, accept):
        self.states = states
        self.alphabet = alphabet
        self.transition = transition
        self.start = start
        self.accept = accept

    def move(self, state, symbol):
        return self.transition[(state, symbol)]

# Equivalence Checker
def check_equivalence(dfa1, dfa2):
    visited = set()
    queue = deque()
    queue.append((dfa1.start, dfa2.start, ""))

    while queue:
        s1, s2, string = queue.popleft()
        if (s1, s2) in visited:
            continue
        visited.add((s1, s2))
        if (s1 in dfa1.accept) != (s2 in dfa2.accept):
            return False, string
        for symbol in dfa1.alphabet:
            ns1 = dfa1.move(s1, symbol)
            ns2 = dfa2.move(s2, symbol)
            queue.append((ns1, ns2, string + symbol))
    return True, None

# Visualization
def visualize_dfa(dfa, filename):
    dot = graphviz.Digraph(format='png')
    for state in dfa.states:
        dot.node(state, shape='doublecircle' if state in dfa.accept else 'circle')
    dot.node('', shape='none')
    dot.edge('', dfa.start)
    for (state, symbol), next_state in dfa.transition.items():
        dot.edge(state, next_state, label=symbol)
    filepath = os.path.join(IMAGE_FOLDER, filename)
    dot.render(filepath, cleanup=True)
    return filepath + '.png'

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get DFA 1
        states1 = request.form['states1'].split(',')
        alphabet1 = request.form['alphabet1'].split(',')
        start1 = request.form['start1']
        accept1 = request.form['accept1'].split(',')
        transitions1 = {}
        for t in request.form['transitions1'].split(';'):
            if t.strip() == '':
                continue
            s, sym, ns = t.strip().split()
            transitions1[(s, sym)] = ns
        dfa1 = DFA(states1, alphabet1, transitions1, start1, accept1)

        # Get DFA 2
        states2 = request.form['states2'].split(',')
        alphabet2 = request.form['alphabet2'].split(',')
        start2 = request.form['start2']
        accept2 = request.form['accept2'].split(',')
        transitions2 = {}
        for t in request.form['transitions2'].split(';'):
            if t.strip() == '':
                continue
            s, sym, ns = t.strip().split()
            transitions2[(s, sym)] = ns
        dfa2 = DFA(states2, alphabet2, transitions2, start2, accept2)

        # Check equivalence
        equivalent, counterexample = check_equivalence(dfa1, dfa2)

        # Visualize DFAs
        img1 = visualize_dfa(dfa1, 'dfa1')
        img2 = visualize_dfa(dfa2, 'dfa2')

        return render_template("result.html",
                               equivalent=equivalent,
                               counterexample=counterexample,
                               img1=img1,
                               img2=img2)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
