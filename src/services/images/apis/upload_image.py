import requests
import base64
import logging
from configs.env import FREEIMAGE_API_KEY, FREEIMAGE_UPLOAD_URL
from io import BytesIO
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def upload_image(image_buffer: BytesIO) -> Optional[str]:
    try:
        image_base64 = base64.b64encode(image_buffer.getvalue()).decode("utf-8")
        response = requests.post(
            FREEIMAGE_UPLOAD_URL,
            data={
                "key": FREEIMAGE_API_KEY,
                "action": "upload",
                "source": image_base64,
                "format": "json"
            },
        )
        response.raise_for_status()

        json_response = response.json()
        if json_response["status_code"] == 200:
            return json_response["image"]["url"]
        else:
            logger.warning(f"Failed to upload image: {json_response.get('status_txt')}")
            return None

    except Exception as e:
        logger.warning(f"Failed to upload image: {str(e)}")
        return None
