import boto3
import datetime
import uuid

from mypy_boto3_s3 import S3ServiceResource

class ImageServiceS3():
    s3_client: S3ServiceResource

    def __init__(self, s3_client):
        self.s3_client = s3_client

    def generate_pre_signed_url(self):
        object_key: str = f"{uuid.uuid1()} - {datetime.datetime.now()}"
        res = self.s3_client.meta.client.generate_presigned_post(Key=object_key, Bucket='photosharingapp-images')
        return res


s3 = boto3.resource(service_name='s3', region_name='us-east-2')
image_services3 = ImageServiceS3(s3_client=s3)
