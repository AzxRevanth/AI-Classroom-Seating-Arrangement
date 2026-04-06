import re
import os
import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

STUDENTS = list("ABCDEFGHIJ")


def parse_constraints(text):
    constraints = []
    for line in text.strip().splitlines():
        low = line.strip().lower()
        if not low:
            continue
        names = [s.upper() for s in re.findall(r'\b([a-j])\b', low)]

        if "not friend" in low and len(names) >= 2:
            constraints.append({"type": "not_friends", "students": names[:2]})
        elif "friend" in low and len(names) >= 2:
            constraints.append({"type": "friends", "students": names[:2]})
        elif "front" in low:
            for s in names:
                constraints.append({"type": "front", "students": [s]})
        elif "back" in low:
            for s in names:
                constraints.append({"type": "back", "students": [s]})
        elif "teacher" in low or "visibility" in low:
            for s in names:
                constraints.append({"type": "teacher_visibility", "students": [s]})
        elif "normal" in low:
            for s in names:
                constraints.append({"type": "normal", "students": [s]})
    return constraints


def adjacent(i, j):
    ri, ci = divmod(i, 5)
    rj, cj = divmod(j, 5)
    return abs(ri - rj) + abs(ci - cj) == 1


def calc_score(arr, constraints):
    penalty = 0
    for c in constraints:
        t, s = c["type"], c["students"]
        if t == "friends":
            a, b = s
            if a in arr and b in arr and not adjacent(arr.index(a), arr.index(b)):
                penalty += 3
        elif t == "not_friends":
            a, b = s
            if a in arr and b in arr and adjacent(arr.index(a), arr.index(b)):
                penalty += 5
        elif t == "front":
            if s[0] in arr and arr.index(s[0]) >= 5:
                penalty += 4
        elif t == "back":
            if s[0] in arr and arr.index(s[0]) < 5:
                penalty += 4
        elif t == "teacher_visibility":
            if s[0] in arr and arr.index(s[0]) >= 5:
                penalty += 3
    return penalty


def hill_climb(constraints, iterations=200):
    best = random.sample(STUDENTS, len(STUDENTS))
    best_score = calc_score(best, constraints)
    for _ in range(iterations):
        candidate = best[:]
        i, j = random.sample(range(10), 2)
        candidate[i], candidate[j] = candidate[j], candidate[i]
        s = calc_score(candidate, constraints)
        if s <= best_score:
            best, best_score = candidate, s
        if best_score <= 1:
            break
    return best, best_score


def explain(arr, constraints):
    results = []
    for c in constraints:
        t, s = c["type"], c["students"]
        if t == "friends":
            a, b = s
            sat = a in arr and b in arr and adjacent(arr.index(a), arr.index(b))
            results.append({"text": f"{a} and {b} are friends", "satisfied": sat,
                             "detail": "seated adjacent" if sat else "not adjacent"})
        elif t == "not_friends":
            a, b = s
            sat = not (a in arr and b in arr and adjacent(arr.index(a), arr.index(b)))
            results.append({"text": f"{a} and {b} are not friends", "satisfied": sat,
                             "detail": "seated apart" if sat else "seated adjacent (conflict)"})
        elif t == "front":
            sat = s[0] in arr and arr.index(s[0]) < 5
            results.append({"text": f"{s[0]} wants front", "satisfied": sat,
                             "detail": "in front row" if sat else "in back row"})
        elif t == "back":
            sat = s[0] in arr and arr.index(s[0]) >= 5
            results.append({"text": f"{s[0]} wants back", "satisfied": sat,
                             "detail": "in back row" if sat else "in front row"})
        elif t == "teacher_visibility":
            sat = s[0] in arr and arr.index(s[0]) < 5
            results.append({"text": f"{s[0]} needs teacher visibility", "satisfied": sat,
                             "detail": "in front row" if sat else "in back row"})
        elif t == "normal":
            results.append({"text": f"{s[0]} is normal", "satisfied": True, "detail": "no constraint"})
    return results


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    constraints = parse_constraints(data.get("constraints", ""))
    arr, final_score = hill_climb(constraints)
    return jsonify({
        "grid": [arr[:5], arr[5:]],
        "score": final_score,
        "explanations": explain(arr, constraints)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
