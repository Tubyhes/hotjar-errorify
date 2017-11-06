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
		if not self.exists_filter_alias(tracker_id):
			return []

		res = self.es.search (	index = tracker_id,
								doc_type = self.type_name,
								routing = tracker_id, 
								from_ = from_,
								size = size,
								sort = "_time:desc",
								body = {"query": {"match_all": {}}})

		return [x["_source"] for x in res["hits"]["hits"]]

	def put_filter_alias (self, tracker_id):
		res = self.es.indices.put_alias (	index = self.index_name,
											name = tracker_id,
											body = {"routing": tracker_id, "filter": {"term": {"_tracker_id": tracker_id}}})

	def exists_filter_alias (self, tracker_id):
		res = self.es.indices.exists_alias (index = self.index_name,
											name = tracker_id)
		return res

	def search (self, tracker_id, query):
		if not self.exists_filter_alias(tracker_id):
			return []

		res = self.es.search ( 	index = tracker_id,
								doc_type = self.type_name,
								routing = tracker_id,
								body = query)
		res.pop("_shards", None)
		res.pop("took", None)
		res.pop("timed_out", None)
		return res



