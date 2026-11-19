
from flask import Flask, request, jsonify, render_template, send_file
from project import analyze_sentiment

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import io
import base64
import qrcode
import csv

app = Flask(__name__)

# Maximum CSV upload size: 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# Home page
@app.route('/')
def home():
    return render_template("index.html")


# Generate QR code
@app.route('/qr')
def generate_qr():

    url = "http://10.121.84.0:5000"

    img = qrcode.make(url)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype="image/png")


# Common function for sentiment analysis
def process_comments(comments):

    results = []

    counts = {
        "Positive": 0,
        "Negative": 0,
        "Neutral": 0
    }

    for comment in comments:

        if comment and comment.strip():

            sentiment = analyze_sentiment(comment)

            counts[sentiment] += 1

            results.append({
                "comment": comment,
                "sentiment": sentiment
            })

    # Generate sentiment graph
    plt.figure(figsize=(7, 5))

    plt.bar(counts.keys(), counts.values())

    plt.xlabel("Sentiment Type")
    plt.ylabel("Number of Comments")
    plt.title("Sentiment Analysis Graph")

    plt.tight_layout()

    img = io.BytesIO()

    plt.savefig(img, format="png")

    img.seek(0)

    graph = base64.b64encode(
        img.getvalue()
    ).decode("utf-8")

    plt.close()

    return jsonify({
        "results": results,
        "counts": counts,
        "total": len(results),
        "graph": graph
    })


# METHOD 1: Manual comment input
@app.route('/analyze', methods=['POST'])
def analyze():

    data = request.get_json(silent=True) or {}

    comment_text = data.get("comment", "")

    if not isinstance(comment_text, str):
        return jsonify({
            "error": "Invalid comment input."
        }), 400

    comments = comment_text.splitlines()

    if not any(c.strip() for c in comments):
        return jsonify({
            "error": "Please enter some comments."
        }), 400

    return process_comments(comments)


# METHOD 2: CSV dataset upload
@app.route('/upload', methods=['POST'])
def upload_csv():

    if 'dataset' not in request.files:
        return jsonify({
            "error": "Please select a CSV file."
        }), 400

    file = request.files['dataset']

    if file.filename == "":
        return jsonify({
            "error": "No file selected."
        }), 400

    if not file.filename.lower().endswith('.csv'):
        return jsonify({
            "error": "Please upload a CSV file only."
        }), 400

    try:

        # Read CSV file
        stream = io.TextIOWrapper(
            file.stream,
            encoding="utf-8-sig",
            newline=""
        )

        reader = csv.DictReader(stream)

        # Check CSV headers
        if not reader.fieldnames:
            return jsonify({
                "error": "CSV file is empty."
            }), 400

        # Remove spaces and ignore capitalization
        column_mapping = {
            column.strip().lower(): column
            for column in reader.fieldnames
            if column is not None
        }

        # Your dataset contains the column named 'comment'
        if "comment" not in column_mapping:
            return jsonify({
                "error": "CSV must contain a column named 'comment'.",
                "available_columns": list(column_mapping.keys())
            }), 400

        # Get the actual column name from CSV
        actual_column = column_mapping["comment"]

        comments = []

        for row in reader:

            comment = row.get(actual_column)

            if comment and comment.strip():
                comments.append(comment.strip())

        if not comments:
            return jsonify({
                "error": "No comments found in the CSV file."
            }), 400

        # Analyze all CSV comments
        return process_comments(comments)

    except UnicodeDecodeError:

        return jsonify({
            "error": "Unable to read CSV. Please use UTF-8 encoding."
        }), 400

    except csv.Error:

        return jsonify({
            "error": "Invalid CSV file format."
        }), 400

    except Exception:

        app.logger.exception("CSV processing failed")

        return jsonify({
            "error": "Something went wrong while processing the dataset."
        }), 500


# Handle large files
@app.errorhandler(413)
def file_too_large(error):

    return jsonify({
        "error": "File too large. Maximum allowed size is 10 MB."
    }), 413


# Run Flask application
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
