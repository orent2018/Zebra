#!/usr/bin/python
# **********************************************
#
#  name:       aws_s3_service.py  
#
#  purpose:    The service expects to recieve a web service call with a file name and the bucket
#              in AWS to which it should be copied. The boto3 python package will handle the process
#              of copying the file in threads in order to shorten the time to completed the task.
#
#  tools:      This service uses the Flask framework and boto3 package to work with AWS S3 resources.
#
#  parameters: The webservice requires AWS user credentials and received as in put
#              in the call a source file name, an AWS bucket name and an AWS region.
#
#  Output:     
#              
#
#  Created: 21/08/2020
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
from botocore.exceptions import NoCredentialsError

def FastUploadToS3(filename,bucket):
    s3_client = boto3.client('s3')
    config = TransferConfig(multipart_threshold=1024*25, max_concurrency=10,
                        multipart_chunksize=1024*25, use_threads=True)
#    file_path = base_dir + filename
    file_path = os.getenv('workdir')+ '/' + filename
#    file_path = os.path.dirname(__file__)+ '/' + filename
    keypath = 'large_files/'+filename
    s3_client.upload_file(file_path, bucket, keypath,Config = config)
#    s3_client.upload_file(file_path, bucket, keypath,ExtraArgs={ 'ACL': 'public-read'},Config = config)
#    ExtraArgs={ 'ACL': 'public-read'},
#    Config = config
#    Callback=ProgressPercentage(filename)

def UploadToS3(local_file, bucket, s3_file):
    #    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
        s3 = boto3.client('s3')
    
        try:
            s3.upload_file(local_file, bucket, s3_file)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False

app = flask.Flask(__name__)

@app.route('/')
def api_root():
    return 'Welcome'

#@app.route('/s3_copy', methods=['POST','GET'])
@app.route('/s3_copy')
def my_route():
    filename = request.args.get('filename', default = 'X', type = str)
    bucket = request.args.get('bucket', default = 'X', type = str)
    region = request.args.get('region', default = 'X', type = str)
    
#   Need to update region is .aws/config
    FastUploadToS3(filename,bucket)
#    UploadToS3(filename,bucket,filename)

    return 'filename:'+filename+'bucket_name:'+bucket+'region:'+region



if __name__ == '__main__':
#  app.run(host='0.0.0.0', port=80)
  app.run(host='0.0.0.0')
