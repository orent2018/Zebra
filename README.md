# AWS S3 python web service and deployment (docker,kubernetes,helm)
# -----------------------------------------------------------------

Flask web framework and boto3 sdk were used to create a web service that accepts three
parameters in the url:

     1) Source file name - file to be uploaded to S3

     2) Bucket name - name of the bucket to which the file should be uploaded

     3) region - region were the bucket resides

In order to connect to an AWS account it is assumed that we have the following credentials:

    - AWS_ACCESS_KEY_ID
   
    - AWS_SECRET_ACCESS_KEY

   The use will be described below either as env variables to a container or as kubernetes secrets

Usage:

    The web service is accessible as follows:

    http://{external-IP}:{NodePort}/s3_copy?filename=<file-name>&bucket=<bucket name>&region=<AWS region>

    The external-IP and NodePort are defined in the kubernetes service or values.yaml file in helm

    The file must be accessible under the workdir defined in the Dockerfile the in a directory named large_files
    (this can also be paramatrized and defined externally)

    The web service expects to receive an exisiting and accessible filename and bucket and does NOT
    implement Error handling to respond when such conditions are not met.


It includes a test message to verify access:

    http://{external-IP}:{NodePort}
   
 and a boto3 fast copy function which performs a copy of large files by breaking the copy operation to threads.

The copy rate was found to be about 10 seconds per 1 GB.


Dockerizing
-----------

A Docker file was created to add prerequisites and run the python web app in a container.  The docker imgage
was created using:

     docker build -t zebra-test .

The container can be run with -p (port mapping) -v (volume mounting) and -e (passsing parameters - env vars) as follows:


     docker run -it -p 5000:5000 -v ~orent66/work/zebra/:/zebra/devops-task/ -e AWS_ACCESS_KEY_ID=###### -e AWS_SECRET_ACCESS_KEY -it zebra-test


This is an insecure way to pass the credentials to the docker container.

The workdir env variable defined in the Dockerfile must match the mountPath in the deployment.yaml (or values.yaml in helm)


Kubernetes
----------

The service was tested on a 2 node kubernetes cluster.  The manifests are found under k8-zebra dir

The deployment and NodePort service was applied as follows:

    kubectl apply -f deployment.yaml
    kubectl apply -f service-zebra.yaml

( A name space was also created using:  kubectl apply -f ns-zebra-aws.yaml )


   The manifests include:

   1) Volume mounts for the directory where source file are located so they are available to the pod


   2) Secrets were created for the 2 AWS credentials as follows:

         kubectl create secret generic access-key --from-literal=accessKeyId='########'

         kubectl create secret generic secret-access --from-literal=secretAccessKey='#####'


   3) An external IP that the service exposes for access to the service.


Helm Chart and package
---------------------

A helm chart called zebra-chart was created as follows:


      helm create zebra-chart 


The deployment.yaml and service yaml were taken from the kubernetes installation and were converted into
templates with the actuall parameters stored in values.yaml

The chart was validated using:


      helm lint zebra-chart


The chart was installed using:


      helm install zebra-chart zebra-chart/


The chart was then packaged using:


      helm package zebra-chart

---------------------------------------------------------
