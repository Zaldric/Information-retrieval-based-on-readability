import operator
from src.Utils import Utils
from math import sqrt


class Query:

    def __init__(self, index, query, language):
        self.results = list()
        self.query = dict()

        util = Utils(language)
        self.index = index
        cleaned_query = Utils.stemmer(util.get_cleaned_tokens(query), language)

        self.add_query_words(cleaned_query)
        self.normalize_frequencies()

    def add_query_words(self, words):
        for word in words:
            found = False
            for key, value in self.query.items():
                if key == word:
                    new_tuple = (word, value + 1)
                    self.query[word] = new_tuple
                    found = True

            if not found:
                self.query[word] = 1.0

    def normalize_frequencies(self):
        max_frequency = max(self.query.items(), key=operator.itemgetter(1))[1]

        for key in self.query.keys():
            self.query[key] /= max_frequency

        wniq_sum = 0.0

        for key, value in self.query.items():
            index_result = self.index.get(key)
            if index_result:
                idf = index_result[0]
                wniq = value * idf
                wniq_sum += wniq * wniq

        wniq_sum = sqrt(wniq_sum)

        if wniq_sum == 0.0:
            self.query = dict.fromkeys(self.query, 0.0)
        else:
            for key, value in self.query.items():
                if key in self.index.get_index().keys():
                    idf = self.index.get(key)[0]
                    wniq = (value * idf) / wniq_sum
                    self.query[key] = wniq

    def similarities(self):
        if self.query:
            wniq_norm = 0.0

            for key, value in self.query.items():
                if key in self.index.get_index():
                    wniq_norm += value * value

            wniq_norm = sqrt(wniq_norm)

            for document in self.index.get_documents().keys():
                numerator, wnij_norm = 0.0, 0.0
                for query_word, query_value in self.query.items():
                    if query_word in self.index.get_index():
                        if document in self.index.get(query_word)[1]:
                            wnij = self.index.get(query_word)[1][document]
                            numerator += query_value * wnij
                            wnij_norm += wnij * wnij

                wnij_norm = sqrt(wnij_norm)

                if numerator != 0.0:
                    denominator = wniq_norm * wnij_norm
                    self.results.append((document, numerator / denominator))

            self.results = sorted(self.results, key=lambda tup: tup[1], reverse=True)
            return self.results

    def get_query(self):
        words = list()
        for key in self.query.keys():
            words.append(key)
        return words


