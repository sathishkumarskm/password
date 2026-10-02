from flask import Flask, jsonify, render_template, request
import random
import re
import string

app = Flask(__name__)

COMMON_PATTERNS = re.compile(
    r"(password|admin|welcome|letmein|qwerty|123456|abc123|qazwsx|monkey|login)"
)


def password_strength(password: str):
    if password is None:
        password = ""

    score = 0
    issues = []

    if not password:
        return {
            "score": 0,
            "label": "Weak",
            "length": 0,
            "feedback": ["Enter a password to check its strength."],
            "checks": {
                "length": False,
                "lowercase": False,
                "uppercase": False,
                "number": False,
                "symbol": False,
            },
        }

    if len(password) >= 16:
        score += 30
    elif len(password) >= 12:
        score += 20
    elif len(password) >= 8:
        score += 10
    else:
        issues.append("Use at least 8 characters.")

    checks = {
        "length": len(password) >= 8,
        "lowercase": bool(re.search(r"[a-z]", password)),
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "number": bool(re.search(r"\d", password)),
        "symbol": bool(re.search(r"[^A-Za-z0-9]", password)),
    }

    if checks["lowercase"]:
        score += 15
    else:
        issues.append("Add lowercase letters.")

    if checks["uppercase"]:
        score += 15
    else:
        issues.append("Add uppercase letters.")

    if checks["number"]:
        score += 15
    else:
        issues.append("Add numbers.")

    if checks["symbol"]:
        score += 15
    else:
        issues.append("Add symbols like !, @, #, or $.")

    if len(set(password)) >= max(6, len(password) // 2):
        score += 10

    if re.search(r"\s", password):
        score -= 10
        issues.append("Avoid spaces.")

    if COMMON_PATTERNS.search(password.lower()):
        score -= 20
        issues.append("Avoid common words and patterns.")

    if re.search(r"(.)\1{2,}", password):
        score -= 10
        issues.append("Avoid repeated characters like aaa.")

    if len(password) > 30:
        score += 5

    score = max(0, min(100, score))

    if score < 35:
        label = "Weak"
    elif score < 70:
        label = "Moderate"
    else:
        label = "Strong"

    unique_feedback = []
    seen = set()
    for item in issues:
        if item not in seen:
            seen.add(item)
            unique_feedback.append(item)

    return {
        "score": score,
        "label": label,
        "length": len(password),
        "feedback": unique_feedback if unique_feedback else ["Good password quality."],
        "checks": checks,
    }


def generate_password(length=14):
    if length < 8:
        length = 8
    if length > 32:
        length = 32

    characters = string.ascii_letters + string.digits + string.punctuation
    password = []
    password.append(random.choice(string.ascii_lowercase))
    password.append(random.choice(string.ascii_uppercase))
    password.append(random.choice(string.digits))
    password.append(random.choice(string.punctuation))

    for _ in range(length - 4):
        password.append(random.choice(characters))

    random.shuffle(password)
    generated = "".join(password)

    while not (
        re.search(r"[a-z]", generated)
        and re.search(r"[A-Z]", generated)
        and re.search(r"\d", generated)
        and re.search(r"[^A-Za-z0-9]", generated)
    ):
        password = [random.choice(characters) for _ in range(length)]
        random.shuffle(password)
        generated = "".join(password)

    return generated


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    password = str(data.get("password", ""))
    return jsonify(password_strength(password))


@app.route("/api/generate")
def generate():
    length = request.args.get("length", default=14, type=int)
    return jsonify({"password": generate_password(length)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
