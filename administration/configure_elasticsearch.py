from elasticsearch import Elasticsearch

es = Elasticsearch()

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

res = es.indices.create(index="error_logs", body=create_index_body)

print res