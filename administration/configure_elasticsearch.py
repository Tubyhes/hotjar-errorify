from elasticsearch import Elasticsearch

es = Elasticsearch()

res = es.indices.create(index="error_logs", body={"mappings": {"javascript": {"_routing": {"required": True}}}})

print res