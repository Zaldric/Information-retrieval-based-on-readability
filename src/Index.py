from math import log10, sqrt


class Index:

    def __init__(self):
        self.words = dict()
        self.documents = dict()
        self.frequencies = dict()

    def add(self, word, document):

        if word not in self.words:
            occurrences = dict()
            occurrences[document] = 1
            pair = (None, occurrences)
            self.words[word] = pair
        elif document not in self.words[word][1]:
            self.words[word][1][document] = 1
        else:
            self.words[word][1][document] += 1

    def set_frequency(self, name, words):

        word_freq = dict()

        for word in words:
            if word not in word_freq:
                word_freq[word] = 1
            else:
                word_freq[word] += 1

        freq = -1

        for value in word_freq.values():
            if value > freq:
                freq = value

        self.frequencies[name] = freq

    def calculate_weights(self):

        if '' in self.words:
            self.words.pop('', None)

        for key, value in self.words.items():

            summation = 0.0
            log = log10(len(self.frequencies) / float(len(value[1])))
            new_tuple = (log, value[1])
            self.words[key] = new_tuple

            for sub_key, sub_value in value[1].items():

                max_frequency = self.frequencies[sub_key]
                self.words[key][1][sub_key] = sub_value / max_frequency
                wij = log * self.words[key][1][sub_key]
                self.words[key][1][sub_key] = wij
                summation += (wij * wij)

            summation = sqrt(summation)

            for sub_key, sub_value in value[1].items():
                if summation == 0.0:
                    self.words[key][1][sub_key] = 0.0
                else:
                    self.words[key][1][sub_key] = sub_value / summation

    def add_document(self, document, document_info):
        self.documents[document] = document_info

    def get_index(self):
        return self.words

    def get(self, key):
        if key in self.words:
            return self.words[key]
        else:
            return None

    def get_total_documents(self):
        return len(self.documents)

    def get_number_of_words(self):
        return len(self.words)

    def get_documents(self):
        return self.documents


