import os
import pickle
from src.Utils import Utils


class IndexBuilder:

    def __init__(self, language):
        self.language = language
        self.unprocessed_files = list()

    def save_index(self):
        util = Utils(self.language)
        processed_files = 0

        with open('files_to_index.txt', 'r') as file:
            files = file.read().split('\n')

        if not os.path.isfile('./index/index.p'):

            for file in files:
                if file[0] != '.':
                    if util.load_words_in_index('../app/corpus/' + file, file) is None:
                        self.unprocessed_files.append(file)
                    else:
                        util.set_document_info('../app/corpus/' + file, file)
                        processed_files += 1
        else:
            with open('./index/index.p', 'rb') as input_index:
                index = pickle.load(input_index)
            util.set_index(index)

            for file in files:
                if file[0] != '.' and file not in index.get_documents():
                    if util.load_words_in_index('../app/corpus/' + file, file) is None:
                        self.unprocessed_files.append(file)
                    else:
                        util.set_document_info('../app/corpus/' + file, file)
                        processed_files += 1

        if processed_files > 0:
            util.get_index().calculate_weights()
            pickle.dump(util.get_index(), open("./index/index.p", "wb"))
            with open('./index/index.p', 'wb') as output:
                pickle.dump(util.get_index(), output, pickle.HIGHEST_PROTOCOL)
        else:
            print("The requested files couldn't be processed.")
            exit(1)
