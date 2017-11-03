from elasticsearch import Elasticsearch

class DBElasticsearch ():

	def __init__ (self, index_name, type_name):
		self.index_name = index_name
		self.type_name = type_name
		self.es = Elasticsearch()

	def store (self, tracker_id, body):
		res = self.es.index (	index = self.index_name, 
								doc_type = self.type_name, 
								routing = tracker_id, 
								body = body,
								refresh = True)

	def retrieve (self, tracker_id, from_, size):
		res = self.es.search (	index = self.index_name,
								doc_type = self.type_name,
								routing = tracker_id, 
								from_ = from_,
								size = size,
								sort = "_time:desc",
								body = {"query": {"match": {"_tracker_id": tracker_id}}})

		return [x["_source"] for x in res["hits"]["hits"]]

	def search (self, tracker_id, query):
		body = 	{ 
					"query": {
						"bool": {
							"must": [
								{"match": {"_tracker_id": tracker_id}},
								query
							]
						}
					}
				}

		res = self.es.search ( 	index = self.index_name,
								doc_type = self.type_name,
								routing = tracking_id,
								body = body)
		
		return [x["_source"] for x in res["hits"]["hits"]]

