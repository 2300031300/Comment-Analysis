from flask import Flask, request, jsonify, render_template, send_file
from project import analyze_sentiment
import matplotlib.pyplot as plt
import io
import base64
import qrcode
app = Flask(__name__)
@app.route('/')
def home():
    return render_template("index.html")
@app.route('/qr')
def generate_qr():
    url = "http://10.121.84.0:5000"
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    comment_text = data.get("comment")
    comments = comment_text.split("\n")
    results = []
    counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for c in comments:
        if c.strip() != "":
            sentiment = analyze_sentiment(c)
            counts[sentiment] += 1
            results.append({
                "comment": c,
                "sentiment": sentiment
            })
    plt.bar(counts.keys(), counts.values())
    plt.xlabel("Sentiment Type")
    plt.ylabel("Number of Comments")
    plt.title("Sentiment Analysis Graph")
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    graph = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return jsonify({
        "results": results,
        "graph": graph
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)