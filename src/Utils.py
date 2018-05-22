import nltk
import unidecode
from src.Index import Index
from src.DocInfo import DocInfo
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import SnowballStemmer
from epub_conversion.utils import open_book, convert_epub_to_lines
from bs4 import BeautifulSoup
from nltk import re


class Utils:

    sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    def __init__(self, language):
        self.stop_words = dict()
        self.index = Index()
        self.language = language

        if language == 'en':
            self.stop_words = set(stopwords.words('english'))
            self.stemmer = PorterStemmer()
        else:
            self.stop_words = set(stopwords.words('spanish'))
            self.stemmer = SnowballStemmer('spanish')

    @staticmethod
    def process_file(file_path):
        if '.txt' in file_path:
            with open(file_path) as file:
                text = file.read()
            return text

        if '.epub' in file_path:
            book = open_book(file_path)
            lines = convert_epub_to_lines(book)
            html = ' '.join(lines)
            html = html.replace('</body>', ' ')
            html = html.replace('</html>', ' ')
            soup = BeautifulSoup(html, 'lxml')
            text = ''

            for node in soup.findAll('p'):
                text += ''.join(node.findAll(text=True)) + '\n'
            return text

    @staticmethod
    def clean_text(text):
        text = unidecode.unidecode(text.lower())
        text = re.sub('[^a-z0-9-]', ' ', text)
        return text

    def load_words(self, words, document):
        for word in words:
            if word not in self.stop_words:
                self.index.add(word, document)

    def set_frequency(self, name, words):
        self.index.set_frequency(name, words)

    @staticmethod
    def stemmer(words, language):
        stem_words = list()
        if language == 'en':
            stemmer = PorterStemmer()
        else:
            stemmer = SnowballStemmer('spanish')
        for word in words:
            stem_words.append(stemmer.stem(word))
        return stem_words

    def get_cleaned_tokens(self, text):
        text = self.clean_text(text)
        tokens = text.split()
        cleaned_tokens = list()

        for token in tokens:
            if token not in self.stop_words:
                cleaned_tokens.append(token)
        return cleaned_tokens

    def load_words_in_index(self, path, name):
        file = self.process_file(path)
        if file is '':
            return None
        cleaned_tokens = self.get_cleaned_tokens(file)
        steam_tokens = list()

        for token in cleaned_tokens:
            steam_tokens.append(self.stemmer.stem(token))

        self.set_frequency(name, steam_tokens)
        self.load_words(steam_tokens, name)

        return len(steam_tokens)

    def set_document_info(self, path, name):
        text = self.process_file(path)
        score = self.get_score(text)
        doc_info = DocInfo(name, text, score, self.stemmer)
        self.index.add_document(name, doc_info)

    def get_score(self, text):
        if self.language == 'es':
            sentences = len(self.sentence_tokenizer.tokenize(text))
            clean_text = self.clean_text(text)
            words = len(clean_text.split())
            syllables = len(re.findall('[aeiou]', clean_text))
            score = 206.835 - (62.3 * (syllables / words)) - (words / sentences)
            return score
        else:
            score = None
        return score

    def get_index(self):
        return self.index

    def set_index(self, index):
        self.index = index
