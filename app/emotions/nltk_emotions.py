from nltk.stem.wordnet import WordNetLemmatizer
# from nltk.corpus import twitter_samples, stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
# from nltk import FreqDist, classify, NaiveBayesClassifier
import pickle
import re, string
import sys
from pathlib import Path

# Uses the stored emotion_classifier Bayesian model to classify
# emotions in text
# To test this, use the command line with a message:
# Example
# python nltk_emotions.py Wonderful day
#   Analyzing: "Wonderful day"
#   Emotion : "Positive"

NLTK_DIR = Path(__file__).resolve().parent
NLTK_MODEL_PATH_RELATIVE = NLTK_DIR / 'models' / 'emotion_classifier.pickle'

_model = None

# Load a pickled model created earlier
# See the setup directory for how to create it.
def load_model(model_file_path):
    f = open(model_file_path, 'rb')
    model = pickle.load(f)
    f.close()
    return model


def init_model():
    global _model
    _model = load_model(NLTK_MODEL_PATH_RELATIVE)
    return _model


def get_model():
    global _model
    if _model is None:
        _model = init_model()
    return _model


def remove_noise(tweet_tokens, stop_words = ()):
    cleaned_tokens = []
    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|' \
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)
        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens

def analyze(message: str) -> str:
    classifier = get_model()
    custom_tokens = remove_noise(word_tokenize(message))
    emotion = classifier.classify(dict([token, True] for token in custom_tokens))
    return emotion

def main(argv):
    if argv:
        sentence = ' '.join(sys.argv[1:])
    else:
        sentence = "I ordered just once from TerribleCo, they screwed up, never used the app again."
    print(f'Analyzing: "{sentence}"')
    emotion = analyze(sentence)
    print(f'Emotion : "{emotion}"')


if __name__ == '__main__':
    main(sys.argv[1:])

