# Crisp Interview Project


## Objective:

To develope and deploy a simple http service that will permit users to upload a file and report back a word count. 


## Residual questions after reading instruction:

As the instruction stated, the service should provide "interfaces for ingesting files, and for receiving counts". 

This implies that these two actions aren't meant to be tied together, i.e. user will issue 2 calls to achieve said action - one to upload the file, and another call to retrieve word count, instead of just one call that completes the upload then responds back immediately with the word count. 

Can this service be implemented with just one interface that permits user to upload the file and immediately be fed back with a http response that contains the word count?  I'm asking this because...
 
 * The 2-step process of uploading file then query for word count will require that the query request be submitted with a file name. 
 * Given the stateless nature of http service, the query request will require that the service record, post file ingestion, the filename and the cooresponding word count in a rudimentary database or separate text file.
 * This need for wordcount database adds unnecessary complexity in programming and deployment of this service, when the point of this project is to gauage in a quick manner a devop candidate's ability to do infrastructure as code. 


## Assumptions taken when working on this project:

 * Scope does not include setting up a complete serving infrastructure (e.g. VPC/Subnet definition/Load balancers/Containerization Orchestration cluster)
 * Scope does not include implementation of a full CI/CD infrastructure (e.g. Jenkins)
 * Scope does not include setting up a monitoring infrastructure
 * Scaling of this service will be manual and not automated
 * Application security and encryption (in-transit or at rest), are not a concern. Plain http call is fine, no need for SSL termination, certificate generation, etc. 
 * Given the question posed above, deliverable will be a http service with just one interface that permits a POST request to upload file and the interface will respond back immediately the word count - combining 2 steps into 1 step to retrieve word count of file.
 * Given that the service iteself is not the focus of this exercise, I do not have integration or unit tests at the moment for the service itself.


## Approach:

 * Given that code can be deployed in multiple ways, I have decided to deploy code inside a docker container. 
 * This docker container will deploy as a kubernetes service, runnable by a minikube installation.


## Other possible approaches to deployment (And this is an engineering wide decision with tech and human resource issues to consider):

 * Deploy code on bare cloud instances (not containerized) Deployments in this case can be
   * Using ansible playbook, or ssh commands, to copy/run code onto destination cloud instance via git clone, tarball, or debian/yum packages.
   * Bake brand new virtual machine images with new version of code and refresh entire serving fleet for deployment.
 * Using Google Cloud functions/AWS Lambda, where deployment will be a simple gcp or aws call. This can either be bare code or containerized
 * Using docker-compose and docker-swarm, basically docker API calls to deploy containers on destination cloud instances.
 * Using mesos-marathon or any other containerization engine to run containers on destination cloud instances


## Build instructions

To build the docker container:

```bash

    cd gocrisp
    docker build -t gcr.io/gocrisp/gocrisp-wordcount:$(git rev-parse --short HEAD) ./

```


## Run instructions

To run the container locally on one's machine:

```bash

    docker run -p 5000:5000 gcr.io/gocrisp/gocrisp-wordcount:$(git rev-parse --short HEAD)

```


## Deploy application to Kubernetes cluster 

This instruction should be applicable on either minikube cluster or GKE cluster. For the latter one must first upload the docker image to the GKE container repo:

```bash

    gcloud auth login
    gcloud auth configure-docker
    docker tag gcr.io/gocrisp/gocrisp-wordcount:$(git rev-parse --short HEAD) gcr.io/gocrisp/gocrisp-wordcount:latest
    docker push -a gcr.io/gocrisp/gocrisp-wordcount  # this should push both tags

```

Now assuming your `kubectl` is configured to talk to the correct cluster, run the following command to create a deployment, then map the service to the deployment. 


```bash
    kubectl apply -f k8syml/wordcount-deployment.yml
    kubectl rollout status deployment/wordcount-deployment  # should show that a deployment is ongoing and spinning up 2 containers 
    kubectl apply -f k8syml/wordcount-service.yml
    kubectl get services                                    # should retrieve a service named wordcount-service
```

The type of service this creates is NodePort service, which maps to k8s cluster node ports. In a production setup most likely we will need to modify the service to type `loadbalancer` to have it automatically provision a cloud provider load balancer, or define an ingress resource in the kubernetes cluster.

When running this on minikube, you'll now need find the url that'll allow you to access this service.

```bash
    minikube service wordcount-service --url
```


