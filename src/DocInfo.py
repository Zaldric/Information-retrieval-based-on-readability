import math
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
        iteration = 0
        limit = math.ceil(len(words) / 2)
        last_match = 0

        for phrase in self.phrases:
            clean_phrase_words = src.Utils.Utils.clean_text(phrase).split()
            match_counter = 0

            for word in words:
                if any(single_word in clean_phrase_words for single_word in [word]):
                    match_counter += 1
                    last_match = iteration

            if match_counter >= limit:
                bold_words = list()
                for phrase_word in phrase.split():
                    clean_phrase_word = src.Utils.Utils.clean_text(phrase_word).strip()
                    if clean_phrase_word in words:
                        if phrase_word not in bold_words:
                            bold_words.append(clean_phrase_word)
                return self.phrases[iteration], bold_words

            iteration += 1

        bold_words = list()
        for phrase_word in self.phrases[last_match].split():
            clean_phrase_word = src.Utils.Utils.clean_text(phrase_word).strip()
            if clean_phrase_word in words:
                if phrase_word not in bold_words:
                    bold_words.append(clean_phrase_word)
        return self.phrases[last_match], bold_words

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
