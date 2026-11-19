import re
import nltk
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('stopwords')
nltk.download('vader_lexicon')

stop_words = set(stopwords.words('english'))

negation_words = {"not", "no", "never"}
stop_words = stop_words - negation_words

sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)

    words = [w for w in text.split() if w not in stop_words]
    clean_text = " ".join(words)

    score = sia.polarity_scores(clean_text)['compound']

    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"