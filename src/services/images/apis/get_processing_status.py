from fastapi import HTTPException, status
from services.images.models.processed_images import ProcessedImages
from services.images.apis.upload_image import upload_image
import logging, uuid

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_processing_status(request_id: str, user_id: str):
    try:
        image_request: ProcessedImages = ProcessedImages.get_or_none(request_id=uuid.UUID(request_id), user_id=uuid.UUID(user_id))
        if not image_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
        return {
            "status": image_request.status,
            "processed_count": image_request.processed_count,
        }
    except:
        logger.warning(f"Error while fetching processing status for request_id: {request_id}")
        raise