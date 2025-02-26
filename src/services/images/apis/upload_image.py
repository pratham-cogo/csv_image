import requests, logging
from configs.env import FREEIMAGE_API_KEY, FREEIMAGE_UPLOAD_URL

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def upload_image(image_url):
    try:
        response = requests.post(
            FREEIMAGE_UPLOAD_URL,
            data={"key": FREEIMAGE_API_KEY, "action": "upload", "source": image_url, "format": "json"},
        )
        response.raise_for_status()
        return response.json()["image"]["url"]
    except Exception as e:
        logger.warning(f"Failed to upload image: {str(e)}")
        return None