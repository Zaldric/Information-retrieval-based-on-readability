import os
import pickle
import re
from src.Query import Query


class QuerySearch:

    def __init__(self, language, query, book_by_themes):
        if os.path.isfile('./src/index/index-' + language + '.p'):
            with open('./src/index/index-' + language + '.p', 'rb') as input_route:
                self.index = pickle.load(input_route)
            self.language = language
            self.query = Query(self.index, query, language)
            self.results = self.query.similarities()
            self.book_by_themes = book_by_themes
        else:
            self.results = None

    def get_readability_score(self, value):
        if self.language == 'es':
            if 0.0 <= value <= 40.0:
                return 'Muy difícil', 5

            if 40.0 <= value <= 55.0:
                return 'Algo difícil', 4

            if 55.0 <= value <= 65.0:
                return 'Normal', 3

            if 65.0 <= value <= 80.0:
                return 'Bastante fácil', 2

            return 'Muy fácil', 1

        if self.language == 'en':
            if value == 1:
                return 'Kindergarten', 6

            if value == 2:
                return 'First Grade', 7

            if value == 3:
                return 'Second Grade', 8

            if value == 4:
                return 'Third Grade', 9

            if value == 5:
                return 'Fourth Grade', 10

            if value == 6:
                return 'Fifth Grade', 11

            if value == 7:
                return 'Sixth Grade', 12

            if value == 8:
                return 'Seventh Grade', 13

            if value == 9:
                return 'Eighth Grade', 14

            if value == 10:
                return 'Ninth Grade', 15

            if value == 11:
                return 'Tenth Grade', 16

            if value == 12:
                return 'Eleventh grade', 17

            if value == 13:
                return 'Twelfth grade', 18

            return 'College', 19

    def get_ranks(self):
        if self.results:
            similarity_rank = list()
            readability_rank = list()
            if not self.book_by_themes and self.book_by_themes is not None:
                return None

            for result in self.results:
                current_document = self.index.get_documents()[result[0]]

                if self.book_by_themes:
                    if current_document.get_title() not in self.book_by_themes:
                        continue

                current_document_info = dict()
                current_document_info['title'] = current_document.get_title()
                current_document_info['readability_score'] = current_document.get_score()
                current_document_info['score_tag'] = self.get_readability_score(
                    current_document_info['readability_score'])
                search_result = current_document.search(self.query.get_original_query())
                extract = search_result[0]

                for word in search_result[1]:
                    extract = re.sub(r"\b%s\b" % word, '<b>' + word + '</b>', extract)

                current_document_info['extract'] = extract
                current_document_info['missing_words'] = [x for x in self.query.original_query if
                                                          x not in search_result[1]]
                similarity_rank.append(current_document_info)
                readability_rank.append(current_document_info)

            my_json = dict()
            my_json['similarity_rank'] = similarity_rank
            readability_rank.sort(key=lambda x: x['readability_score'], reverse=True)
            my_json['readability_rank'] = readability_rank
            return my_json
        return None
