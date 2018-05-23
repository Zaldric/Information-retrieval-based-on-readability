import pickle
from src.Query import Query


class QuerySearch:

    def __init__(self, language, query):
        with open('./src/index/index.p', 'rb') as input_route:
            self.index = pickle.load(input_route)
        self.language = language
        self.query = Query(self.index, query, language)
        self.results = self.query.similarities()

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

    def get_ranks(self):
        if self.results:
            similarity_rank = list()

            for top in range(0, len(self.results)):
                current_document = self.index.get_documents()[self.results[top][0]]
                current_document_info = dict()
                current_document_info['rank'] = top + 1
                current_document_info['similarity'] = self.results[top][1]
                current_document_info['readability_score'] = current_document.get_score()
                current_document_info['score_tag'] = self.get_readability_score(current_document_info['readability_score'])
                current_document_info['title'] = current_document.get_title()
                current_document_info['extract'] = current_document.search(self.query.get_query())
                similarity_rank.append(current_document_info)

            my_json = dict()
            my_json['similarity_rank'] = similarity_rank
            readability_rank = list()

            for top in range(0, len(self.results)):
                current_document = self.index.get_documents()[self.results[top][0]]
                current_document_info = dict()
                current_document_info['rank'] = top + 1
                current_document_info['readability_score'] = current_document.get_score()
                current_document_info['score_tag'] = self.get_readability_score(current_document_info['readability_score'])
                current_document_info['title'] = current_document.get_title()
                current_document_info['extract'] = current_document.search(self.query.get_query())
                readability_rank.append(current_document_info)
            readability_rank.sort(key=lambda x: x['readability_score'], reverse=True)
            my_json['readability_rank'] = readability_rank
            return my_json
        return None
