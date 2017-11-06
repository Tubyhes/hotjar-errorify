import sys, os, json, time
sys.path.append(os.path.abspath(os.path.join('..', 'api')))

import main
import unittest
from elasticsearch import Elasticsearch

class ApiTestCase (unittest.TestCase):

	def setUp(self):
		main.app.testing = True
		self.app = main.app.test_client()
		self.es = Elasticsearch()
		create_index_body = {
			"mappings": {
				"javascript": {
					"_routing": {
						"required": True
					},
					"properties": {
						"_tracker_id": { 
							"type": "string"
						}
					}
				}
			}
		}

		res = self.es.indices.create(index="error_logs", body=create_index_body)


	def test_providing_headers (self):
		# forgot to add content-type header
		rv = self.app.post("/data", data = json.dumps({"herp": "derp"}), headers = [("x-tracker_id", "1234567890")])
		assert rv.status_code == 400
		
		# forgot to add tracker_id
		rv = self.app.post("/data", data = json.dumps({"herp": "derp"}), content_type = "application/json")
		assert rv.status_code == 400

		# provided non-existing tracker id
		rv = self.app.post("/data", headers = [("x-tracker_id", "4563452757")])
		assert rv.status_code == 401

		# forgot to add session_id in get
		rv = self.app.get("/data", headers = [("x-tracker_id", "1234567890")])
		assert rv.status_code == 401

		# provide unauthorized session - tracker combo
		rv = self.app.get("/data", headers = [("x-tracker_id", "1234567890"), ("x-session_id", "qwerty")])
		assert rv.status_code == 403


	def test_post_get_data (self):
		# sending empty document (will not get stored!)
		rv = self.app.post("/data", data = json.dumps({}), content_type = "application/json", headers = [("x-tracker_id", "1234567890")])
		assert rv.status_code == 400

		# standard successful case
		rv = self.app.post("/data", data = json.dumps({"herp": "derp"}), content_type = "application/json", headers = [("x-tracker_id", "1234567890")])
		assert rv.status_code == 201

		# retrieve the data point that we just stored
		rv = self.app.get("/data", headers = [("x-tracker_id", "1234567890"), ("x-session_id", "abcdef")])
		assert rv.status_code == 200
		assert len(json.loads(rv.data)) == 1

		# retrieve data from a different tracker that has no data yet
		rv = self.app.get("/data", headers = [("x-tracker_id", "2345678901"), ("x-session_id", "abcdef")])
		assert rv.status_code == 200
		assert len(json.loads(rv.data)) == 0


	def test_lots_of_data_paging (self):
		# insert a large number of datapoints
		total = 100
		for x in range(total):
		 	rv = self.app.post("/data", data = json.dumps({"herp": "derp", "line_nr": x}), content_type = "application/json", headers = [("x-tracker_id", "1234567890")])
		 	assert rv.status_code == 201

		# retrieve all datapoints
		rv = self.app.get("/data", headers = [("x-tracker_id", "1234567890"),  ("x-session_id", "abcdef")])
		assert rv.status_code == 200
		d = json.loads(rv.data)
		print len(d)
		assert len(d) == total

		# retrieve first 10 datapoints
		rv = self.app.get("/data?from=0&size=10", headers = [("x-tracker_id", "1234567890"),  ("x-session_id", "abcdef")])
		assert rv.status_code == 200
		d = json.loads(rv.data)
		assert len(d) == 10
		assert d[0]["line_nr"] == total - 1

		# retrieve second 10 datapoints
		rv = self.app.get("/data?from=10&size=10", headers = [("x-tracker_id", "1234567890"),  ("x-session_id", "abcdef")])
		assert rv.status_code == 200
		d = json.loads(rv.data)
		assert len(d) == 10
		assert d[0]["line_nr"] == total - 11


	def test_searching_data (self):
		# insert some data that we can search for
		for x in range (10):
			rv = self.app.post("/data", data = json.dumps({"herp": "derp", "line_nr": x%2+1}), content_type = "application/json", headers = [("x-tracker_id", "1234567890")])
			assert rv.status_code == 201

		for x in range (10):
			rv = self.app.post("/data", data = json.dumps({"herp": "derp", "line_nr": x%2+3}), content_type = "application/json", headers = [("x-tracker_id", "2345678901")])
			assert rv.status_code == 201

		for x in range (10):
			rv = self.app.post("/data", data = json.dumps({"herp": "derp", "line_nr": x%2+1}), content_type = "application/json", headers = [("x-tracker_id", "0987654321")])
			assert rv.status_code == 201

		# search for errors in line 2 for tracker_id 1234567890
		rv = self.app.get("/search", content_type = "application/json", data=json.dumps({"query": {"match": {"line_nr": 2}}}), headers = [("x-tracker_id", "1234567890"),  ("x-session_id", "abcdef")])
		assert rv.status_code == 200
		d = json.loads(rv.data)
		r = [x["_source"] for x in d["hits"]["hits"]]
		assert len(r) == 5

		# search for errors in line 2 for tracker_id 2345678901
		rv = self.app.get("/search", content_type = "application/json", data=json.dumps({"query": {"match": {"line_nr": 2}}}), headers = [("x-tracker_id", "2345678901"),  ("x-session_id", "abcdef")])
		assert rv.status_code == 200
		d = json.loads(rv.data)
		r = [x["_source"] for x in d["hits"]["hits"]]
		assert len(r) == 0

		# return top 10 lines with errors for tracker_id 0987654321
		rv = self.app.get("/search", content_type = "application/json", data=json.dumps({"size": 0, "aggs": {"group_by_line": {"terms": {"field": "line_nr"}}}}), headers = [("x-tracker_id", "0987654321"),  ("x-session_id", "qwerty")])
		assert rv.status_code == 200
		d = json.loads(rv.data)
		print d
		print rv.data


	def tearDown(self):
		self.es.indices.delete("error_logs")

if  __name__ == '__main__':
	unittest.main()
