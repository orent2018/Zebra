#!/usr/bin/python
# **********************************************
#
#  name:       aws_s3_service.py  

#  purpose:    The service expects to recieve a web service call with a file name and the bucket
#              in AWS to which it should be copied. The boto3 python package will handle the process
#              of copying the file in threads in order to shorten the time to completed the task.
#
#  tools:      This service uses the Flask framework and boto3 package to work with AWS S3 resources.
#
#  parameters: The webservice requires AWS user credentials which will be supplied to the docker container externally
#              either as env variables or more securly through kubernetes secrets
#              The input for the call a source is file name, an AWS bucket name and an AWS region.
#
#  assumptions: Currently there is no error handling so that the service relies on an existing file name found in 
#               a directory supplied by an external variable workdir, a valid bucket name that is reachable with the
#               supplied AWS credentials. The region provided is not directly used but is stored as an env variable
#  Output:     
#              
#
#  Created: 24/08/2020
#
#  Maintainer: Oren Teomi
#
# **********************************************

import os
import sys
import flask
from flask import request
import threading 
import boto3
from boto3.s3.transfer import TransferConfig

# Fast copy function to AWS with multiple threads
# -----------------------------------------------
def FastUploadToS3(filename,bucket,region):
    s3_client = boto3.client('s3')
    config = TransferConfig(multipart_threshold=1024*25, max_concurrency=10,
                        multipart_chunksize=1024*25, use_threads=True)

#   Make sure workdir has been (externally) defined or exit - For TESTING in a non dockerized settings as it is defined in the Dockerfile
#   -------------------------------------------------------
    if "workdir" in os.environ:
      file_path = os.getenv('workdir')+ '/' + filename
    else:
      print("File Directory: workdir is not defined - S3 Copy Cancelled!")
      return 'Exit'
    keypath = 'large_files/'+filename

#   After variables defined call the boto3 copy function to perform the operation
#   -----------------------------------------------------------------------------
    s3_client.upload_file(file_path, bucket, keypath,Config = config)

#   End Fast S3 Copy function

app = flask.Flask(__name__)

# Test message to check connectivity to the web service
# -----------------------------------------------------
@app.route('/')
def api_root():
    return 'Welcome Test\n'

# Main function of accepting the 3 parameters (filename,bucket,region) and invoking the fast parallel copy function
# -----------------------------------------------------------------------------------------------------------------
@app.route('/s3_copy')
def my_route():
    filename = request.args.get('filename', default = 'X', type = str)
    bucket = request.args.get('bucket', default = 'X', type = str)
    region = request.args.get('region', default = 'us-east-1', type = str)
    
#   Update the AWS region env variable based on the provided region input
    os.environ["AWS_DEFAULT_REGION"]=region

#   Invoke the fast copy function
    FastUploadToS3(filename,bucket,region)

    return 'Copied file: '+filename+' to AWS bucket: '+bucket+' in region: '+region+'\n'


if __name__ == '__main__':
  app.run(host='0.0.0.0')
