from flask import Flask, render_template, request, jsonify
from collections import deque
import graphviz
import os
import markdown
from dotenv import load_dotenv

app = Flask(__name__)
IMAGE_FOLDER = 'static/dfa_images'
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# ------------------ GEMINI API -------------------
import google.generativeai as genai

# ⚠️ REPLACE this key with a NEW regenerated one
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# --------------------------------------------------

# ------------------ DFA CLASS ---------------------
class DFA:
    def __init__(self, states, alphabet, transition, start, accept):
        self.states = states
        self.alphabet = alphabet
        self.transition = transition
        self.start = start
        self.accept = accept

    def move(self, state, symbol):
        return self.transition[(state, symbol)]

# --------------- DFA EQUIVALENCE ------------------
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

# --------------- DFA VISUALIZATION ----------------
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


# ------------------ MAIN PAGE ---------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # ----------- RAW INPUT (needed for history + AI) ----------
        raw1 = {
            "states": request.form['states1'],
            "alphabet": request.form['alphabet1'],
            "start": request.form['start1'],
            "accept": request.form['accept1'],
            "transitions": request.form['transitions1']
        }

        raw2 = {
            "states": request.form['states2'],
            "alphabet": request.form['alphabet2'],
            "start": request.form['start2'],
            "accept": request.form['accept2'],
            "transitions": request.form['transitions2']
        }

        # ------------------ PARSE DFA 1 -----------------------
        states1 = raw1["states"].split(',')
        alphabet1 = raw1["alphabet"].split(',')
        accept1 = raw1["accept"].split(',')
        transitions1 = {}

        for t in raw1["transitions"].split(';'):
            if t.strip():
                s, sym, ns = t.strip().split()
                transitions1[(s, sym)] = ns

        dfa1 = DFA(states1, alphabet1, transitions1, raw1["start"], accept1)

        # ------------------ PARSE DFA 2 -----------------------
        states2 = raw2["states"].split(',')
        alphabet2 = raw2["alphabet"].split(',')
        accept2 = raw2["accept"].split(',')
        transitions2 = {}

        for t in raw2["transitions"].split(';'):
            if t.strip():
                s, sym, ns = t.strip().split()
                transitions2[(s, sym)] = ns

        dfa2 = DFA(states2, alphabet2, transitions2, raw2["start"], accept2)

        # ------------------ EQUIVALENCE CHECK ----------------
        equivalent, counterexample = check_equivalence(dfa1, dfa2)

        # ------------------ DRAW DFA IMAGES -------------------
        img1 = visualize_dfa(dfa1, 'dfa1')
        img2 = visualize_dfa(dfa2, 'dfa2')

        return render_template(
            "result.html",
            equivalent=equivalent,
            counterexample=counterexample,
            img1=img1,
            img2=img2,
            raw1=raw1,
            raw2=raw2
        )

    return render_template("index.html")


# ------------------ AI EXPLANATION API ----------------------
@app.route("/ai_explain", methods=["POST"])
def ai_explain():
    try:
        data = request.get_json()

        dfa1 = data["dfa1"]
        dfa2 = data["dfa2"]
        equivalent = data["equivalent"]
        counterexample = data["counterexample"]

        prompt = f"""
        You are an Automata Theory tutor.
        Explain whether the following two DFAs are equivalent or not.

        DFA 1:
        States: {dfa1['states']}
        Alphabet: {dfa1['alphabet']}
        Start: {dfa1['start']}
        Accept: {dfa1['accept']}
        Transitions: {dfa1['transitions']}

        DFA 2:
        States: {dfa2['states']}
        Alphabet: {dfa2['alphabet']}
        Start: {dfa2['start']}
        Accept: {dfa2['accept']}
        Transitions: {dfa2['transitions']}

        Result: {"Equivalent" if equivalent else "Not Equivalent"}
        Counterexample: {counterexample}

        Provide a clear, student-friendly explanation with headings and bullet points.
        """

        model = genai.GenerativeModel("models/gemini-pro-latest")
        response = model.generate_content(prompt)

        explanation = ""
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text"):
                explanation += part.text

        html = markdown.markdown(explanation)
        return jsonify({"explanation": html})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



#-----------------for chat box-------------

@app.route("/ai_chat", methods=["POST"])
def ai_chat():
    try:
        data = request.get_json()

        user_message = data["message"]
        dfa1 = data["dfa1"]
        dfa2 = data["dfa2"]

        prompt = f"""
        You are an Automata Theory tutor chatting with a student.

        The student is studying these two DFAs:

        DFA 1:
        States: {dfa1['states']}
        Alphabet: {dfa1['alphabet']}
        Start: {dfa1['start']}
        Accept: {dfa1['accept']}
        Transitions: {dfa1['transitions']}

        DFA 2:
        States: {dfa2['states']}
        Alphabet: {dfa2['alphabet']}
        Start: {dfa2['start']}
        Accept: {dfa2['accept']}
        Transitions: {dfa2['transitions']}

        The student asked: \"{user_message}\"

        Answer in a friendly, clear way. 
        Use headings and bullet points when helpful. 
        Keep the explanation focused on automata / DFAs unless they ask general questions.
        """

        model = genai.GenerativeModel("models/gemini-pro-latest")
        response = model.generate_content(prompt)

        reply_text = ""
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text"):
                reply_text += part.text

        reply_html = markdown.markdown(reply_text)
        return jsonify({"reply": reply_html})

    except Exception as e:
        return jsonify({"error": str(e)}), 500






# ------------------ RUN FLASK ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
