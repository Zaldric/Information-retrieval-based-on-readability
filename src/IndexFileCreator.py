import os
import pickle
from src.Utils import Utils
from os import listdir
from os.path import isfile, join


class IndexFileCreator:

    def __init__(self, language, books_for_index):
        self.language = language
        self.unprocessed_files = list()
        self.books_for_index = books_for_index
        self.processed_files = list()

    def save_index(self):
        util = Utils(self.language)
        processed_files = 0

        if not os.path.isfile('./src/index/index-' + self.language + '.p'):

            for file in [f for f in listdir('./app/corpus/' + self.language) if
                         isfile(join('./app/corpus/' + self.language, f))]:
                if file[0] != '.':
                    text = util.process_file('./app/corpus/' + self.language + '/' + file)
                    if util.load_words_in_index(text, file) is None:
                        self.unprocessed_files.append(file)
                    else:
                        util.set_document_info(text, file)
                        processed_files += 1
                        self.processed_files.append(file)
        else:
            with open('./src/index/index-' + self.language + '.p', 'rb') as input_index:
                index = pickle.load(input_index)
            util.set_index(index)

            for file in self.books_for_index:
                if file[0] != '.' and file not in index.get_documents():
                    text = util.process_file('./app/corpus/' + self.language + '/' + file)
                    if util.load_words_in_index(text, file) is None:
                        self.unprocessed_files.append(file)
                    else:
                        util.set_document_info(text, file)
                        processed_files += 1
                        self.processed_files.append(file)

        if processed_files > 0:
            util.get_index().calculate_weights()
            pickle.dump(util.get_index(), open('./src/index/index-' + self.language + '.p', 'wb'))
            with open('./src/index/index-' + self.language + '.p', 'wb') as output:
                pickle.dump(util.get_index(), output, pickle.HIGHEST_PROTOCOL)
        else:
            exit(1)

    def get_unprocessed_files(self):
        return self.unprocessed_files

    def get_processed_files(self):
        return self.processed_files
