import pickle
from src.Query import Query


class QuerySearch:

    def __init__(self, language, query):
        with open('index.p', 'rb') as input_route:
            self.index = pickle.load(input_route)
        self.query = query
        self.results = Query(self.index, query, language).similarities()

    def get_ranks(self):
        similarity_rank = list()

        for top in range(0, len(self.results)):
            current_document = self.index.get_documents()[self.results[top][0]]
            current_document_info = dict()
            current_document_info['rank'] = top + 1
            current_document_info['similarity'] = self.index.get_documents()[self.results[top][1]]
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
            current_document_info['title'] = current_document.get_title()
            current_document_info['extract'] = current_document.search(self.query.get_query())
            readability_rank.append(current_document_info)

        my_json['readabily_rank'] = readability_rank.sort(key=lambda x: x['readability_score'])
        return my_json
