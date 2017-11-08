# hotjar-errorify

Service for storing and retrieving Javascript error logs. Uses the following stack:

* nginx
* uwsgi
* python flask api
* elasticsearch database

Deployment of nginx-uwsgi-api is done using Kubernetes and Docker. Deployment of ElasticSearch cluster is not covered in this repo, though a local install will do the trick.

## Installs

Install the following software:

### Kubernetes / minikube

Follow the instructions [here](https://kubernetes.io/docs/getting-started-guides/minikube/)

### ElasticSearch

Follow the instructions [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html)

After you got ElasticSearch running, make sure your local cluster is accessible from the outside. In `/etc/elasticsearch/elasticsearch.yml` add lines:

```
network.host: 0.0.0.0
network.post: 9200
```

and restart elasticsearch.

### Errorify

Clone the [repo](https://github.com/Tubyhes/hotjar-errorify)

## Running Unittests

You are advised to use a virtualenv to manage the python dependencies. In your virtualenv, install the dependencies:

```
pip install -r requirements
```

You should now be able to run the Unit tests:
```
cd tests
python api_tests.py
```

The unit tests will create and delete the required ElasticSearch index before and after every test.

## Running Locally

With the virtualenv active, configure the required ElasticSeach index by running administration/configure_elasticsearch.py:

```
cd adminstration
python configure_elasticsearch.py
```

Then in the api folder, run the api:

```
cd api
python
>>>import main
>>>main.app.run()
```

You can now make API calls to the api locally on `localhost:5000`

## Deploying on Kubernetes

First step is to build the Docker image, using docker from Minikube:

```
eval $(minikube docker-env)
docker build -t errorify:v1 .
```

Then, with the docker image built, start a new Kubernetes deployment:
```
kubectl run errorify-node --image=errorify:v1 --port=80
```

If the pods are successfully running, expose the service:
```
kubectl expose deployment errorify-node --type=LoadBalancer
```

Obtain the address from minikube:
```
minikube service errorify-node
```

You can now make API calls to this address. The API is configured to use the local ElasticSearch install, so make sure the required index is already configured (see above).
If you have a dedicated ElasticSearch cluster you want the API to talk to, update the kubernetes_settings.py file to contain the ElasticSearch ip addresses before you build the docker image. 