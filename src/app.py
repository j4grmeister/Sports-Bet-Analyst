from flask import Flask, request, jsonify, render_template
import subprocess

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    
    available_cash = request.form.get("cash", "")

    try:
        result = subprocess.run(
            ["python3", "src\\predict_upcoming_mlb.py", available_cash],
            capture_output=True, text=True, timeout=60
        )
        output = result.stdout.strip()
    except Exception as e:
        output = f"Error: {str(e)}"
    
    return jsonify({"output": output})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)