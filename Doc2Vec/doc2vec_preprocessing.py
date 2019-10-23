import re
import nltk
# nltk.download('stopwords') # uncomment if running project for the first time
from nltk.corpus import stopwords

def normalize_text(text):
    normtext = re.sub(r'[^\w]', ' ', text).lower()
    norm_text = re.sub(' +', ' ', normtext)
    return norm_text


def stopping(text):
    stop_words = set(stopwords.words('english'))
    for word in stop_words:
        text = text.replace(" " + word + " ", " ")
    return text