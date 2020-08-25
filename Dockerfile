FROM python:2-slim

RUN pip install flask && pip install boto3   

COPY aws_s3_webservice.py /app/aws_s3_webservice.py

EXPOSE 5000

VOLUME /zebra/devops/

WORKDIR /zebra/devops-task/

ENV workdir /zebra/devops-task/

CMD ["python","/app/aws_s3_webservice.py"]
