""" S3 Service """

import logging
import boto3 as aws

s3_resource = aws.resource("s3")
s3_client = aws.client("s3")
logging.basicConfig(format="%(asctime)s | S3: %(message)s")


def create_bucket(bucket_name, bucket_region):
    """
    Creates a bucket in the S3 service specified region

    Args:
        bucket_name (srt): Name given to the bucket
        bucket_region (srt): Region where the bucket should be created
    """
    bucket = s3_resource.Bucket(bucket_name)

    if bucket_exists(bucket):
        logging.warning(f"Bucket {bucket_name} already exists")
        delete_bucket(bucket)
        logging.warning(f"Bucket {bucket_name} deleted")

    try:
        bucket = s3_resource.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": bucket_region},
        )
        logging.warning(f"Bucket {bucket_name} created")

    except Exception as err:
        logging.exception(f"Create bucket exception: {err}")

    return bucket


def bucket_exists(bucket):
    """
    Check if the given bucket exists

    Args:
        bucket (obj): Boto3 bucket object
    """
    if bucket.creation_date is not None:
        return True
    return False


def get_bucket(bucket_name):
    buckets = s3_client.list_buckets()["Buckets"]
    bucket = [bucket for bucket in buckets if bucket["Name"] == bucket_name]
    return bucket[0] if bucket else None


def delete_bucket(bucket):
    """
    Delete a given bucket

    Args:
        bucket (obj): Boto3 bucket object
    """
    try:
        bucket.delete()

    except Exception as err:
        logging.exception(f"Delete bucket exception: {err}")


def list_all_objects(bucket_name):
    """
    List all objects within a given bucket

    Args:
        bucket_name (str): Name of the bucket
    """
    try:
        pages = s3_client.get_paginator("list_objects").paginate(Bucket=bucket_name)

    except Exception as err:
        logging.exception(f"List S3 objects exception: {err}")

    objects = [file["Key"] for page in pages for file in page["Contents"]]
    return objects


def list_objects(bucket_name, prefix=""):
    """
    List all objects within a given bucket with a certain prefix

    Args:
        bucket_name (str): Name of the bucket
        prefix (str): prefix of file names
    """
    objects = s3_client.list_objects(Bucket=bucket_name, Prefix=prefix)
    files = [file["Key"] for file in objects["Contents"]]
    return files
