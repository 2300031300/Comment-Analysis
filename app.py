from flask import Flask, render_template, request
import spacy
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")
train_texts = [
    "Somu works at Infosys",
    "Jaggu joined in Bussiness",
    "Cherry lives in Amalapuram"
]
labels = ["works_at", "works_at", "lives_in"]
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(train_texts)
model = LogisticRegression()
model.fit(X, labels)
def rule_based_extraction(texts):
    rb = []
    for t in texts:
        doc = nlp(t)
        for token in doc:
            if token.dep_ == "prep" and list(token.children):
                rb.append([
                    token.head.text,
                    token.text,
                    list(token.children)[0].text
                ])
    return pd.DataFrame(rb, columns=["Subject", "Relation", "Object"])


@app.route("/", methods=["GET", "POST"])
def index():
    rb_table = None
    ml_table = None

    if request.method == "POST":
        input_text = request.form["sentences"]
        texts = [t.strip() for t in input_text.split("\n") if t.strip()]

        # Rule-Based
        rb_table = rule_based_extraction(texts)

        # ML-Based
        X_test = vectorizer.transform(texts)
        preds = model.predict(X_test)
        ml_table = pd.DataFrame({
            "Sentence": texts,
            "Predicted Relation": preds
        })

    return render_template(
        "index.html",
        rb_table=rb_table,
        ml_table=ml_table
    )


if __name__ == "__main__":
    app.run(debug=True)
