import logging
import boto3
import json
from io import BytesIO
from fastapi import HTTPException
from botocore.config import Config

from app.core.config import env_var

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        try:
            required_fields = [
                env_var.DO_SPACES_ENDPOINT,
                env_var.DO_SPACES_REGION,
                env_var.DO_SPACES_KEY,
                env_var.DO_SPACES_SECRET,
                env_var.DO_SPACES_BUCKET,
            ]
            if not all(required_fields):
                raise ValueError("Missing required DigitalOcean Spaces environment variables.")

            self.s3_client = boto3.client(
                "s3",
                endpoint_url=env_var.DO_SPACES_ENDPOINT,
                region_name=env_var.DO_SPACES_REGION,
                aws_access_key_id=env_var.DO_SPACES_KEY,
                aws_secret_access_key=env_var.DO_SPACES_SECRET,
                config=Config(retries={'max_attempts': 3}),
            )

            self.bucket_name = env_var.DO_SPACES_BUCKET
            self.base_url = env_var.DO_SPACES_CDN_URL or f"https://{self.bucket_name}.{env_var.DO_SPACES_REGION}.digitaloceanspaces.com"

        except Exception as e:
            logger.error(f"Failed to initialize S3Service: {str(e)}")
            raise

    def upload_json_data(self, data: dict, filename: str = "data.json", folder: str = "cdn") -> str:
        """
        Upload a Python dictionary as a JSON file to DigitalOcean Spaces.

        Args:
            data: Dictionary to upload
            filename: Name of the file (e.g., latest.json)
            folder: Folder path in the bucket (e.g., cdn, currency)

        Returns:
            Full URL of the uploaded object
        """
        try:
            object_key = f"{env_var.ENV_STATE}/{folder}/{filename}"
            file_bytes = json.dumps(data, indent=2).encode("utf-8")

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=BytesIO(file_bytes),
                ContentType="application/json",
            )

            file_url = f"{self.base_url}/{object_key}"
            logger.info(f"JSON uploaded to: {file_url}")
            return file_url

        except Exception as e:
            logger.error(f"Error uploading JSON to S3: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to upload JSON file to CDN")
