import os
import logging

import boto3

from botocore.exceptions import ClientError

from core.config import (
    S3_ENDPOINT_URL,
    S3_ACCESS_KEY_ID,
    S3_SECRET_ACCESS_KEY,
    S3_BUCKET_NAME,
    S3_SESSION_KEY,
    S3_REGION,
    LOCAL_SESSION_PATH,
)

logger = logging.getLogger(__name__)


class S3SessionManager:
    def __init__(self):
        self.s3_client = None
        self._initialized = False

    def initialize(self):
        """Initialize S3 client"""
        if not all([S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, S3_BUCKET_NAME]):
            logger.warning("S3 credentials not provided, using local session storage")
            return False

        try:
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=S3_ENDPOINT_URL,
                aws_access_key_id=S3_ACCESS_KEY_ID,
                aws_secret_access_key=S3_SECRET_ACCESS_KEY,
                region_name=S3_REGION,
            )

            self.s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
            self._initialized = True
            logger.info("S3 session manager initialized successfully")
            return True

        except ClientError as e:
            logger.error(f"S3 initialization failed: {e}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error during S3 initialization: {e}")
            return False

    async def download_session(self) -> bool:
        """Download session file from S3"""
        if not self._initialized:
            logger.warning("S3 not initialized, using local session")
            return False

        try:
            os.makedirs(os.path.dirname(LOCAL_SESSION_PATH), exist_ok=True)

            self.s3_client.download_file(
                S3_BUCKET_NAME, S3_SESSION_KEY, LOCAL_SESSION_PATH
            )
            logger.info(f"Session downloaded from S3: {S3_SESSION_KEY}")
            return True

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                logger.info("Session file not found in S3, will create new one")
            else:
                logger.error(f"Error downloading session from S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading session: {e}")
            return False

    async def upload_session(self) -> bool:
        """Upload session file to S3"""
        if not self._initialized:
            logger.warning("S3 not initialized, session will be stored locally only")
            return False

        if not os.path.exists(LOCAL_SESSION_PATH):
            logger.warning("Local session file not found, nothing to upload")
            return False

        try:
            self.s3_client.upload_file(
                LOCAL_SESSION_PATH, S3_BUCKET_NAME, S3_SESSION_KEY
            )
            logger.info(f"Session uploaded to S3: {S3_SESSION_KEY}")
            return True

        except Exception as e:
            logger.error(f"Error uploading session to S3: {e}")
            return False

    def get_session_path(self) -> str:
        """Get local session file path"""
        return LOCAL_SESSION_PATH

    async def cleanup_local_session(self):
        """Remove local session file (for security)"""
        try:
            if os.path.exists(LOCAL_SESSION_PATH):
                os.remove(LOCAL_SESSION_PATH)
                logger.info("Local session file cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up local session: {e}")


s3_manager = S3SessionManager()
