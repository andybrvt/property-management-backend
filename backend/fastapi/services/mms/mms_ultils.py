import requests
import logging
from backend.fastapi.utils.s3 import upload_file_to_s3

logger = logging.getLogger(__name__)

def save_twilio_image_to_s3(media_url: str, filename: str) -> str:
    """
    Downloads an image from Twilio's URL and uploads it to S3.

    Parameters:
    - media_url (str): The Twilio-provided URL of the MMS image.
    - filename (str): The filename to store in S3.

    Returns:
    - str: The uploaded S3 URL or None if failed.
    """
    try:
        logger.info(f"📥 Downloading image from Twilio: {media_url}")

        # 📥 Download the image from Twilio
        response = requests.get(media_url, stream=True)
        response.raise_for_status()
        file_content = response.content  # Get image bytes

        # 📤 Upload to S3
        s3_url = upload_file_to_s3(file_content, filename)

        if s3_url:
            logger.info(f"✅ Successfully uploaded to S3: {s3_url}")
            return s3_url
        else:
            logger.error(f"❌ Failed to upload image to S3.")
            return None

    except Exception as e:
        logger.error(f"❌ Error downloading/uploading MMS: {e}")
        return None