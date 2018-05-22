import re
import nltk
from unidecode import unidecode
import src.Utils


class DocInfo:

    sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    def __init__(self, title, body, score, stemmer):
        self.title = title
        self.score = score
        self.phrases = list()
        self.clean_phrases = list()
        self.words_frequency = list()

        self.set_phrases(body, stemmer)

    def set_phrases(self, body, stemmer):
        self.phrases.append(self.title)
        self.phrases += self.sentence_tokenizer.tokenize(body)

        for phrase in self.phrases:
            self.clean_phrases.append(self.stemmer(src.Utils.Utils.clean_text(phrase), stemmer))

    def search(self, words):
        i = 0

        for clean_phrase in self.clean_phrases:
            phrase_words = clean_phrase.split()

            for word in words:
                for phrase_word in phrase_words:
                    if phrase_word == word:
                        return self.phrases[i]
            i += 1

        return ''

    @staticmethod
    def stemmer(text, stemmer):
        text = unidecode(text.lower())
        text = re.sub('[^a-z0-9-]', ' ', text)
        stem_words = list()

        for word in text.split():
            stem_words.append(stemmer.stem(word))

        return ' '.join(stem_words)

    def get_title(self):
        return self.title

    def get_score(self):
        return self.score
