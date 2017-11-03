
from flask import Flask, request, g, make_response
from flask.json import jsonify
from services.db_elasticsearch import DBElasticsearch
from services.auth_stub import AuthStub
import time

app = Flask(__name__)

def get_auth():
	if not hasattr(g, "auth"):
		g.auth = AuthStub()
	return g.auth

def get_db():
	if not hasattr(g, "db"):
		g.db = connect_db()
	return g.db 

def connect_db():
	return DBElasticsearch("error_logs", "javascript")


@app.route("/")
def hello():
	return "Hello World"


@app.route ("/data", methods=['GET'])
def get_data ():

	# get tracker id from request header, or bad request 
	tracker_id = request.headers.get("x-tracker_id")
	if tracker_id is None:
		return make_response(("No tracker id provided!", 400, []))

	# get session id from request header, or unauthorized
	session_id = request.headers.get("x-session_id")
	if session_id is None:
		return make_response(("No session id provided!", 401, []))

	# verify this session id has access to this tracker id
	if not get_auth().authorized(tracker_id, session_id):
		return make_response(("Unauthorized!", 403, []))

	# obtain the from and size request parameters, or use default values
	from_ = request.args.get("from", 0)
	size = request.args.get("size", 1000)

	# if we get here, retrieve and return the data from the database
	v = get_db().retrieve(tracker_id, from_, size)
	return jsonify(v)


@app.route ("/data", methods=['POST'])
def store_data ():

	# get tracker id from request header, or bad request 
	tracker_id = request.headers.get("x-tracker_id")
	if tracker_id is None:
		return make_response(("No tracker id provided!", 400, []))

	# get the data from the request payload, or bad request
	data = request.get_json()
	if data is None:
		return make_response(("No data provided!", 400, []))
	if not data:
		return make_response(("Empty data provided!", 400, []))

	# add the tracker id and timestamp to the data
	data["_tracker_id"] = tracker_id
	data["_time"] = int(time.time() * 1000)

	# store data in database, return success
	get_db().store(tracker_id, data)
	return make_response(("Stored!", 201, []))


if (__name__) == "__main__":
	app.run()


